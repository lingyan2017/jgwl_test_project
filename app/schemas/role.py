from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoleCreate(BaseModel):
    tenant_id: str
    role_name: str
    role_key: str
    role_sort: int = 0
    data_scope: int = 1
    status: int = 1
    remark: Optional[str] = None
    menu_ids: list[int] = []


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    role_sort: Optional[int] = None
    data_scope: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None
    menu_ids: Optional[list[int]] = None


class RoleOut(BaseModel):
    id: int
    tenant_id: str
    role_name: str
    role_key: str
    role_sort: int
    data_scope: int
    status: int
    remark: Optional[str] = None
    create_time: Optional[datetime] = None

    model_config = {"from_attributes": True}
