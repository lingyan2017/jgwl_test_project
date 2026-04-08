from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysConfig(Base):
    __tablename__ = "sys_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    item_value: Mapped[str] = mapped_column(String(512), nullable=False)
    sys_code: Mapped[str] = mapped_column(String(32), nullable=False)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    create_user: Mapped[str | None] = mapped_column(String(64))
    update_user: Mapped[str | None] = mapped_column(String(64))