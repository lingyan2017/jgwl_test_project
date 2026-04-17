from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.session import get_db
from app.models.user import SysUser
from app.core.deps import get_current_user
from app.schemas.common import success
from app.api.v1.trial_calc import (
    Product, TrialParam, StageConfig, trial_calc, 
    get_summary, STAGE_PERCENTAGE, PERIOD_JUST_END
)

router = APIRouter()


from pydantic import BaseModel
from typing import Optional


class TrialCalculationRequest(BaseModel):
    amount: int  # 本金
    min_period: int  # 最小借款周期（天）
    stage_num: int = 1  # 分期数（默认1期）
    daily_interest_rate: int  # 日利率（万分之）
    daily_fee_rate: int  # 日费率（万分之）
    float_rate: int = 0  # 浮动费率（万分之）
    tax_rate: int  # GST税率（万分之，如1600表示16%）
    coupon_amount: int = 0  # 优惠券金额
    reduce_rate: float = 0  # 减免比例（0-1之间）


@router.post("/trial-calculate")
async def trial_calculate(
    request: TrialCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """
    试算接口 - 使用 trial_calc.py 中的 TrialParam 方法
    """
    # 构建产品配置
    product = Product(
        min_period=request.min_period,
        period=1,  # 日贷
        day_interest_rate=request.daily_interest_rate,
        day_fee_rate=request.daily_fee_rate + request.float_rate,  # 基础费率 + 浮动费率
        gst_fee_rate=request.tax_rate,
        stage_num=request.stage_num,
        period_cal_type=PERIOD_JUST_END,
    )
    
    # 构建试算参数
    trial_param = TrialParam(
        loan=request.amount,
        coupon_amount=request.coupon_amount,
        reduce_rate=request.reduce_rate,
        repay_order="s;t;i;p",  # 默认抵扣顺序：服务费→GST→利息→本金
        loan_date=date.today(),
    )
    
    # 如果是多期，构建分期配置（等比例分期）
    stage_configs = None
    if request.stage_num > 1:
        # 计算每期天数和比例
        sub_period = request.min_period // request.stage_num
        sub_percentage = 10000 // request.stage_num  # 等比例
        
        stage_configs = [
            StageConfig(sub_period=sub_period, sub_percentage=sub_percentage)
            for _ in range(request.stage_num)
        ]
    
    # 执行试算
    details = trial_calc(product, trial_param, stage_configs, STAGE_PERCENTAGE)
    
    # 获取汇总信息
    summary = get_summary(details)
    
    # 转换为前端需要的格式
    result = {
        "amount": summary.total_loan,
        "min_period": request.min_period,
        "stage_num": summary.total_stages,
        "total_fees": summary.total_amount,
        "total_interest": summary.total_interest,
        "total_service_fee": summary.total_service_fee,
        "total_gst": summary.total_gst,
        "total_reduced": summary.total_reduced,
        "total_actual_repay": summary.total_actual_repay,
        "stages": [
            {
                "stage_index": d.id,
                "stage_total": d.total,
                "stage_principal": d.amount,
                "stage_interest": d.interest,
                "stage_service_fee": d.service_fee,
                "stage_tax": d.gst,
                "service_fee_reduced": d.service_fee_reduced,
                "interest_reduced": d.interest_reduced,
                "tax_reduced": d.gst_reduced,
                "actual_payment": d.actual_repay,
                "per_period_days": d.stage_period,
                "repay_date": str(d.repay_date),
                "repay_day_offset": d.repay_day_offset,
            }
            for d in details
        ]
    }
    
    return success(result)


# 示例调用
if __name__ == "__main__":
    from datetime import date
    
    # 示例参数
    BASE_DATE = date(2026, 4, 16)
    
    # 产品配置
    p = Product(
        min_period=14,
        period=1,
        day_interest_rate=9,
        day_fee_rate=197,  # 103 + 94
        gst_fee_rate=1600,
        stage_num=1,
        period_cal_type=PERIOD_JUST_END,
    )
    
    # 试算参数
    t = TrialParam(
        loan=200,
        coupon_amount=0,
        reduce_rate=0,
        repay_order="s;t;i;p",
        loan_date=BASE_DATE,
    )
    
    # 执行试算
    details = trial_calc(p, t)
    summary = get_summary(details)
    
    print("\n试算结果：")
    print(f"放款金额: {summary.total_loan}")
    print(f"最小借款周期: {p.min_period}天")
    print(f"分期数: {summary.total_stages}期")
    print(f"总应还: {summary.total_amount}")
    print(f"总利息: {summary.total_interest}")
    print(f"总服务费: {summary.total_service_fee}")
    print(f"总GST: {summary.total_gst}")
    print(f"总减免: {summary.total_reduced}")
    print(f"实际总还款: {summary.total_actual_repay}")
    print("\n各期详细信息：")
    
    for d in details:
        print(f"\n第{d.id}期：")
        print(f"  账期天数: {d.stage_period}")
        print(f"  还款日期: {d.repay_date}")
        print(f"  总应还: {d.total}")
        print(f"  本金: {d.amount}")
        print(f"  利息: {d.interest}")
        print(f"  服务费: {d.service_fee}")
        print(f"  GST: {d.gst}")
        print(f"  减免服务费: {d.service_fee_reduced}")
        print(f"  减免利息: {d.interest_reduced}")
        print(f"  减免GST: {d.gst_reduced}")
        print(f"  实际应付款: {d.actual_repay}")