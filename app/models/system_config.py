from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="配置项名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="配置项的简要描述")
    item_type: Mapped[int] = mapped_column(Integer, nullable=False, comment="配置项数据类型")
    item_value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置项值")
    weight: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="显示权重")
    version: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号")
    status: Mapped[int] = mapped_column(Integer, nullable=False, comment="是否有效.0:无效;1:有效")
    online_time: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="上线时间")
    offline_time: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="下线时间")
    ctime: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="记录创建时间")
    utime: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="记录更新时间")
    op_uid: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    remark: Mapped[str] = mapped_column(Text, nullable=False, comment="备注")
    sys_code: Mapped[str] = mapped_column(String(50), default="", nullable=False, comment="平台标识")
    quarantine: Mapped[str | None] = mapped_column(String(200), default="", comment="排除的平台")
