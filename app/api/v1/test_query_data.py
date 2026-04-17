import json
import logging
import urllib.parse
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.core.aes_cipher import AESCipher
from app.db.session import get_db
from app.models.test_query_data import TestQueryData, TestQueryDataLog
from app.models.sys_config import SysConfig
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
        # 如果params是字符串，转换为字典
        if isinstance(item_dict["params"], str):
            try:
                item_dict["params"] = json.loads(item_dict["params"])
            except:
                item_dict["params"] = {}
        result.append(item_dict)
    
    return success({"total": total, "items": result})


@router.get("/get/{id}")
async def get_test_query_data(id: int, db: AsyncSession = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    # 转换params字段为字典
    result = TestQueryDataOut.model_validate(test_data).model_dump()
    # 如果params是字符串，转换为字典
    if isinstance(result["params"], str):
        try:
            result["params"] = json.loads(result["params"])
        except:
            result["params"] = {}
    
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
        url_desc=data.url_desc,
        language=data.language,
        params=params_str,
        has_image=data.has_image,
        create_user=current_user.username
    )
    db.add(test_data)
    await db.commit()
    await db.refresh(test_data)
    
    logger.info(
        "[TEST_QUERY_DATA] create  operator=%s -> url=%s language=%s",
        _op(current_user), test_data.url, test_data.language,
    )
    
    # 转换params字段为字典
    result = TestQueryDataOut.model_validate(test_data).model_dump()
    # 如果params是字符串，转换为字典
    if isinstance(result["params"], str):
        try:
            result["params"] = json.loads(result["params"])
        except:
            result["params"] = {}
    
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
    # 如果params是字符串，转换为字典
    if isinstance(result["params"], str):
        try:
            result["params"] = json.loads(result["params"])
        except:
            result["params"] = {}
    
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
    logger.info(f"[TEST_QUERY_DATA] 开始调用接口 - test_query_data_id={data.test_query_data_id}, sys_code={data.sys_code}")
    
    # 获取测试数据
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == data.test_query_data_id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        logger.warning(f"[TEST_QUERY_DATA] 测试数据不存在 - id={data.test_query_data_id}")
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    logger.info(f"[TEST_QUERY_DATA] 获取测试数据成功 - url={test_data.url}, language={test_data.language}")
    
    # 准备请求参数
    request_params = data.params or json.loads(test_data.params)
    language = test_data.language  # java 或 go
    sys_code = data.sys_code  # 从调用参数中获取
    
    logger.info(f"[TEST_QUERY_DATA] 请求参数 - Keys: {list(request_params.keys()) if isinstance(request_params, dict) else 'N/A'}")
    
    # 获取 run_mode 参数（优先使用前端传递的，否则使用默认值 0）
    run_mode = data.run_mode if data.run_mode is not None else 0
    logger.info(f"[TEST_QUERY_DATA] 运行模式 - run_mode={run_mode} ({'生产环境' if run_mode == 1 else '测试环境'})")
    
    # 根据 sys_code、status 和 run_mode 查询系统配置
    config = (await db.execute(
        select(SysConfig).where(
            SysConfig.sys_code == sys_code,
            SysConfig.status == 1,  # 只查询可用的配置
            SysConfig.run_mode == run_mode  # 匹配运行模式
        )
    )).scalar_one_or_none()
    
    if not config:
        logger.error(f"[TEST_QUERY_DATA] 未找到系统配置 - sys_code={sys_code}, run_mode={run_mode}")
        raise HTTPException(status_code=404, detail=f"未找到系统配置: sys_code={sys_code}, run_mode={run_mode}")
    
    logger.info(f"[TEST_QUERY_DATA] 获取系统配置成功 - sys_code={config.sys_code}, status={config.status}, run_mode={config.run_mode}")
    
    # 根据语言选择域名
    domain_name = config.java_domain_name if language == "java" else config.go_domain_name
    if not domain_name:
        logger.error(f"[TEST_QUERY_DATA] {language.upper()} 域名未配置")
        raise HTTPException(status_code=400, detail=f"{language.upper()} 域名未配置")
    
    logger.info(f"[TEST_QUERY_DATA] 使用域名 - language={language}, domain={domain_name}")
    
    # 使用 AES 加密请求参数
    try:
        logger.info(f"[TEST_QUERY_DATA] 开始 AES 加密 - key_length={len(config.aes_key)}, iv_length={len(config.aes_iv)}")
        aes_cipher = AESCipher(config.aes_key, config.aes_iv)
        encrypted_data = aes_cipher.encrypt_json(request_params)
        logger.info(f"[TEST_QUERY_DATA] AES 加密成功 - 加密数据长度: {len(encrypted_data)} chars")
    except Exception as e:
        logger.error(f"[TEST_QUERY_DATA] AES 加密失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AES 加密失败: {str(e)}")
    
    # 构建请求 URL: domain_name?data=encrypted_data
    if run_mode == 0:
        if language == "java":
            url = f"{domain_name}/gateway/ApiService{test_data.url}?source={sys_code}&data={encrypted_data}"
        else:
            url = f"{domain_name}{test_data.url}?data={encrypted_data}&source={sys_code}"
    else:
        logger.info(f"[TEST_QUERY_DATA] 禁止使用生产环境 - language={language}, domain={domain_name}")
        return success(msg="禁止使用生产环境")

    logger.info(
        "[TEST_QUERY_DATA] 发送请求 - operator=%s sys_code=%s language=%s domain=%s",
        _op(current_user), sys_code, language, domain_name,
    )
    logger.info(f"[TEST_QUERY_DATA] 完整 URL: {url[:200]}...")
    
    # 发送 GET 请求
    try:
        logger.info(f"[TEST_QUERY_DATA] 发起 HTTP POST 请求...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, timeout=30.0)
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"[TEST_QUERY_DATA] HTTP 请求成功 - 状态码: {response.status_code}")
            logger.debug(f"[TEST_QUERY_DATA] 响应 JSON: {json.dumps(response_json, ensure_ascii=False)[:200]}...")
            status = 1  # 成功
            error_msg = None
    except Exception as e:
        response_json = {}
        status = 0  # 失败
        error_msg = str(e)
        logger.error(f"[TEST_QUERY_DATA] HTTP 请求失败: {e}", exc_info=True)
    
    # 解密响应数据中的 data 字段
    decrypted_response = None
    if status == 1 and response_json:
        try:
            # 获取加密的 data 字段
            encrypted_data = response_json.get("data", "")
            
            if not encrypted_data:
                logger.warning("[TEST_QUERY_DATA] 响应中 data 字段为空")
                response_data = response_json
            else:
                logger.info(f"[TEST_QUERY_DATA] 开始 AES 解密响应 data - 加密数据长度: {len(encrypted_data)} chars")
                decrypted_data = aes_cipher.decrypt(encrypted_data)
                logger.info(f"[TEST_QUERY_DATA] AES 解密成功 - 解密后长度: {len(decrypted_data)} bytes")
                
                # 尝试解析为 JSON
                try:
                    decrypted_json = json.loads(decrypted_data)
                    logger.info(f"[TEST_QUERY_DATA] JSON 解析成功 - Keys: {list(decrypted_json.keys()) if isinstance(decrypted_json, dict) else 'N/A'}")
                    
                    # 构建最终响应：保留 code, message，替换 data 为解密后的内容
                    response_data = {
                        "code": response_json.get("code", 0),
                        "message": response_json.get("message", ""),
                        "data": decrypted_json
                    }
                except json.JSONDecodeError:
                    logger.warning(f"[TEST_QUERY_DATA] 解密后的数据不是有效 JSON，返回原始字符串")
                    response_data = {
                        "code": response_json.get("code", 0),
                        "message": response_json.get("message", ""),
                        "data": decrypted_data
                    }
        except Exception as e:
            logger.error(f"[TEST_QUERY_DATA] AES 解密失败: {e}", exc_info=True)
            response_data = {"error": f"解密失败: {str(e)}", "original_response": response_json}
            status = 0
            error_msg = f"AES 解密失败: {str(e)}"
    else:
        response_data = {"error": error_msg} if error_msg else {}
    
    # 记录日志
    log = TestQueryDataLog(
        test_query_data_id=test_data.id,
        sys_code=sys_code,
        request_params=json.dumps(request_params, ensure_ascii=False),
        response_data=json.dumps(response_data, ensure_ascii=False),
        status=status,
        error_msg=error_msg,
        create_user=current_user.username
    )
    db.add(log)
    await db.commit()
    
    logger.info(f"[TEST_QUERY_DATA] 调用完成 - status={'成功' if status == 1 else '失败'}, 日志已保存")
    
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


