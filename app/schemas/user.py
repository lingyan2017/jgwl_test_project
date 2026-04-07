from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    tenant_id: str
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: int = 0
    dept_id: Optional[int] = None
    post_id: Optional[int] = None
    user_type: int = 2
    status: int = 1
    role_ids: list[int] = []


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[int] = None
    dept_id: Optional[int] = None
    post_id: Optional[int] = None
    status: Optional[int] = None
    role_ids: Optional[list[int]] = None


class UserOut(BaseModel):
    id: int
    tenant_id: str
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: int
    dept_id: Optional[int] = None
    post_id: Optional[int] = None
    user_type: int
    status: int
    create_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str
    tenant_id: str = "default"
