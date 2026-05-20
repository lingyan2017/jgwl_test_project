from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Literal, Optional
import httpx
import logging

from app.db.session import get_db
from app.models.user import SysUser
from app.core.deps import get_current_user
from app.schemas.common import success

router = APIRouter()
logger = logging.getLogger("app.payment_test")


class PaymentTestRequest(BaseModel):
    payment_type: Literal["放款", "还款"]
    payment_channel: Literal["stp", "opm"]
    payment_account: str
    url_type: str


@router.post("/test-payment")
async def test_payment(
    request: PaymentTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """
    STP/OPM测试支付接口
    """

    # 构建请求URL
    base_urls = {
        "stp": {
            "payout": "https://stp-api.example.com/payout",
            "balance": "https://stp-api.example.com/balance",
            "status": "https://stp-api.example.com/status",
            "cep": "https://stp-api.example.com/cep",
        },
        "opm": {
            "payout": "https://opm-api.example.com/payout",
            "balance": "https://opm-api.example.com/balance",
            "status": "https://opm-api.example.com/status",
            "cep": "https://opm-api.example.com/cep",
            "trackstatus": "https://opm-api.example.com/trackstatus",
        }
    }

    # 获取对应的URL
    url = base_urls.get(request.payment_channel, {}).get(request.url_type)
    if not url:
        raise HTTPException(status_code=400, detail="无效的支付通道或URL类型")

    # 构建请求参数
    request_params = {
        "payment_type": request.payment_type,
        "payment_channel": request.payment_channel,
        "payment_account": request.payment_account,
        "url_type": request.url_type,
        "timestamp": "2026-05-20T00:00:00Z",
    }

    # 模拟请求（实际应该调用真实API）
    try:
        logger.info(f"Testing payment: {request_params}")

        # 这里应该调用真实的支付API
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(url, json=request_params, timeout=30.0)
        #     response_data = response.json()

        # 模拟响应
        response_data = {
            "code": 0,
            "message": "success",
            "data": {
                "transaction_id": "TXN123456789",
                "status": "success",
                "amount": 1000,
                "currency": "MXN",
                "account": request.payment_account,
                "timestamp": "2026-05-20T00:00:00Z"
            }
        }

        return success({
            "request_params": request_params,
            "response_data": response_data,
            "url": url
        })

    except Exception as e:
        logger.error(f"Payment test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"支付测试失败: {str(e)}")
