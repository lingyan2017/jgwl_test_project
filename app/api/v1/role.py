from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.role import SysRole, SysRoleMenu
from app.schemas.common import success
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter()


@router.get("/list")
async def list_roles(
    page: int = 1,
    page_size: int = 10,
    tenant_id: str | None = None,
    role_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(SysRole).where(SysRole.deleted == 0)
    if tenant_id:
        q = q.where(SysRole.tenant_id == tenant_id)
    if role_name:
        q = q.where(SysRole.role_name.like(f"%{role_name}%"))
    if status is not None:
        q = q.where(SysRole.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysRole.role_sort, SysRole.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [RoleOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_role(id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    menu_ids = (await db.execute(select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == id))).scalars().all()
    data = RoleOut.model_validate(role).model_dump()
    data["menu_ids"] = list(menu_ids)
    return success(data)


@router.post("/create")
async def create_role(data: RoleCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    menu_ids = data.menu_ids
    role = SysRole(**data.model_dump(exclude={"menu_ids"}))
    db.add(role)
    await db.flush()
    for mid in menu_ids:
        db.add(SysRoleMenu(role_id=role.id, menu_id=mid))
    await db.commit()
    await db.refresh(role)
    return success(RoleOut.model_validate(role))


@router.put("/update/{id}")
async def update_role(id: int, data: RoleUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    menu_ids = data.menu_ids
    for k, v in data.model_dump(exclude_none=True, exclude={"menu_ids"}).items():
        setattr(role, k, v)
    if menu_ids is not None:
        await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == id))
        for mid in menu_ids:
            db.add(SysRoleMenu(role_id=id, menu_id=mid))
    await db.commit()
    await db.refresh(role)
    return success(RoleOut.model_validate(role))


@router.delete("/delete/{id}")
async def delete_role(id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    role = (await db.execute(select(SysRole).where(SysRole.id == id, SysRole.deleted == 0))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    role.deleted = 1
    await db.commit()
    return success(msg="删除成功")
