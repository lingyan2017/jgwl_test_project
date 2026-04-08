import json
import logging

import httpx

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.test_query_data import TestQueryData, TestQueryDataLog
from app.models.user import SysUser
from app.schemas.common import success
from app.schemas.test_query_data import (
    TestQueryDataCreate, TestQueryDataUpdate, TestQueryDataOut,
    TestQueryDataCallRequest, TestQueryDataCallResponse
)

router = APIRouter()
logger = logging.getLogger("app.test_query_data")


def _op(u: SysUser) -> str:
    """格式化操作人信息"""
    return f"{u.username}(id={u.id},tenant={u.tenant_id})"


@router.get("/list")
async def list_test_query_data(
    page: int = 1,
    page_size: int = 10,
    url: str | None = None,
    language: str | None = None,
    sys_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(TestQueryData).where(TestQueryData.deleted == 0)

    if url:
        q = q.where(TestQueryData.url.like(f"%{url}%"))
    if language:
        q = q.where(TestQueryData.language == language)
    if sys_code:
        q = q.where(TestQueryData.sys_code == sys_code)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(TestQueryData.id).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    
    # 转换params字段为字典
    result = []
    for item in items:
        item_dict = TestQueryDataOut.model_validate(item).model_dump()
        item_dict["params"] = json.loads(item.params)
        result.append(item_dict)
    
    return success({"total": total, "items": result})


@router.get("/get/{id}")
async def get_test_query_data(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    # 转换params字段为字典
    result = TestQueryDataOut.model_validate(test_data).model_dump()
    result["params"] = json.loads(test_data.params)
    
    return success(result)


@router.post("/create")
async def create_test_query_data(
    data: TestQueryDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    # 转换params为JSON字符串
    params_str = json.dumps(data.params)
    
    test_data = TestQueryData(
        url=data.url,
        language=data.language,
        sys_code=data.sys_code,
        params=params_str,
        create_user=current_user.username
    )
    db.add(test_data)
    await db.commit()
    await db.refresh(test_data)
    
    logger.info(
        "[TEST_QUERY_DATA] create  operator=%s -> url=%s language=%s sys_code=%s",
        _op(current_user), test_data.url, test_data.language, test_data.sys_code,
    )
    
    # 转换params字段为字典
    result = TestQueryDataOut.model_validate(test_data).model_dump()
    result["params"] = json.loads(test_data.params)
    
    return success(result)


@router.put("/update/{id}")
async def update_test_query_data(
    id: int,
    data: TestQueryDataUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    # 更新字段
    update_data = data.model_dump(exclude_none=True)
    if "params" in update_data:
        update_data["params"] = json.dumps(update_data["params"])
    update_data["update_user"] = current_user.username
    
    for k, v in update_data.items():
        setattr(test_data, k, v)
    
    await db.commit()
    await db.refresh(test_data)
    
    logger.info(
        "[TEST_QUERY_DATA] update  operator=%s -> id=%d url=%s",
        _op(current_user), test_data.id, test_data.url,
    )
    
    # 转换params字段为字典
    result = TestQueryDataOut.model_validate(test_data).model_dump()
    result["params"] = json.loads(test_data.params)
    
    return success(result)


@router.delete("/delete/{id}")
async def delete_test_query_data(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    test_data.deleted = 1
    test_data.update_user = current_user.username
    await db.commit()
    
    logger.warning(
        "[TEST_QUERY_DATA] delete  operator=%s -> id=%d url=%s",
        _op(current_user), test_data.id, test_data.url,
    )
    
    return success(msg="删除成功")


@router.post("/call")
async def call_test_query_data(
    data: TestQueryDataCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    # 获取测试数据
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == data.test_query_data_id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    # 准备请求参数
    request_params = data.params or json.loads(test_data.params)
    url = test_data.url
    
    # 发送请求
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request_params, timeout=30.0)
            response_data = response.json()
            status = 1  # 成功
            error_msg = None
    except Exception as e:
        response_data = {"error": str(e)}
        status = 0  # 失败
        error_msg = str(e)
    
    # 记录日志
    log = TestQueryDataLog(
        test_query_data_id=test_data.id,
        request_params=json.dumps(request_params),
        response_data=json.dumps(response_data),
        status=status,
        error_msg=error_msg,
        create_user=current_user.username
    )
    db.add(log)
    await db.commit()
    
    # 返回响应
    if status == 1:
        return success(TestQueryDataCallResponse(
            success=True,
            data=response_data
        ))
    else:
        return success(TestQueryDataCallResponse(
            success=False,
            error=error_msg
        ))


@router.get("/logs/{test_query_data_id}")
async def get_test_query_data_logs(
    test_query_data_id: int,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    q = select(TestQueryDataLog).where(TestQueryDataLog.test_query_data_id == test_query_data_id)
    
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    items = (await db.execute(q.order_by(TestQueryDataLog.create_time.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    
    # 转换字段为字典
    result = []
    for item in items:
        item_dict = {
            "id": item.id,
            "test_query_data_id": item.test_query_data_id,
            "request_params": json.loads(item.request_params),
            "response_data": json.loads(item.response_data),
            "status": item.status,
            "error_msg": item.error_msg,
            "create_time": item.create_time,
            "create_user": item.create_user
        }
        result.append(item_dict)
    
    return success({"total": total, "items": result})