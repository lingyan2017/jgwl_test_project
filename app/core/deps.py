from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from app.core.security import decode_access_token
from app.db.session import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    from app.models.user import SysUser

    result = await db.execute(
        select(SysUser).where(
            SysUser.id == int(user_id),
            SysUser.deleted == 0,
            SysUser.status == 1,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def require_admin(current_user=Depends(get_current_user)):
    """要求租户管理员(1)或超级管理员(0)，普通用户(2)被拒绝"""
    if current_user.user_type == 2:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user


async def require_super_admin(current_user=Depends(get_current_user)):
    """要求超级管理员(0)"""
    if current_user.user_type != 0:
        raise HTTPException(status_code=403, detail="权限不足，需要超级管理员权限")
    return current_user
