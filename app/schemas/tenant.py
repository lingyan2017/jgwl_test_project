from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TenantCreate(BaseModel):
    tenant_id: str
    tenant_name: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: int = 1


class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[int] = None


class TenantOut(BaseModel):
    id: int
    tenant_id: str
    tenant_name: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: int
    create_time: Optional[datetime] = None

    model_config = {"from_attributes": True}
