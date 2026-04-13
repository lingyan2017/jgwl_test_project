import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.sys_config import SysConfig
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.sys_config import SysConfigCreate, SysConfigUpdate, SysConfigOut

router = APIRouter()
logger = logging.getLogger("app.sys_config")


def _op(u: SysUser) -> str:
    """格式化操作人信息"""
    return f"{u.username}(id={u.id},tenant={u.tenant_id})"


@router.get("/list")
async def list_sys_config(
    page: int = 1,
    page_size: int = 10,
    sys_code: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SysConfig)

    if sys_code:
        q = q.where(SysConfig.sys_code == sys_code)
    if status is not None:
        q = q.where(SysConfig.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(SysConfig.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    
    return success({"total": total, "items": [SysConfigOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_sys_config(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    config = (await db.execute(select(SysConfig).where(SysConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return success(SysConfigOut.model_validate(config))


@router.post("/create")
async def create_sys_config(
    data: SysConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    config = SysConfig(
        aes_key=data.aes_key,
        aes_iv=data.aes_iv,
        java_domain_name=data.java_domain_name,
        go_domain_name=data.go_domain_name,
        status=data.status,
        run_mode=data.run_mode,
        sys_code=data.sys_code,
        create_user=current_user.username
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    logger.info(
        "[SYS_CONFIG] create  operator=%s -> sys_code=%s aes_key=%s",
        _op(current_user), config.sys_code, config.aes_key,
    )
    
    return success(SysConfigOut.model_validate(config))


@router.put("/update/{id}")
async def update_sys_config(
    id: int,
    data: SysConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    config = (await db.execute(select(SysConfig).where(SysConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 更新字段
    update_data = data.model_dump(exclude_none=True)
    update_data["update_user"] = current_user.username
    
    for k, v in update_data.items():
        setattr(config, k, v)
    
    await db.commit()
    await db.refresh(config)
    
    logger.info(
        "[SYS_CONFIG] update  operator=%s -> id=%d sys_code=%s",
        _op(current_user), config.id, config.sys_code,
    )
    
    return success(SysConfigOut.model_validate(config))


@router.delete("/delete/{id}")
async def delete_sys_config(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    config = (await db.execute(select(SysConfig).where(SysConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.delete(config)
    await db.commit()
    
    logger.warning(
        "[SYS_CONFIG] delete  operator=%s -> id=%d sys_code=%s",
        _op(current_user), config.id, config.sys_code,
    )
    
    return success(msg="删除成功")