<template>
  <div class="payment-test">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>STP/OPM 测试支付</span>
        </div>
      </template>

      <el-form :model="form" label-width="130px" style="max-width: 600px;">
        <el-form-item label="支付方式" required>
          <el-radio-group v-model="form.payment_type">
            <el-radio value="放款">放款</el-radio>
            <el-radio value="还款">还款</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="支付通道" required>
          <el-radio-group v-model="form.payment_channel" @change="onChannelChange">
            <el-radio value="stp">STP</el-radio>
            <el-radio value="opm">OPM</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="支付账号" required>
          <el-select v-model="form.payment_account" placeholder="请选择支付账号" style="width: 100%;">
            <el-option
              v-for="item in accountOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="支付URL类型" required>
          <el-select v-model="form.url_type" placeholder="请选择URL类型" style="width: 100%;">
            <el-option
              v-for="item in urlTypeOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitRequest" :loading="loading">确认请求</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 响应结果弹窗 -->
    <el-dialog v-model="dialogVisible" title="请求结果" width="700px" top="10vh">
      <div class="dialog-content">
        <h4>请求参数</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="支付方式">{{ resultData.request_params?.payment_type }}</el-descriptions-item>
          <el-descriptions-item label="支付通道">{{ resultData.request_params?.payment_channel?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="支付账号">{{ resultData.request_params?.payment_account }}</el-descriptions-item>
          <el-descriptions-item label="URL类型">{{ resultData.request_params?.url_type }}</el-descriptions-item>
          <el-descriptions-item label="请求URL" :span="2">{{ resultData.url }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px;">响应结果</h4>
        <pre class="response-json">{{ formatJson(resultData.response_data) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { testPayment } from '@/api/paymentTest';

const loading = ref(false);
const dialogVisible = ref(false);
const resultData = ref<any>({});

const form = reactive({
  payment_type: '放款',
  payment_channel: 'stp',
  payment_account: '',
  url_type: '',
});

const accountMap: Record<string, string[]> = {
  opm: ['Tikin', 'A47', 'Ekm', 'CaryWorld'],
  stp: ['COMERCIA47', 'TIKIN1', 'YUNDS', 'YOONA_TECH'],
};

const urlTypeMap: Record<string, string[]> = {
  opm: ['payout', 'balance', 'status', 'cep', 'trackstatus'],
  stp: ['payout', 'balance', 'status', 'cep'],
};

const accountOptions = computed(() => accountMap[form.payment_channel] || []);
const urlTypeOptions = computed(() => urlTypeMap[form.payment_channel] || []);

const onChannelChange = () => {
  form.payment_account = '';
  form.url_type = '';
};

const formatJson = (data: any) => {
  if (!data) return '';
  return JSON.stringify(data, null, 2);
};

const submitRequest = async () => {
  if (!form.payment_type || !form.payment_channel || !form.payment_account || !form.url_type) {
    ElMessage.error('请填写所有必填项');
    return;
  }

  loading.value = true;
  try {
    const response = await testPayment(form);
    resultData.value = response.data;
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error('请求失败: ' + (error as any).toString());
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.payment_type = '放款';
  form.payment_channel = 'stp';
  form.payment_account = '';
  form.url_type = '';
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.response-json {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
