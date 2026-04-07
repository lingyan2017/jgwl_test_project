from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    tenant_id: str
    post_code: str
    post_name: str
    post_sort: int = 0
    status: int = 1
    remark: Optional[str] = None


class PostUpdate(BaseModel):
    post_code: Optional[str] = None
    post_name: Optional[str] = None
    post_sort: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class PostOut(BaseModel):
    id: int
    tenant_id: str
    post_code: str
    post_name: str
    post_sort: int
    status: int
    remark: Optional[str] = None
    create_time: Optional[datetime] = None

    model_config = {"from_attributes": True}
