from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DeptCreate(BaseModel):
    tenant_id: str
    parent_id: int = 0
    dept_name: str
    order_num: int = 0
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: int = 1


class DeptUpdate(BaseModel):
    parent_id: Optional[int] = None
    dept_name: Optional[str] = None
    order_num: Optional[int] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[int] = None


class DeptOut(BaseModel):
    id: int
    tenant_id: str
    parent_id: int
    dept_name: str
    order_num: int
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: int
    create_time: Optional[datetime] = None
    children: list[DeptOut] = []

    model_config = {"from_attributes": True}


DeptOut.model_rebuild()
