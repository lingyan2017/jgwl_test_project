from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.role import SysUserRole
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    """非超级管理员只能操作自己租户的数据"""
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


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
    # 租户隔离：超级管理员可按 tenant_id 过滤；其他用户只能看自己租户
    if current_user.user_type == 0:
        if tenant_id:
            q = q.where(SysUser.tenant_id == tenant_id)
    else:
        q = q.where(SysUser.tenant_id == current_user.tenant_id)
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
    _check_tenant(current_user, user.tenant_id)
    return success(UserOut.model_validate(user))


@router.post("/create")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
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
    return success(UserOut.model_validate(user))


@router.put("/update/{id}")
async def update_user(id: int, data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
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
    return success(UserOut.model_validate(user))


@router.delete("/delete/{id}")
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    _check_tenant(current_user, user.tenant_id)
    user.deleted = 1
    await db.commit()
    return success(msg="删除成功")


@router.get("/roles/{id}")
async def get_user_roles(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    user = (await db.execute(select(SysUser).where(SysUser.id == id, SysUser.deleted == 0))).scalar_one_or_none()
    if user:
        _check_tenant(current_user, user.tenant_id)
    result = await db.execute(select(SysUserRole.role_id).where(SysUserRole.user_id == id))
    return success(result.scalars().all())
