from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysMenu(Base):
    __tablename__ = "sys_menu"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0)
    menu_name: Mapped[str] = mapped_column(String(64), nullable=False)
    menu_type: Mapped[int | None] = mapped_column(SmallInteger)
    path: Mapped[str | None] = mapped_column(String(256))
    component: Mapped[str | None] = mapped_column(String(256))
    icon: Mapped[str | None] = mapped_column(String(64))
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    perms: Mapped[str | None] = mapped_column(String(256))
    is_frame: Mapped[int] = mapped_column(SmallInteger, default=0)
    visible: Mapped[int] = mapped_column(SmallInteger, default=1)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
