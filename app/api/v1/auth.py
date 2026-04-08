import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.user import LoginRequest

router = APIRouter()
logger = logging.getLogger("app.auth")


def _get_ip(request: Request) -> str:
    return request.headers.get("x-forwarded-for") or (
        request.client.host if request.client else "unknown"
    )


@router.post("/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _get_ip(request)
    result = await db.execute(
        select(SysUser).where(
            SysUser.username == data.username,
            SysUser.tenant_id == data.tenant_id,
            SysUser.deleted == 0,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        logger.warning(
            "[AUTH] login failed  user=%s tenant=%s ip=%s reason=用户名或密码错误",
            data.username, data.tenant_id, ip,
        )
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if user.status != 1:
        logger.warning(
            "[AUTH] login failed  user=%s tenant=%s ip=%s reason=账号已被禁用",
            data.username, data.tenant_id, ip,
        )
        raise HTTPException(status_code=400, detail="账号已被禁用")

    await db.execute(
        update(SysUser).where(SysUser.id == user.id).values(last_login=datetime.now())
    )
    await db.commit()

    token = create_access_token({"sub": str(user.id), "tenant_id": user.tenant_id})
    logger.info(
        "[AUTH] login success  user=%s(id=%d) tenant=%s user_type=%d ip=%s",
        user.username, user.id, user.tenant_id, user.user_type, ip,
    )
    return success(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "tenant_id": user.tenant_id,
                "user_type": user.user_type,
                "avatar": user.avatar,
            },
        }
    )


@router.get("/me")
async def get_me(current_user: SysUser = Depends(get_current_user)):
    return success(
        {
            "id": current_user.id,
            "username": current_user.username,
            "real_name": current_user.real_name,
            "tenant_id": current_user.tenant_id,
            "user_type": current_user.user_type,
            "email": current_user.email,
            "phone": current_user.phone,
            "avatar": current_user.avatar,
        }
    )


@router.post("/logout")
async def logout(current_user: SysUser = Depends(get_current_user)):
    logger.info(
        "[AUTH] logout  user=%s(id=%d) tenant=%s",
        current_user.username, current_user.id, current_user.tenant_id,
    )
    return success(msg="退出成功")
