import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.role import SysRole, SysRoleMenu
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter()
logger = logging.getLogger("app.role")


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


def _op(u: SysUser) -> str:
    return f"{u.username}(id={u.id},tenant={u.tenant_id})"


@router.get("/list")
async def list_roles(
    page: int = 1,
    page_size: int = 10,
    tenant_id: str | None = None,
    role_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysRole).where(SysRole.deleted == 0)
    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysRole.tenant_id == tenant_id)
    else:
        q = q.where(SysRole.tenant_id == current_user.tenant_id)
    if role_name:
        q = q.where(SysRole.role_name.like(f"%{role_name}%"))
    if status is not None:
        q = q.where(SysRole.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysRole.role_sort, SysRole.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [RoleOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_role(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    _check_tenant(current_user, role.tenant_id)
    menu_ids = (await db.execute(select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == id))).scalars().all()
    data = RoleOut.model_validate(role).model_dump()
    data["menu_ids"] = list(menu_ids)
    return success(data)


@router.post("/create")
async def create_role(data: RoleCreate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(require_admin)):
    _check_tenant(current_user, data.tenant_id)
    menu_ids = data.menu_ids
    role = SysRole(**data.model_dump(exclude={"menu_ids"}))
    db.add(role)
    await db.flush()
    for mid in menu_ids:
        db.add(SysRoleMenu(role_id=role.id, menu_id=mid))
    await db.commit()
    await db.refresh(role)
    logger.info(
        "[ROLE] create  operator=%s -> role_name=%s id=%d tenant=%s menu_ids=%s",
        _op(current_user), role.role_name, role.id, role.tenant_id, menu_ids,
    )
    return success(RoleOut.model_validate(role))


@router.put("/update/{id}")
async def update_role(id: int, data: RoleUpdate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(require_admin)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    _check_tenant(current_user, role.tenant_id)
    menu_ids = data.menu_ids
    for k, v in data.model_dump(exclude_none=True, exclude={"menu_ids"}).items():
        setattr(role, k, v)
    if menu_ids is not None:
        await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == id))
        for mid in menu_ids:
            db.add(SysRoleMenu(role_id=id, menu_id=mid))
    await db.commit()
    await db.refresh(role)
    logger.info(
        "[ROLE] update  operator=%s -> role_id=%d name=%s",
        _op(current_user), role.id, role.role_name,
    )
    return success(RoleOut.model_validate(role))


@router.delete("/delete/{id}")
async def delete_role(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(require_admin)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    _check_tenant(current_user, role.tenant_id)
    role.deleted = 1
    await db.commit()
    logger.warning(
        "[ROLE] delete  operator=%s -> role_id=%d name=%s tenant=%s",
        _op(current_user), role.id, role.role_name, role.tenant_id,
    )
    return success(msg="删除成功")
