#!/usr/bin/env python3
"""
贷款试算计算器
对应 Go 实现：common/pkg/core/trial.go
"""
import math
from dataclasses import dataclass
from typing import List, Optional
from datetime import date, timedelta

# ─── 常量 ────────────────────────────────────────────────────────────────────
PRODUCT_FEE_BASE = 10_000  # 万分之基数（所有费率单位均为万分之）

# 还款日计算模式
PERIOD_JUST_END      = "just_end"       # 只计尾：放款日不算，到期日算
PERIOD_START_AND_END = "start_and_end"  # 计头计尾：首尾都算（天数-1）

# 付息方式
CHARGE_AFTER    = "after"     # 后置：到期还息
CHARGE_HEAD_CUT = "head_cut"  # 前置：放款时预扣（砍头息）

# 分期方式
STAGE_PERCENTAGE = "percentage"  # 按比例
STAGE_AMOUNT     = "amount"      # 按固定金额（-1 表示最后一期差值）


# ─── 数据结构 ─────────────────────────────────────────────────────────────────

@dataclass
class Product:
    """产品配置"""
    min_period:           int          # 总贷款天数（如 14）
    period:               int          # 周期乘数（日贷=1，周贷=7，月贷=30）
    day_interest_rate:    int          # 日利率（万分之，如  9  = 0.09%/天）
    day_fee_rate:         int          # 日服务费率（万分之，如 197 = 1.97%/天）
    gst_fee_rate:         int          # GST 税率（万分之，如 1600 = 16%）
    stage_num:            int  = 1     # 分期数（1=单期）
    charge_interest_type: str  = CHARGE_AFTER
    charge_fee_type:      str  = CHARGE_AFTER
    period_cal_type:      str  = PERIOD_JUST_END


@dataclass
class StageConfig:
    """分期配置"""
    sub_period:     int           # 本期账期天数
    sub_percentage: int = 10_000  # 本期本金占比（万分之，10000=100%）
    sub_amount:     int = 0       # 按金额分期时使用（-1=最后一期差值）


@dataclass
class TrialParam:
    """试算请求参数"""
    loan:          int            # 借款金额
    coupon_amount: int   = 0      # 优惠券金额（绝对值抵扣）
    reduce_rate:   float = 0.0    # 折扣比例（0~1，如 0.5=减免50%息费）
    repay_order:   str   = ""     # 优惠券抵扣顺序，如 "s;t;i;p"（服务费→GST→利息→本金）
    loan_date: Optional[date] = None  # 放款日（None=今天）


@dataclass
class StageDetail:
    """单期还款明细"""
    id:              int    # 期数（从 1 开始）
    stage_num:       int    # 总期数
    stage_period:    int    # 本期账期天数
    repay_day_offset: int   # 距放款日天数
    repay_date:      date   # 还款日期
    total:           int    # 本期应还总额（未扣减免）
    amount:          int    # 本金
    interest:        int    # 利息
    gst:             int    # GST
    service_fee:     int    # 服务费
    # 砍头息（预扣金额）
    interest_prepaid:    int = 0
    fee_prepaid:         int = 0
    gst_prepaid:         int = 0
    # 优惠券减免
    amount_reduced:      int = 0
    interest_reduced:    int = 0
    gst_reduced:         int = 0
    service_fee_reduced: int = 0

    @property
    def total_reduced(self) -> int:
        return (self.amount_reduced + self.interest_reduced
                + self.gst_reduced + self.service_fee_reduced)

    @property
    def actual_repay(self) -> int:
        """实际还款（扣优惠后）"""
        return self.total - self.total_reduced


@dataclass
class TrialSummary:
    """汇总数据"""
    total_stages:       int
    total_loan:         int   # 总本金
    total_interest:     int   # 总利息
    total_service_fee:  int   # 总服务费
    total_gst:          int   # 总 GST
    total_amount:       int   # 总应还
    total_reduced:      int   # 总减免
    total_actual_repay: int   # 实际总还款


# ─── 核心计算函数 ─────────────────────────────────────────────────────────────

def _float_rate(*args: float) -> float:
    """浮点连乘，用于单期向上取整计算"""
    r = 1.0
    for a in args:
        r *= a
    return r


