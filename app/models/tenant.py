from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysTenant(Base):
    __tablename__ = "sys_tenant"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    tenant_name: Mapped[str] = mapped_column(String(128), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(64))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    contact_email: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
