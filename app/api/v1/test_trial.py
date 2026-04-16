import math
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import SysUser
from app.core.deps import get_current_user
from app.schemas.common import success

router = APIRouter()


def calculate_all_stages(
        amount,  # 本金
        min_period,  # 最小借款周期（天）
        stage_num,  # 分期数
        daily_interest_rate,  # 日利率（万分之）
        daily_fee_rate,  # 日费率（万分之）
        tax_rate,  # 税费率（百分比，如16表示16%）
        coupon_amount,  # 优惠券金额
        reduce_rate  # 减免比例（0-1之间）
):
    """
    计算分期贷款所有期数的费用，所有结果向上取整
    """
    # 计算每期天数（向上取整）
    per_period_days = math.ceil(min_period / stage_num)

    # 计算每期本金（向上取整）
    per_stage_principal = math.ceil(amount / stage_num)

    # 初始化总费用和结果列表
    total_fees = 0
    stages_result = []

    # 计算所有期数的费用
    for stage_index in range(stage_num):
        # 计算当期利息（向上取整）
        interestRate = min_period * 1 * daily_interest_rate / 10000
        # stage_interest = math.ceil(per_stage_principal * (daily_interest_rate / 10000) * min_period)

        # 计算当期服务费（向上取整）
        serviceRate = min_period * 1 * daily_fee_rate / 10000
        # stage_service_fee = math.ceil(per_stage_principal * (daily_fee_rate / 10000) * min_period)

        # # 计算当期税费（向上取整）
        gstRate = (interestRate + serviceRate) * tax_rate / 10000
        # stage_tax = math.ceil((stage_interest + stage_service_fee) * (tax_rate / 10000))

        # 计算当期总应还（向上取整）
        stage_interest = math.ceil(amount * interestRate)
        stage_service_fee = math.ceil(amount * serviceRate)
        stage_total = math.ceil(per_stage_principal * (1.0 + interestRate + serviceRate + gstRate))

        stage_tax = stage_total - stage_interest - stage_service_fee

        # 计算优惠券减免（只在第一期处理）
        service_fee_reduced = 0
        interest_reduced = 0
        tax_reduced = 0

        if stage_index == 0 and reduce_rate > 0 and reduce_rate <= 1:
            # 计算总费用（利息+服务费+税费）
            current_fees = stage_interest + stage_service_fee + stage_tax
            # 计算减免金额（向上取整）
            discount_amount = math.ceil(current_fees * reduce_rate)

            # 按照顺序减免：先减免服务费，再减免利息，最后减免税费
            service_fee_reduced = min(stage_service_fee, discount_amount)
            remaining_discount = discount_amount - service_fee_reduced

            if remaining_discount > 0:
                interest_reduced = min(stage_interest, remaining_discount)
                remaining_discount -= interest_reduced

            if remaining_discount > 0:
                tax_reduced = min(stage_tax, remaining_discount)

        # 构建当期结果
        stage_result = {
            "stage_index": stage_index + 1,
            "stage_total": stage_total,
            "stage_principal": per_stage_principal,
            "stage_interest": stage_interest,
            "stage_service_fee": stage_service_fee,
            "stage_tax": stage_tax,
            "service_fee_reduced": service_fee_reduced,
            "interest_reduced": interest_reduced,
            "tax_reduced": tax_reduced,
            "actual_payment": max(0, stage_total - service_fee_reduced - interest_reduced - tax_reduced),
            "per_period_days": per_period_days
        }

        # 添加到结果列表
        stages_result.append(stage_result)

        # 累计总费用
        total_fees += stage_total

    # 构建总结果
    total_result = {
        "amount": amount,
        "min_period": min_period,
        "stage_num": stage_num,
        "total_fees": total_fees,
        "stages": stages_result
    }

    return total_result


from pydantic import BaseModel
from typing import Optional


class TrialCalculationRequest(BaseModel):
    amount: float  # 本金
    min_period: int  # 最小借款周期（天）
    stage_num: int  # 分期数
    daily_interest_rate: float  # 日利率（万分之）
    daily_fee_rate: float  # 日费率（万分之）
    float_rate: float = 0  # 浮动费率（万分之）
    tax_rate: float  # 税费率（百分比，如16表示16%）
    coupon_amount: float = 0  # 优惠券金额
    reduce_rate: float = 0  # 减免比例（0-1之间）


@router.post("/trial-calculate")
async def trial_calculate(
    request: TrialCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """
    试算接口 - 计算分期贷款所有期数的费用
    """
    result = calculate_all_stages(
        request.amount,
        request.min_period,
        request.stage_num,
        request.daily_interest_rate,
        request.daily_fee_rate + request.float_rate,  # 日费率 = 基础费率 + 浮动费率
        request.tax_rate,
        request.coupon_amount,
        request.reduce_rate
    )
    
    return success(result)


# 示例调用
if __name__ == "__main__":
    # 示例参数
    amount = 200  # 本金
    min_period = 14  # 最小借款周期14天
    stage_num = 2  # 分2期
    daily_interest_rate = 9  #
    float_rate = 94  # 浮动费率
    daily_fee_rate = 103  # 日费率
    tax_rate = 1600  # 税费率
    coupon_amount = 0  # 优惠券金额500
    reduce_rate = 0  # 减免比例50%

    # 计算并打印结果
    result = calculate_all_stages(
        amount,
        min_period,
        stage_num,
        daily_interest_rate,
        daily_fee_rate + float_rate,
        tax_rate,
        coupon_amount,
        reduce_rate
    )

    print("分期费用计算结果（向上取整）：")
    print(f"放款金额: {result['amount']}")
    print(f"最小借款周期: {result['min_period']}天")
    print(f"分期数: {result['stage_num']}期")
    print(f"总费用: {result['total_fees']}")
    print("\n各期详细信息：")

    for stage in result['stages']:
        print(f"\n第{stage['stage_index']}期：")
        print(f"  总应还: {stage['stage_total']}")
        print(f"  本金: {stage['stage_principal']}")
        print(f"  利息: {stage['stage_interest']}")
        print(f"  服务费: {stage['stage_service_fee']}")
        print(f"  税费: {stage['stage_tax']}")
        print(f"  减免服务费: {stage['service_fee_reduced']}")
        print(f"  减免利息: {stage['interest_reduced']}")
        print(f"  减免税费: {stage['tax_reduced']}")
        print(f"  实际应付款: {stage['actual_payment']}")
        print(f"  期数天数: {stage['per_period_days']}天")