def _int_rate(*args: int) -> int:
    """
    整数连乘后 floor 除以 PRODUCT_FEE_BASE
    对应 Go Rate() 函数
    """
    r = 1
    for a in args:
        r *= a
    return r // PRODUCT_FEE_BASE


# ── 全局总额计算 ──────────────────────────────────────────────────────────────

def calc_total_interest(p: Product, loan: int) -> int:
    """
    总利息
    单期用 float × ceil（避免截断误差），多期用 int × floor（差值由最后一期补足）

    公式：loan × MinPeriod × Period × DayInterestRate / 10000
    示例：200 × 14 × 1 × 9 / 10000 = 2.52 → ceil = 3
    """
    if p.stage_num > 1:
        # 多期：floor（整数除法）
        return _int_rate(loan, p.min_period, p.period, p.day_interest_rate)
    # 单期：ceil
    r = _float_rate(p.min_period, p.period, p.day_interest_rate, 1.0 / PRODUCT_FEE_BASE)
    return math.ceil(r * loan)


def calc_total_gst(p: Product, loan: int) -> int:
    """
    总 GST
    单期用 ceil，多期用 floor

    公式：loan × MinPeriod × Period × (DayInterestRate+DayFeeRate) × GstFeeRate / 10000²
    示例：200 × 14 × 1 × 206 × 1600 / 10000 / 10000 = 9.2288 → ceil = 10
    """
    if p.stage_num > 1:
        g = _int_rate(loan, p.min_period, p.period,
                      p.day_fee_rate + p.day_interest_rate, p.gst_fee_rate)
        return g // PRODUCT_FEE_BASE
    r = _float_rate(p.min_period, p.period,
                    p.day_fee_rate + p.day_interest_rate,
                    p.gst_fee_rate,
                    1.0 / PRODUCT_FEE_BASE,
                    1.0 / PRODUCT_FEE_BASE)
    return math.ceil(r * loan)


def calc_total_amount(p: Product, loan: int) -> int:
    """
    总应还 = loan × rate（向上取整）

    后置付息：rate = 1 + 利率 + 服务费率 + GST率
    前置付息：rate = 1 / (1 - 利率 - 服务费率 - GST率)

    示例（后置）：
      ir = 14×1×9/10000   = 0.0126
      sr = 14×1×197/10000 = 0.2758
      gr = (ir+sr)×1600/10000 = 0.046144
      rate = 1.334544
      总应还 = ceil(200 × 1.334544) = ceil(266.9088) = 267
    """
    ir = p.min_period * p.period * p.day_interest_rate / PRODUCT_FEE_BASE
    sr = p.min_period * p.period * p.day_fee_rate      / PRODUCT_FEE_BASE
    gr = (ir + sr) * p.gst_fee_rate / PRODUCT_FEE_BASE

    if p.charge_interest_type == CHARGE_HEAD_CUT and p.charge_fee_type == CHARGE_HEAD_CUT:
        rate = 1.0 / (1.0 - ir - sr - gr)
    else:
        rate = 1.0 + ir + sr + gr

    return math.ceil(loan * rate)


def calc_total_service_fee(p: Product, loan: int) -> int:
    """
    总服务费 = 总应还 - 本金 - 总利息 - 总GST
    示例：267 - 200 - 3 - 10 = 54
    """
    ti = calc_total_interest(p, loan)
    tg = calc_total_gst(p, loan)
    ta = calc_total_amount(p, loan)
    if p.charge_interest_type == CHARGE_HEAD_CUT and p.charge_fee_type == CHARGE_HEAD_CUT:
        ti = calc_total_interest(p, ta)
        tg = calc_total_gst(p, ta)
    return ta - loan - ti - tg


# ── 每期计算 ──────────────────────────────────────────────────────────────────

def calc_sub_loan(idx: int, loan: int,
                  configs: List[StageConfig], method: str) -> int:
    """
    当期本金
    - 非最后一期（按比例）：loan × SubPercentage / 10000（floor）
    - 最后一期：差值 = loan - 前几期之和
    """
    if method == STAGE_AMOUNT:
        val = configs[idx].sub_amount
        if val == -1:
            val = loan - sum(configs[i].sub_amount for i in range(idx))
        return val
    # 按比例
    if idx < len(configs) - 1:
        return _int_rate(loan, configs[idx].sub_percentage)
    before = sum(calc_sub_loan(i, loan, configs, method) for i in range(idx))
    return loan - before


