from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TestQueryData(Base):
    __tablename__ = "test_query_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    url_desc: Mapped[str | None] = mapped_column(String(256))  # URL说明
    language: Mapped[str] = mapped_column(String(16), nullable=False)  # java 或 go
    sys_code: Mapped[str] = mapped_column(String(32), nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=False)  # JSON格式的请求参数
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    create_user: Mapped[str | None] = mapped_column(String(64))
    update_user: Mapped[str | None] = mapped_column(String(64))


class TestQueryDataLog(Base):
    __tablename__ = "test_query_data_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_query_data_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    request_params: Mapped[str] = mapped_column(Text, nullable=False)  # 请求参数
    response_data: Mapped[str] = mapped_column(Text, nullable=False)  # 响应数据
    status: Mapped[int] = mapped_column(SmallInteger, default=1)  # 1成功 0失败
    error_msg: Mapped[str | None] = mapped_column(Text)  # 错误信息
    create_time: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    create_user: Mapped[str | None] = mapped_column(String(64))