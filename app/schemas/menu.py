from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MenuCreate(BaseModel):
    parent_id: int = 0
    menu_name: str
    menu_type: int = 2
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    order_num: int = 0
    perms: Optional[str] = None
    is_frame: int = 0
    visible: int = 1
    status: int = 1


class MenuUpdate(BaseModel):
    parent_id: Optional[int] = None
    menu_name: Optional[str] = None
    menu_type: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    order_num: Optional[int] = None
    perms: Optional[str] = None
    is_frame: Optional[int] = None
    visible: Optional[int] = None
    status: Optional[int] = None


class MenuOut(BaseModel):
    id: int
    parent_id: int
    menu_name: str
    menu_type: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    order_num: int
    perms: Optional[str] = None
    is_frame: int
    visible: int
    status: int
    create_time: Optional[datetime] = None
    children: list[MenuOut] = []

    model_config = {"from_attributes": True}


MenuOut.model_rebuild()
