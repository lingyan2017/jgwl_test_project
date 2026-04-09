from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class TestQueryDataCreate(BaseModel):
    url: str
    language: str  # java 或 go
    sys_code: str
    params: Dict[str, Any]  # JSON格式的请求参数
    create_user: Optional[str] = None


class TestQueryDataUpdate(BaseModel):
    url: Optional[str] = None
    language: Optional[str] = None
    sys_code: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    update_user: Optional[str] = None


class TestQueryDataOut(BaseModel):
    id: int
    url: str
    language: str
    sys_code: str
    params: str | Dict[str, Any]  # 支持字符串或字典类型
    deleted: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_user: Optional[str] = None
    update_user: Optional[str] = None

    model_config = {"from_attributes": True}


class TestQueryDataLogCreate(BaseModel):
    test_query_data_id: int
    request_params: Dict[str, Any]
    response_data: Dict[str, Any]
    status: int
    error_msg: Optional[str] = None
    create_user: Optional[str] = None


class TestQueryDataLogOut(BaseModel):
    id: int
    test_query_data_id: int
    request_params: Dict[str, Any]
    response_data: Dict[str, Any]
    status: int
    error_msg: Optional[str] = None
    create_time: Optional[datetime] = None
    create_user: Optional[str] = None

    model_config = {"from_attributes": True}


class TestQueryDataCallRequest(BaseModel):
    test_query_data_id: int
    params: Optional[Dict[str, Any]] = None


class TestQueryDataCallResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None