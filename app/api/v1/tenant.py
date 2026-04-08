from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.tenant import SysTenant
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.tenant import TenantCreate, TenantOut, TenantUpdate

router = APIRouter()


def _check_tenant(current_user: SysUser, target_tenant_id: str) -> None:
    if current_user.user_type != 0 and target_tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问其他租户的数据")


@router.get("/list")
async def list_tenants(
    page: int = 1,
    page_size: int = 10,
    tenant_name: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysTenant).where(SysTenant.deleted == 0)
    # 非超级管理员只能看到自己所属的租户
    if current_user.user_type != 0:
        q = q.where(SysTenant.tenant_id == current_user.tenant_id)
    if tenant_name:
        q = q.where(SysTenant.tenant_name.like(f"%{tenant_name}%"))
    if status is not None:
        q = q.where(SysTenant.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (
        await db.execute(q.order_by(SysTenant.id).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return success({"total": total, "items": [TenantOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_tenant(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    tenant = (await db.execute(select(SysTenant).where(SysTenant.id == id, SysTenant.deleted == 0))).scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    _check_tenant(current_user, tenant.tenant_id)
    return success(TenantOut.model_validate(tenant))


@router.post("/create")
async def create_tenant(data: TenantCreate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    if current_user.user_type != 0:
        raise HTTPException(status_code=403, detail="只有超级管理员才能创建租户")
    if (await db.execute(select(SysTenant).where(SysTenant.tenant_id == data.tenant_id))).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="租户ID已存在")
    tenant = SysTenant(**data.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return success(TenantOut.model_validate(tenant))


@router.put("/update/{id}")
async def update_tenant(id: int, data: TenantUpdate, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    tenant = (await db.execute(select(SysTenant).where(SysTenant.id == id, SysTenant.deleted == 0))).scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    _check_tenant(current_user, tenant.tenant_id)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(tenant, k, v)
    await db.commit()
    await db.refresh(tenant)
    return success(TenantOut.model_validate(tenant))


@router.delete("/delete/{id}")
async def delete_tenant(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    tenant = (await db.execute(select(SysTenant).where(SysTenant.id == id, SysTenant.deleted == 0))).scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    _check_tenant(current_user, tenant.tenant_id)
    tenant.deleted = 1
    await db.commit()
    return success(msg="删除成功")
