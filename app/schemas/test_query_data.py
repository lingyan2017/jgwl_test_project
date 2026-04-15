from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class TestQueryDataCreate(BaseModel):
    url: str
    url_desc: Optional[str] = None  # URL说明
    language: str  # java 或 go
    params: Dict[str, Any]  # JSON格式的请求参数
    has_image: Optional[int] = 0  # 是否包含图片：0-否，1-是
    create_user: Optional[str] = None


class TestQueryDataUpdate(BaseModel):
    url: Optional[str] = None
    url_desc: Optional[str] = None  # URL说明
    language: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    has_image: Optional[int] = None  # 是否包含图片：0-否，1-是
    update_user: Optional[str] = None


class TestQueryDataOut(BaseModel):
    id: int
    url: str
    url_desc: Optional[str] = None  # URL说明
    language: str
    params: str | Dict[str, Any]  # 支持字符串或字典类型
    has_image: Optional[int] = 0  # 是否包含图片：0-否，1-是
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
    sys_code: str  # 系统编码（调用时传入）
    params: Optional[Dict[str, Any]] = None
    run_mode: Optional[int] = None  # 0-测试环境, 1-生产环境


class TestQueryDataCallResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None