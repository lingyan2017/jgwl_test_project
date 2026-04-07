from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


def success(data: Any = None, msg: str = "success") -> dict:
    return {"code": 200, "msg": msg, "data": data}


def error(msg: str = "error", code: int = 500) -> dict:
    return {"code": code, "msg": msg, "data": None}


class PageData(BaseModel, Generic[T]):
    total: int
    items: list[T]
