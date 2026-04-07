from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysPermission(Base):
    __tablename__ = "sys_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    perm_code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    perm_name: Mapped[str] = mapped_column(String(128), nullable=False)
    perm_type: Mapped[int] = mapped_column(SmallInteger, default=1)
    resource_url: Mapped[str | None] = mapped_column(String(256))
    method: Mapped[str | None] = mapped_column(String(16))
    menu_id: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
