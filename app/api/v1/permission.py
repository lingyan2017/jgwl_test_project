from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_super_admin
from app.db.session import get_db
from app.models.permission import SysPermission
from app.schemas.common import success
from app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter()


@router.get("/list")
async def list_permissions(
    page: int = 1,
    page_size: int = 10,
    perm_name: str | None = None,
    perm_type: int | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(SysPermission).where(SysPermission.deleted == 0)
    if perm_name:
        q = q.where(SysPermission.perm_name.like(f"%{perm_name}%"))
    if perm_type is not None:
        q = q.where(SysPermission.perm_type == perm_type)
    if status is not None:
        q = q.where(SysPermission.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysPermission.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success({"total": total, "items": [PermissionOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_permission(id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    perm = (await db.execute(select(SysPermission).where(SysPermission.id == id, SysPermission.deleted == 0))).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    return success(PermissionOut.model_validate(perm))


@router.post("/create")
async def create_permission(data: PermissionCreate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    if (await db.execute(select(SysPermission).where(SysPermission.perm_code == data.perm_code))).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="权限编码已存在")
    perm = SysPermission(**data.model_dump())
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return success(PermissionOut.model_validate(perm))


@router.put("/update/{id}")
async def update_permission(id: int, data: PermissionUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    perm = (await db.execute(select(SysPermission).where(SysPermission.id == id, SysPermission.deleted == 0))).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(perm, k, v)
    await db.commit()
    await db.refresh(perm)
    return success(PermissionOut.model_validate(perm))


@router.delete("/delete/{id}")
async def delete_permission(id: int, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    perm = (await db.execute(select(SysPermission).where(SysPermission.id == id, SysPermission.deleted == 0))).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    perm.deleted = 1
    await db.commit()
    return success(msg="删除成功")
