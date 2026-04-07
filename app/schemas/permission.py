from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PermissionCreate(BaseModel):
    perm_code: str
    perm_name: str
    perm_type: int = 1
    resource_url: Optional[str] = None
    method: Optional[str] = None
    menu_id: Optional[int] = None
    status: int = 1


class PermissionUpdate(BaseModel):
    perm_name: Optional[str] = None
    perm_type: Optional[int] = None
    resource_url: Optional[str] = None
    method: Optional[str] = None
    menu_id: Optional[int] = None
    status: Optional[int] = None


class PermissionOut(BaseModel):
    id: int
    perm_code: str
    perm_name: str
    perm_type: int
    resource_url: Optional[str] = None
    method: Optional[str] = None
    menu_id: Optional[int] = None
    status: int
    create_time: Optional[datetime] = None

    model_config = {"from_attributes": True}
