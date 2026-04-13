from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SysConfigCreate(BaseModel):
    aes_key: str
    aes_iv: str
    java_domain_name: str = ""
    go_domain_name: str = ""
    status: int = 0
    run_mode: int = 0
    sys_code: str
    create_user: Optional[str] = None


class SysConfigUpdate(BaseModel):
    aes_key: Optional[str] = None
    aes_iv: Optional[str] = None
    java_domain_name: Optional[str] = None
    go_domain_name: Optional[str] = None
    status: Optional[int] = None
    run_mode: Optional[int] = None
    sys_code: Optional[str] = None
    update_user: Optional[str] = None


class SysConfigOut(BaseModel):
    id: int
    aes_key: str
    aes_iv: str
    java_domain_name: str
    go_domain_name: str
    status: int
    run_mode: int
    sys_code: str
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_user: Optional[str] = None
    update_user: Optional[str] = None

    model_config = {"from_attributes": True}