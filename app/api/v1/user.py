import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.role import SysUserRole
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()
logger = logging.getLogger("app.user")


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    """非超级管理员只能操作自己租户的数据"""
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


def _op(u: SysUser) -> str:
    """格式化操作人信息"""
    return f"{u.username}(id={u.id},tenant={u.tenant_id})"


@router.get("/list")
async def list_users(
    page: int = 1,
    page_size: int = 10,
    username: str | None = None,
    tenant_id: str | None = None,
    status: int | None = None,
    dept_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysUser).where(SysUser.deleted == 0)

    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysUser.tenant_id == tenant_id)
    elif current_user.user_type == 1:
        q = q.where(SysUser.tenant_id == current_user.tenant_id)
        q = q.where(SysUser.user_type != 0)
    else:
        q = q.where(SysUser.id == current_user.id)

    if username:
        q = q.where(SysUser.username.like(f"%{username}%"))
    if status is not None:
        q = q.where(SysUser.status == status)
    if dept_id is not None:
        q = q.where(SysUser.dept_id == dept_id)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysUser.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [UserOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user.user_type != 0 and user.user_type == 0:
        raise HTTPException(status_code=403, detail="权限不足")
    if current_user.user_type == 2 and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    _check_tenant(current_user, user.tenant_id)
    return success(UserOut.model_validate(user))


@router.post("/create")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    _check_tenant(current_user, data.tenant_id)
    existing = (await db.execute(
        select(SysUser).where(SysUser.username == data.username, SysUser.tenant_id == data.tenant_id, SysUser.deleted == 0)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="用户名在该租户下已存在")

    role_ids = data.role_ids
    user_data = data.model_dump(exclude={"role_ids"})
    user_data["password"] = get_password_hash(user_data["password"])
    user = SysUser(**user_data)
    db.add(user)
    await db.flush()

    for rid in role_ids:
        db.add(SysUserRole(user_id=user.id, role_id=rid))

    await db.commit()
    await db.refresh(user)
    logger.info(
        "[USER] create  operator=%s -> new_user=%s(id=%d) tenant=%s",
        _op(current_user), user.username, user.id, user.tenant_id,
    )
    return success(UserOut.model_validate(user))


@router.put("/update/{id}")
async def update_user(
    id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user.user_type != 0 and user.user_type == 0:
        raise HTTPException(status_code=403, detail="权限不足")

    if current_user.user_type == 2:
        if user.id != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        allowed = {k: v for k, v in data.model_dump(exclude_none=True).items()
                   if k in ("real_name", "email", "phone", "avatar")}
        for k, v in allowed.items():
            setattr(user, k, v)
        await db.commit()
        await db.refresh(user)
        logger.info("[USER] update(self)  operator=%s fields=%s", _op(current_user), list(allowed.keys()))
        return success(UserOut.model_validate(user))

    _check_tenant(current_user, user.tenant_id)
    role_ids = data.role_ids
    for k, v in data.model_dump(exclude_none=True, exclude={"role_ids"}).items():
        setattr(user, k, v)

    if role_ids is not None:
        await db.execute(delete(SysUserRole).where(SysUserRole.user_id == id))
        for rid in role_ids:
            db.add(SysUserRole(user_id=id, role_id=rid))

    await db.commit()
    await db.refresh(user)
    logger.info(
        "[USER] update  operator=%s -> user_id=%d username=%s",
        _op(current_user), user.id, user.username,
    )
    return success(UserOut.model_validate(user))


@router.delete("/delete/{id}")
async def delete_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user.user_type != 0 and user.user_type == 0:
        raise HTTPException(status_code=403, detail="权限不足")
    _check_tenant(current_user, user.tenant_id)
    user.deleted = 1
    await db.commit()
    logger.warning(
        "[USER] delete  operator=%s -> user_id=%d username=%s tenant=%s",
        _op(current_user), user.id, user.username, user.tenant_id,
    )
    return success(msg="删除成功")


@router.get("/roles/{id}")
async def get_user_roles(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if user:
        if current_user.user_type == 2 and user.id != current_user.id:
            raise HTTPException(status_code=403, detail="权限不足")
        _check_tenant(current_user, user.tenant_id)
    result = await db.execute(select(SysUserRole.role_id).where(SysUserRole.user_id == id))
    return success(result.scalars().all())
