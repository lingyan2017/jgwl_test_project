<template>
  <div class="trial-calculator">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试算测试</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="150px" style="max-width: 800px;">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="本金" required>
              <el-input v-model.number="form.amount" type="number" placeholder="请输入本金" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最小借款周期（天）" required>
              <el-input v-model.number="form.min_period" type="number" placeholder="请输入借款周期" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分期数" required>
              <el-input v-model.number="form.stage_num" type="number" placeholder="请输入分期数" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日利率" required>
              <el-input v-model.number="form.daily_interest_rate" type="number" placeholder="请输入日利率" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="日费率" required>
              <el-input v-model.number="form.daily_fee_rate" type="number" placeholder="请输入日费率" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="浮动费率">
              <el-input v-model.number="form.float_rate" type="number" placeholder="请输入浮动费率" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="税率（百分比）" required>
              <el-input v-model.number="form.tax_rate" type="number" placeholder="请输入税率" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优惠券金额">
              <el-input v-model.number="form.coupon_amount" type="number" placeholder="请输入优惠券金额" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="减免比例（0-1之间）">
              <el-input v-model.number="form.reduce_rate" type="number" placeholder="请输入减免比例" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="calculate" :loading="loading">开始试算</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 结果展示 -->
    <el-card v-if="result" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>试算结果</span>
        </div>
      </template>
      
      <div class="result-section">
        <h3 style="margin-top: 20px;">总体信息</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="放款金额">{{ result.amount }}</el-descriptions-item>
          <el-descriptions-item label="最小借款周期">{{ result.min_period }}天</el-descriptions-item>
          <el-descriptions-item label="分期数">{{ result.stage_num }}期</el-descriptions-item>
          <el-descriptions-item label="总应还">{{ result.total_fees }}</el-descriptions-item>
          <el-descriptions-item label="总利息">{{ result.total_interest }}</el-descriptions-item>
          <el-descriptions-item label="总服务费">{{ result.total_service_fee }}</el-descriptions-item>
          <el-descriptions-item label="总GST">{{ result.total_gst }}</el-descriptions-item>
          <el-descriptions-item label="总减免">{{ result.total_reduced }}</el-descriptions-item>
          <el-descriptions-item label="实际总还款">{{ result.total_actual_repay }}</el-descriptions-item>
        </el-descriptions>
        
        <h3 style="margin-top: 20px;">各期明细</h3>
        <el-table :data="result.stages" style="width: 100%" border>
          <el-table-column prop="stage_index" label="期数" width="80" />
          <el-table-column prop="stage_total" label="总应还" width="100" />
          <el-table-column prop="stage_principal" label="本金" width="100" />
          <el-table-column prop="stage_interest" label="利息" width="100" />
          <el-table-column prop="stage_service_fee" label="服务费" width="100" />
          <el-table-column prop="stage_tax" label="GST" width="100" />
          <el-table-column prop="service_fee_reduced" label="减免服务费" width="120" />
          <el-table-column prop="interest_reduced" label="减免利息" width="120" />
          <el-table-column prop="tax_reduced" label="减免GST" width="120" />
          <el-table-column prop="actual_payment" label="实际应付款" width="120" />
          <el-table-column prop="per_period_days" label="期数天数" width="100" />
          <el-table-column prop="repay_date" label="还款日期" width="120" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { trialCalculate } from '@/api/trial';

const loading = ref(false);

const form = reactive({
  amount: 200, // 本金
  min_period: 14, // 最小借款周期（天）
  stage_num: 1, // 分期数（默认1期）
  daily_interest_rate: 9, // 日利率（万分之）
  daily_fee_rate: 103, // 日费率（万分之）
  float_rate: 94, // 浮动费率（万分之）
  tax_rate: 1600, // GST税率（万分之，1600=16%）
  coupon_amount: 0, // 优惠券金额
  reduce_rate: 0 // 减免比例（0-1之间）
});

const result = ref<any>(null);

const calculate = async () => {
  if (!form.amount || !form.min_period || !form.stage_num || 
      !form.daily_interest_rate || !form.daily_fee_rate || !form.tax_rate) {
    ElMessage.error('请填写必填项');
    return;
  }
  
  if (form.reduce_rate < 0 || form.reduce_rate > 1) {
    ElMessage.error('减免比例应在0-1之间');
    return;
  }
  
  loading.value = true;
  try {
    const response = await trialCalculate(form);
    result.value = response.data;
    ElMessage.success('试算完成');
  } catch (error) {
    ElMessage.error('试算失败: ' + (error as any).toString());
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.amount = 200;
  form.min_period = 14;
  form.stage_num = 1;
  form.daily_interest_rate = 9;
  form.daily_fee_rate = 103;
  form.float_rate = 94;
  form.tax_rate = 1600;
  form.coupon_amount = 0;
  form.reduce_rate = 0;
  result.value = null;
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-section {
  padding: 20px 0;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>