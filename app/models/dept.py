from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysDept(Base):
    __tablename__ = "sys_dept"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0)
    dept_name: Mapped[str] = mapped_column(String(64), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    leader: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