@router.post("/call-with-files")
async def call_test_query_data_with_files(
    test_query_data_id: int = Form(...),
    sys_code: str = Form(...),
    run_mode: Optional[int] = Form(None),
    params: str = Form("{}"),  # 以JSON字符串形式接收参数
    files: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    logger.info(f"[TEST_QUERY_DATA] 开始调用接口(带文件) - test_query_data_id={test_query_data_id}, sys_code={sys_code}")
    
    # 获取测试数据
    test_data = (await db.execute(select(TestQueryData).where(TestQueryData.id == test_query_data_id, TestQueryData.deleted == 0))).scalar_one_or_none()
    if not test_data:
        logger.warning(f"[TEST_QUERY_DATA] 测试数据不存在 - id={test_query_data_id}")
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    logger.info(f"[TEST_QUERY_DATA] 获取测试数据成功 - url={test_data.url}, language={test_data.language}, has_image={test_data.has_image}")
    
    # 解析请求参数
    try:
        request_params = json.loads(params) if params else json.loads(test_data.params)
    except json.JSONDecodeError:
        request_params = json.loads(test_data.params)
    
    language = test_data.language  # java 或 go
    
    logger.info(f"[TEST_QUERY_DATA] 请求参数 - Keys: {list(request_params.keys()) if isinstance(request_params, dict) else 'N/A'}")
    
    # 获取 run_mode 参数（优先使用前端传递的，否则使用默认值 0）
    run_mode = run_mode if run_mode is not None else 0
    logger.info(f"[TEST_QUERY_DATA] 运行模式 - run_mode={run_mode} ({'生产环境' if run_mode == 1 else '测试环境'})")
    
    # 根据 sys_code、status 和 run_mode 查询系统配置
    config = (await db.execute(
        select(SysConfig).where(
            SysConfig.sys_code == sys_code,
            SysConfig.status == 1,  # 只查询可用的配置
            SysConfig.run_mode == run_mode  # 匹配运行模式
        )
    )).scalar_one_or_none()
    
    if not config:
        logger.error(f"[TEST_QUERY_DATA] 未找到系统配置 - sys_code={sys_code}, run_mode={run_mode}")
        raise HTTPException(status_code=404, detail=f"未找到系统配置: sys_code={sys_code}, run_mode={run_mode}")
    
    logger.info(f"[TEST_QUERY_DATA] 获取系统配置成功 - sys_code={config.sys_code}, status={config.status}, run_mode={config.run_mode}")
    
    # 根据语言选择域名
    domain_name = config.java_domain_name if language == "java" else config.go_domain_name
    if not domain_name:
        logger.error(f"[TEST_QUERY_DATA] {language.upper()} 域名未配置")
        raise HTTPException(status_code=400, detail=f"{language.upper()} 域名未配置")
    
    logger.info(f"[TEST_QUERY_DATA] 使用域名 - language={language}, domain={domain_name}")
    
    # 准备请求体 - 如果有文件则使用multipart格式
    if files and len(files) > 0 and any(file.filename for file in files if file):  # 如果有非空文件
        # 使用multipart/form-data格式发送请求
        import tempfile
        import os
        
        # 准备multipart数据
        multipart_data = []
        
        # 添加请求参数（AES加密后）
        try:
            logger.info(f"[TEST_QUERY_DATA] 开始 AES 加密 - key_length={len(config.aes_key)}, iv_length={len(config.aes_iv)}")
            aes_cipher = AESCipher(config.aes_key, config.aes_iv)
            encrypted_data = aes_cipher.encrypt_json(request_params)
            logger.info(f"[TEST_QUERY_DATA] AES 加密成功 - 加密数据长度: {len(encrypted_data)} chars")
        except Exception as e:
            logger.error(f"[TEST_QUERY_DATA] AES 加密失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"AES 加密失败: {str(e)}")
        
        multipart_data.append(("data", encrypted_data))
        multipart_data.append(("source", sys_code))
        
        # 添加文件
        for file in files:
            if file and file.filename:  # 确保文件存在且有名称
                multipart_data.append(("files", (file.filename, await file.read(), file.content_type)))
        
        # 构建请求 URL
        if run_mode == 0:
            if language == "java":
                url = f"{domain_name}gatewat/ApiService{test_data.url}"
            else:
                url = f"{domain_name}{test_data.url}"
        else:
            logger.info(f"[TEST_QUERY_DATA] 禁止使用生产环境 - language={language}, domain={domain_name}")
            return success(msg="禁止使用生产环境")
        
        logger.info(f"[TEST_QUERY_DATA] 发起 HTTP POST 请求(带文件)...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, files=multipart_data, timeout=30.0)
                response.raise_for_status()
                response_json = response.json()
                logger.info(f"[TEST_QUERY_DATA] HTTP 请求成功 - 状态码: {response.status_code}")
                logger.debug(f"[TEST_QUERY_DATA] 响应 JSON: {json.dumps(response_json, ensure_ascii=False)[:200]}...")
                status = 1  # 成功
                error_msg = None
        except Exception as e:
            response_json = {}
            status = 0  # 失败
            error_msg = str(e)
            logger.error(f"[TEST_QUERY_DATA] HTTP 请求失败: {e}", exc_info=True)
    else:
        # 没有文件，使用普通POST请求（向后兼容）
        try:
            logger.info(f"[TEST_QUERY_DATA] 开始 AES 加密 - key_length={len(config.aes_key)}, iv_length={len(config.aes_iv)}")
            aes_cipher = AESCipher(config.aes_key, config.aes_iv)
            encrypted_data = aes_cipher.encrypt_json(request_params)
            logger.info(f"[TEST_QUERY_DATA] AES 加密成功 - 加密数据长度: {len(encrypted_data)} chars")
        except Exception as e:
            logger.error(f"[TEST_QUERY_DATA] AES 加密失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"AES 加密失败: {str(e)}")
        
        # 构建请求 URL: domain_name?data=encrypted_data
        if run_mode == 0:
            if language == "java":
                url = f"{domain_name}gatewat/ApiService{test_data.url}?data={encrypted_data}"
            else:
                url = f"{domain_name}{test_data.url}?data={encrypted_data}&source={sys_code}"
        else:
            logger.info(f"[TEST_QUERY_DATA] 禁止使用生产环境 - language={language}, domain={domain_name}")
            return success(msg="禁止使用生产环境")

        logger.info(f"[TEST_QUERY_DATA] 发起 HTTP POST 请求...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, timeout=30.0)
                response.raise_for_status()
                response_json = response.json()
                logger.info(f"[TEST_QUERY_DATA] HTTP 请求成功 - 状态码: {response.status_code}")
                logger.debug(f"[TEST_QUERY_DATA] 响应 JSON: {json.dumps(response_json, ensure_ascii=False)[:200]}...")
                status = 1  # 成功
                error_msg = None
        except Exception as e:
            response_json = {}
            status = 0  # 失败
            error_msg = str(e)
            logger.error(f"[TEST_QUERY_DATA] HTTP 请求失败: {e}", exc_info=True)
    
    # 解密响应数据中的 data 字段
    decrypted_response = None
    if status == 1 and response_json:
        try:
            # 获取加密的 data 字段
            encrypted_data = response_json.get("data", "")
            
            if not encrypted_data:
                logger.warning("[TEST_QUERY_DATA] 响应中 data 字段为空")
                response_data = response_json
            else:
                logger.info(f"[TEST_QUERY_DATA] 开始 AES 解密响应 data - 加密数据长度: {len(encrypted_data)} chars")
                decrypted_data = aes_cipher.decrypt(encrypted_data)
                logger.info(f"[TEST_QUERY_DATA] AES 解密成功 - 解密后长度: {len(decrypted_data)} bytes")
                
                # 尝试解析为 JSON
                try:
                    decrypted_json = json.loads(decrypted_data)
                    logger.info(f"[TEST_QUERY_DATA] JSON 解析成功 - Keys: {list(decrypted_json.keys()) if isinstance(decrypted_json, dict) else 'N/A'}")
                    
                    # 构建最终响应：保留 code, message，替换 data 为解密后的内容
                    response_data = {
                        "code": response_json.get("code", 0),
                        "message": response_json.get("message", ""),
                        "data": decrypted_json
                    }
                except json.JSONDecodeError:
                    logger.warning(f"[TEST_QUERY_DATA] 解密后的数据不是有效 JSON，返回原始字符串")
                    response_data = {
                        "code": response_json.get("code", 0),
                        "message": response_json.get("message", ""),
                        "data": decrypted_data
                    }
        except Exception as e:
            logger.error(f"[TEST_QUERY_DATA] AES 解密失败: {e}", exc_info=True)
            response_data = {"error": f"解密失败: {str(e)}", "original_response": response_json}
            status = 0
            error_msg = f"AES 解密失败: {str(e)}"
    else:
        response_data = {"error": error_msg} if error_msg else {}
    
    # 记录日志
    log = TestQueryDataLog(
        test_query_data_id=test_data.id,
        sys_code=sys_code,
        request_params=json.dumps(request_params, ensure_ascii=False),
        response_data=json.dumps(response_data, ensure_ascii=False),
        status=status,
        error_msg=error_msg,
        create_user=current_user.username
    )
    db.add(log)
    await db.commit()
    
    logger.info(f"[TEST_QUERY_DATA] 调用完成 - status={'成功' if status == 1 else '失败'}, 日志已保存")
    
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
            "sys_code": item.sys_code,
            "request_params": json.loads(item.request_params),
            "response_data": json.loads(item.response_data),
            "status": item.status,
            "error_msg": item.error_msg,
            "create_time": item.create_time,
            "create_user": item.create_user
        }
        result.append(item_dict)
    
    return success({"total": total, "items": result})


@router.get("/latest-log/{test_query_data_id}")
async def get_latest_test_query_data_log(
        test_query_data_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: SysUser = Depends(get_current_user),
):
    """
    获取指定测试数据的最新一条日志（当前用户）
    """
    # 查询当前用户对指定测试数据的最新日志
    q = (
        select(TestQueryDataLog)
        .where(
            TestQueryDataLog.test_query_data_id == test_query_data_id,
            TestQueryDataLog.create_user == current_user.username
        )
        .order_by(TestQueryDataLog.create_time.desc())
        .limit(1)
    )

    log = (await db.execute(q)).scalar_one_or_none()

    if not log:
        return success(None)

    # 转换字段为字典并返回
    result = {
        "id": log.id,
        "test_query_data_id": log.test_query_data_id,
        "sys_code": log.sys_code,
        "request_params": json.loads(log.request_params),
        "response_data": json.loads(log.response_data),
        "status": log.status,
        "error_msg": log.error_msg,
        "create_time": log.create_time,
        "create_user": log.create_user
    }

    return success(result)
