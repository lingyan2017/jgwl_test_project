import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.system_config import SystemConfig
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate, SystemConfigOut

router = APIRouter()
logger = logging.getLogger("app.system_config")


def _op(u: SysUser) -> str:
    return f"{u.username}(id={u.id},tenant={u.tenant_id})"


@router.get("/list")
async def list_system_config(
    page: int = 1,
    page_size: int = 10,
    item_name: str | None = None,
    sys_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(SystemConfig)

    if item_name:
        q = q.where(SystemConfig.item_name.like(f"%{item_name}%"))
    if sys_code:
        q = q.where(SystemConfig.sys_code == sys_code)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (
        await db.execute(
            q.order_by(SystemConfig.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return success({"total": total, "items": [SystemConfigOut.model_validate(i) for i in items]})


@router.get("/get/{id}")
async def get_system_config(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    config = (await db.execute(select(SystemConfig).where(SystemConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return success(SystemConfigOut.model_validate(config))


@router.post("/create")
async def create_system_config(
    data: SystemConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    now = int(time.time())
    config = SystemConfig(
        item_name=data.item_name,
        description=data.description,
        item_type=data.item_type,
        item_value=data.item_value,
        weight=data.weight,
        version=data.version,
        status=data.status,
        online_time=data.online_time,
        offline_time=data.offline_time,
        ctime=now,
        utime=now,
        op_uid=current_user.id,
        remark=data.remark,
        sys_code=data.sys_code,
        quarantine=data.quarantine or "",
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)

    logger.info(
        "[SYSTEM_CONFIG] create  operator=%s -> item_name=%s sys_code=%s",
        _op(current_user), config.item_name, config.sys_code,
    )

    return success(SystemConfigOut.model_validate(config))


@router.put("/update/{id}")
async def update_system_config(
    id: int,
    data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    config = (await db.execute(select(SystemConfig).where(SystemConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")

    update_data = data.model_dump(exclude_none=True)
    for k, v in update_data.items():
        setattr(config, k, v)

    config.utime = int(time.time())
    config.op_uid = current_user.id

    await db.commit()
    await db.refresh(config)

    logger.info(
        "[SYSTEM_CONFIG] update  operator=%s -> id=%d item_name=%s",
        _op(current_user), config.id, config.item_name,
    )

    return success(SystemConfigOut.model_validate(config))


@router.delete("/delete/{id}")
async def delete_system_config(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    config = (await db.execute(select(SystemConfig).where(SystemConfig.id == id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")

    await db.delete(config)
    await db.commit()

    logger.warning(
        "[SYSTEM_CONFIG] delete  operator=%s -> id=%d item_name=%s",
        _op(current_user), config.id, config.item_name,
    )

    return success(msg="删除成功")
