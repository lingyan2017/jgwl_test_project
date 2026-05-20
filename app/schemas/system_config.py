from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SystemConfigCreate(BaseModel):
    item_name: str
    description: str = ""
    item_type: int = 0
    item_value: str = ""
    weight: int = 0
    version: int = 1
    status: int = 1
    online_time: int = 0
    offline_time: int = 0
    remark: str = ""
    sys_code: str = ""
    quarantine: Optional[str] = ""


class SystemConfigUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[int] = None
    item_value: Optional[str] = None
    weight: Optional[int] = None
    version: Optional[int] = None
    status: Optional[int] = None
    online_time: Optional[int] = None
    offline_time: Optional[int] = None
    remark: Optional[str] = None
    sys_code: Optional[str] = None
    quarantine: Optional[str] = None


class SystemConfigOut(BaseModel):
    id: int
    item_name: str
    description: str
    item_type: int
    item_value: str
    weight: int
    version: int
    status: int
    online_time: int
    offline_time: int
    ctime: int
    utime: int
    op_uid: int
    remark: str
    sys_code: str
    quarantine: Optional[str] = ""

    model_config = {"from_attributes": True}