def calc_stage_interest(p: Product, idx: int, loan: int, s_loan: int,
                        interest_before: int, configs: List[StageConfig]) -> int:
    """
    当期利息
    - 非最后一期：s_loan × MinPeriod × Period × DayInterestRate / 10000（floor）
    - 最后一期：  差值 = TotalInterest - interestBefore（吸收舍入误差）
    """
    if idx < len(configs) - 1:
        return _int_rate(s_loan, p.min_period, p.period, p.day_interest_rate)
    return calc_total_interest(p, loan) - interest_before


def calc_stage_gst(p: Product, idx: int, loan: int, s_loan: int,
                   gst_before: int, configs: List[StageConfig]) -> int:
    """
    当期 GST
    - 非最后一期：s_loan × MinPeriod × Period × (FeeRate+InterestRate) × GstRate / 10000²（floor）
    - 最后一期：  差值 = TotalGst - gstBefore
    """
    if idx < len(configs) - 1:
        g = _int_rate(s_loan, p.min_period, p.period,
                      p.day_fee_rate + p.day_interest_rate, p.gst_fee_rate)
        return g // PRODUCT_FEE_BASE
    return calc_total_gst(p, loan) - gst_before


def calc_sub_total(p: Product, idx: int, loan: int, total_before: int,
                   configs: List[StageConfig], method: str) -> int:
    """
    当期总应还
    - 非最后一期：ceil(TotalAmount × SubPercentage / 10000)
    - 最后一期：  差值 = TotalAmount - totalBefore
    """
    if method == STAGE_AMOUNT:
        s_l = configs[idx].sub_amount
        if s_l == -1:
            s_l = loan - sum(configs[i].sub_amount for i in range(idx))
        ratio = s_l / loan
    else:
        ratio = configs[idx].sub_percentage / PRODUCT_FEE_BASE

    if idx < len(configs) - 1:
        return math.ceil(calc_total_amount(p, loan) * ratio)
    return calc_total_amount(p, loan) - total_before


def calc_stage_service_fee(p: Product, idx: int, loan: int, s_loan: int,
                           fee_before: int,
                           configs: List[StageConfig], method: str) -> int:
    """
    当期服务费
    - 非最后一期：SubTotal - subLoan - interest - gst
    - 最后一期：  差值 = TotalServiceFee - serviceFeeBefore
    """
    if idx < len(configs) - 1:
        st = calc_sub_total(p, idx, loan, 0, configs, method)
        si = calc_stage_interest(p, idx, loan, s_loan, 0, configs)
        sg = calc_stage_gst(p, idx, loan, s_loan, 0, configs)
        return st - s_loan - si - sg
    return calc_total_service_fee(p, loan) - fee_before


# ─── 主试算函数 ───────────────────────────────────────────────────────────────

