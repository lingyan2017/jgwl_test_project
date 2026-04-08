from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SysConfigCreate(BaseModel):
    item_name: str
    item_value: str
    sys_code: str
    create_user: Optional[str] = None


class SysConfigUpdate(BaseModel):
    item_name: Optional[str] = None
    item_value: Optional[str] = None
    sys_code: Optional[str] = None
    update_user: Optional[str] = None


class SysConfigOut(BaseModel):
    id: int
    item_name: str
    item_value: str
    sys_code: str
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_user: Optional[str] = None
    update_user: Optional[str] = None

    model_config = {"from_attributes": True}