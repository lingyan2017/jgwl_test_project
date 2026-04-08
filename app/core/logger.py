import logging
import logging.handlers
import sys
from pathlib import Path

# 日志目录（项目根目录下 logs/）
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logging(level: int = logging.INFO) -> None:
    """初始化全局日志：控制台 + 按天轮转文件"""
    root = logging.getLogger()
    if root.handlers:
        return  # 避免重复初始化
    root.setLevel(level)

    # 控制台 handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(_FORMATTER)
    root.addHandler(console)

    # 文件 handler（按天轮转，保留 30 天；若文件锁冲突则跳过）
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=LOG_DIR / "app.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
            delay=True,          # 延迟到第一次写入时再打开文件，避免启动时锁冲突
        )
        file_handler.setFormatter(_FORMATTER)
        root.addHandler(file_handler)
    except Exception:
        root.warning("无法创建文件日志 handler，仅使用控制台输出")

    # 降低高频三方库噪音
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