def trial_calc(
        p: Product,
        trial: TrialParam,
        stage_configs: Optional[List[StageConfig]] = None,
        stage_method: str = STAGE_PERCENTAGE,
) -> List[StageDetail]:
    """
    贷款试算主函数，返回每期还款明细列表

    Args:
        p:             产品配置
        trial:         试算参数（借款金额、优惠券等）
        stage_configs: 分期配置列表（None=单期产品，自动构造）
        stage_method:  分期方式（STAGE_PERCENTAGE / STAGE_AMOUNT）

    Returns:
        List[StageDetail]: 每期明细
    """
    loan_date = trial.loan_date or date.today()

    # 无分期配置 → 自动构造单期（100% 本金，全部账期）
    if not stage_configs:
        stage_configs = [StageConfig(sub_period=p.min_period, sub_percentage=PRODUCT_FEE_BASE)]
        stage_method = STAGE_PERCENTAGE

    coupon          = trial.coupon_amount
    interest_before = gst_before = total_before = fee_before = 0
    act_period      = 0
    details: List[StageDetail] = []

    for idx, sub in enumerate(stage_configs):
        n = len(stage_configs)

        # ── Step 1：计算各期费用 ──────────────────────────────────────────────
        s_loan  = calc_sub_loan(idx, trial.loan, stage_configs, stage_method)
        s_int   = calc_stage_interest(p, idx, trial.loan, s_loan, interest_before, stage_configs)
        s_gst   = calc_stage_gst(p, idx, trial.loan, s_loan, gst_before, stage_configs)
        s_total = calc_sub_total(p, idx, trial.loan, total_before, stage_configs, stage_method)
        s_fee   = calc_stage_service_fee(p, idx, trial.loan, s_loan, fee_before, stage_configs, stage_method)

        # 前 N-1 期累加（最后一期不累加，用差值兜底）
        if idx < n - 1:
            interest_before += s_int
            gst_before      += s_gst
            total_before    += s_total
            fee_before      += s_fee

        # ── Step 2：还款日 ────────────────────────────────────────────────────
        act_period += sub.sub_period
        if idx == 0 and p.period_cal_type == PERIOD_START_AND_END:
            act_period -= 1      # 计头计尾模式：第一期减 1 天

        offset     = act_period * p.period
        repay_date = loan_date + timedelta(days=offset)

        # ── Step 3：砍头息（前置付息预扣）────────────────────────────────────
        int_prepaid = fee_prepaid = gst_prepaid = 0
        if p.charge_interest_type == CHARGE_HEAD_CUT:
            int_prepaid = s_int
            gst_prepaid = s_gst
            s_int = s_gst = 0
        if p.charge_fee_type == CHARGE_HEAD_CUT:
            fee_prepaid = s_fee

        # ── Step 4：优惠券减免 ────────────────────────────────────────────────
        amt_red = int_red = gst_red = fee_red = 0

        if trial.reduce_rate > 0:
            # 折扣模式：按比例减免息费（多期只第一期生效）
            if n == 1 or idx == 0:
                dr = trial.reduce_rate
                int_red  = math.ceil(s_int * dr)
                gst_red  = math.ceil(s_gst * dr)
                fee_red  = math.ceil((s_int + s_fee + s_gst) * dr) - int_red - gst_red

        elif coupon > 0 and trial.repay_order:
            # 按序抵扣模式（依 repay_order 顺序，券额用尽即止）
            for o in trial.repay_order.split(";"):
                if o == "s":             # 服务费
                    if coupon >= s_fee:   coupon -= s_fee; fee_red = s_fee
                    else:                fee_red = coupon; coupon = 0; break
                elif o == "t":           # GST
                    if coupon >= s_gst:   coupon -= s_gst; gst_red = s_gst
                    else:                gst_red = coupon; coupon = 0; break
                elif o == "i":           # 利息
                    if coupon >= s_int:   coupon -= s_int; int_red = s_int
                    else:                int_red = coupon; coupon = 0; break
                elif o == "p":           # 本金
                    if coupon >= s_loan:  coupon -= s_loan; amt_red = s_loan
                    else:                amt_red = coupon; coupon = 0; break
            # 多期贷前优惠券只在第一期生效，不结余到第二期
            if idx == 0 and n > 1:
                coupon = 0

        details.append(StageDetail(
            id=idx + 1, stage_num=n, stage_period=sub.sub_period,
            repay_day_offset=offset, repay_date=repay_date,
            total=s_total, amount=s_loan, interest=s_int,
            gst=s_gst, service_fee=s_fee,
            interest_prepaid=int_prepaid,
            fee_prepaid=fee_prepaid,
            gst_prepaid=gst_prepaid,
            amount_reduced=amt_red, interest_reduced=int_red,
            gst_reduced=gst_red, service_fee_reduced=fee_red,
        ))

    return details


# ─── 汇总 & 输出 ──────────────────────────────────────────────────────────────

def get_summary(details: List[StageDetail]) -> TrialSummary:
    return TrialSummary(
        total_stages       = len(details),
        total_loan         = sum(d.amount      for d in details),
        total_interest     = sum(d.interest    for d in details),
        total_service_fee  = sum(d.service_fee for d in details),
        total_gst          = sum(d.gst         for d in details),
        total_amount       = sum(d.total       for d in details),
        total_reduced      = sum(d.total_reduced  for d in details),
        total_actual_repay = sum(d.actual_repay   for d in details),
    )


