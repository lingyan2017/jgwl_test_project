from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SysConfig(Base):
    __tablename__ = "sys_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    aes_key: Mapped[str] = mapped_column(String(128), nullable=False, comment="aes加密key")
    aes_iv: Mapped[str] = mapped_column(String(512), nullable=False, comment="aes加密iv")
    java_domain_name: Mapped[str] = mapped_column(String(255), default="", nullable=False, comment="apiservice域名")
    go_domain_name: Mapped[str] = mapped_column(String(100), default="", nullable=False, comment="api域名")
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="状态 0不可用,1可用")
    run_mode: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="0测试环境,1生产环境")
    sys_code: Mapped[str] = mapped_column(String(32), nullable=False, comment="系统编码")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), comment="创建时间")
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    create_user: Mapped[str | None] = mapped_column(String(64), comment="创建人")
    update_user: Mapped[str | None] = mapped_column(String(64), comment="更新人")