def print_result(details: List[StageDetail], title: str = "试算结果"):
    W = 96
    DIV = "─" * W
    print(f"\n{'═' * W}")
    print(f"  {title}")
    print(f"{'═' * W}")
    print(f"  {'期':>2}  {'账期':>4}  {'本金':>8}  {'利息':>6}  {'服务费':>8}  "
          f"{'GST':>6}  {'当期总额':>8}  {'优惠减免':>8}  {'实际还款':>8}  "
          f"{'还款日':>12}  {'天数':>4}")
    print(f"  {DIV}")
    for d in details:
        print(f"  {d.id:>2}  {d.stage_period:>4}  {d.amount:>8}  {d.interest:>6}  "
              f"{d.service_fee:>8}  {d.gst:>6}  {d.total:>8}  "
              f"{d.total_reduced:>8}  {d.actual_repay:>8}  "
              f"{str(d.repay_date):>12}  {d.repay_day_offset:>4}")

    s = get_summary(details)
    print(f"  {DIV}")
    print(f"  汇总")
    print(f"  {'─' * 50}")
    print(f"  {'总期数':<10}: {s.total_stages}")
    print(f"  {'总本金':<10}: {s.total_loan}")
    print(f"  {'总利息':<10}: {s.total_interest}")
    print(f"  {'总服务费':<10}: {s.total_service_fee}")
    print(f"  {'总 GST':<10}: {s.total_gst}")
    chk = s.total_loan + s.total_interest + s.total_service_fee + s.total_gst
    print(f"  {'总应还':<10}: {s.total_amount}  "
          f"（{s.total_loan}+{s.total_interest}+{s.total_service_fee}+{s.total_gst} = {chk}）")
    if s.total_reduced:
        print(f"  {'总减免':<10}: {s.total_reduced}")
        print(f"  {'实际总还款':<10}: {s.total_actual_repay}")
    print(f"{'═' * W}\n")


# ─── 示例运行 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    BASE_DATE = date(2026, 4, 16)

    # 产品基础配置（题目参数）
    p1 = Product(
        min_period=14,
        period=1,
        day_interest_rate=9,
        day_fee_rate=197,          # 103 + float_rate(94)
        gst_fee_rate=1600,
        stage_num=1,
        period_cal_type=PERIOD_JUST_END,
    )

    # ── 示例1：单期，无优惠 ──────────────────────────────────────────────────
    t1 = TrialParam(loan=200, loan_date=BASE_DATE)
    print_result(trial_calc(p1, t1),
                 "示例1：单期  loan=200  14天  无优惠")

    # ── 示例2：单期 + 优惠券（按序 服务费→GST→利息→本金）───────────────────
    # coupon=20，s=54 > 20，故只能抵扣 s 中的 20，remaining=0
    t2 = TrialParam(loan=200, coupon_amount=20,
                    repay_order="s;t;i;p", loan_date=BASE_DATE)
    print_result(trial_calc(p1, t2),
                 "示例2：单期  coupon=20  抵扣顺序 s→t→i→p")

    # ── 示例3：单期 + 折扣 50% ──────────────────────────────────────────────
    t3 = TrialParam(loan=200, reduce_rate=0.5, loan_date=BASE_DATE)
    print_result(trial_calc(p1, t3),
                 "示例3：单期  reduce_rate=0.5（5折减免息费）")

    # ── 示例4：2期 按比例分期（各 1/3）──────────────────────────────────────
    # min_period = 14×3 = 42（总天数，也是利息计算基数）
    p3 = Product(
        min_period=14, period=1,
        day_interest_rate=9, day_fee_rate=197, gst_fee_rate=1600,
        stage_num=2, period_cal_type=PERIOD_JUST_END,
    )
    stages3 = [
        StageConfig(sub_period=7, sub_percentage=5000),  # 50%
        StageConfig(sub_period=7, sub_percentage=5000),  # 最后一期，比例不参与计算（用差值）
    ]
    t4 = TrialParam(loan=200, loan_date=BASE_DATE)
    print_result(trial_calc(p3, t4, stages3, STAGE_PERCENTAGE),
                 "示例4：3期等额  loan=200  每期14天  无优惠")

    # ── 示例5：3期 + 优惠券（只第一期生效，不结余到第二期）─────────────────
    t5 = TrialParam(loan=200, coupon_amount=30,
                    repay_order="s;t;i;p", loan_date=BASE_DATE)
    print_result(trial_calc(p3, t5, stages3, STAGE_PERCENTAGE),
                 "示例5：3期  coupon=30（贷前券，只抵第一期，不结余）")
