<template>
  <div class="system-config-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置项管理</span>
          <el-button type="primary" @click="openDialog()">新增</el-button>
        </div>
      </template>

      <!-- 查询条件 -->
      <el-form :inline="true" :model="query" class="mb-4">
        <el-form-item label="配置项名称">
          <el-input v-model="query.item_name" placeholder="请输入配置项名称" style="width: 200px" clearable />
        </el-form-item>
        <el-form-item label="系统平台">
          <el-input v-model="query.sys_code" placeholder="请输入系统平台" style="width: 200px" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 列表 -->
      <el-table :data="tableData" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="item_name" label="配置项名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="item_type" label="数据类型" width="100">
          <template #default="{ row }">
            {{ itemTypeLabel(row.item_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="item_value" label="配置值" min-width="200" show-overflow-tooltip />
        <el-table-column prop="version" label="版本" width="70" />
        <el-table-column prop="weight" label="权重" width="70" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sys_code" label="系统平台" width="110" />
        <el-table-column prop="online_time" label="上线时间" width="170">
          <template #default="{ row }">
            {{ formatTimestamp(row.online_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="offline_time" label="下线时间" width="170">
          <template #default="{ row }">
            {{ formatTimestamp(row.offline_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="ctime" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatTimestamp(row.ctime) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" text @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑配置项' : '新增配置项'" width="650px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="配置项名称" required>
          <el-input v-model="form.item_name" placeholder="请输入配置项名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="数据类型" required>
          <el-select v-model="form.item_type" placeholder="请选择数据类型" style="width: 100%">
            <el-option label="字符串" :value="0" />
            <el-option label="数字" :value="1" />
            <el-option label="布尔" :value="2" />
            <el-option label="JSON" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置值" required>
          <el-input v-model="form.item_value" type="textarea" :rows="3" placeholder="请输入配置值" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="版本号" required>
              <el-input-number v-model="form.version" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="权重">
              <el-input-number v-model="form.weight" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态" required>
          <el-radio-group v-model="form.status">
            <el-radio :value="1">有效</el-radio>
            <el-radio :value="0">无效</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上线时间">
              <el-date-picker
                v-model="form.online_time_date"
                type="datetime"
                placeholder="请选择上线时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下线时间">
              <el-date-picker
                v-model="form.offline_time_date"
                type="datetime"
                placeholder="请选择下线时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="系统平台">
          <el-input v-model="form.sys_code" placeholder="公共为common，单平台为平台标识" />
        </el-form-item>
        <el-form-item label="排除平台">
          <el-input v-model="form.quarantine" placeholder="多个平台用逗号分割" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getSystemConfigList,
  createSystemConfig,
  updateSystemConfig,
  deleteSystemConfig
} from '@/api/systemConfig';

const dialogVisible = ref(false);
const saving = ref(false);
const editRow = ref<any>(null);
const tableData = ref<any[]>([]);
const total = ref(0);

const query = reactive({
  page: 1,
  page_size: 10,
  item_name: '',
  sys_code: ''
});

const form = reactive({
  item_name: '',
  description: '',
  item_type: 0,
  item_value: '',
  weight: 0,
  version: 1,
  status: 1,
  online_time_date: null as Date | null,
  offline_time_date: null as Date | null,
  remark: '',
  sys_code: '',
  quarantine: ''
});

const itemTypeLabel = (type: number) => {
  const map: Record<number, string> = { 0: '字符串', 1: '数字', 2: '布尔', 3: 'JSON' };
  return map[type] ?? '未知';
};

const formatTimestamp = (ts: number) => {
  if (!ts) return '-';
  const d = new Date(ts * 1000);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

const dateToTimestamp = (d: Date | null): number => {
  if (!d) return 0;
  return Math.floor(new Date(d).getTime() / 1000);
};

const timestampToDate = (ts: number): Date | null => {
  if (!ts) return null;
  return new Date(ts * 1000);
};

const loadData = async () => {
  try {
    const params: any = { page: query.page, page_size: query.page_size };
    if (query.item_name) params.item_name = query.item_name;
    if (query.sys_code) params.sys_code = query.sys_code;
    const response = await getSystemConfigList(params);
    tableData.value = response.data.items;
    total.value = response.data.total;
  } catch {
    ElMessage.error('获取数据失败');
  }
};

const resetQuery = () => {
  query.item_name = '';
  query.sys_code = '';
  query.page = 1;
  loadData();
};

const handleSizeChange = (size: number) => {
  query.page_size = size;
  loadData();
};

const handleCurrentChange = (current: number) => {
  query.page = current;
  loadData();
};

const resetForm = () => {
  form.item_name = '';
  form.description = '';
  form.item_type = 0;
  form.item_value = '';
  form.weight = 0;
  form.version = 1;
  form.status = 1;
  form.online_time_date = null;
  form.offline_time_date = null;
  form.remark = '';
  form.sys_code = '';
  form.quarantine = '';
};

const openDialog = (row?: any) => {
  if (row) {
    editRow.value = row;
    form.item_name = row.item_name;
    form.description = row.description;
    form.item_type = row.item_type;
    form.item_value = row.item_value;
    form.weight = row.weight;
    form.version = row.version;
    form.status = row.status;
    form.online_time_date = timestampToDate(row.online_time);
    form.offline_time_date = timestampToDate(row.offline_time);
    form.remark = row.remark;
    form.sys_code = row.sys_code;
    form.quarantine = row.quarantine || '';
  } else {
    editRow.value = null;
    resetForm();
  }
  dialogVisible.value = true;
};

const saveData = async () => {
  if (!form.item_name) {
    ElMessage.error('请输入配置项名称');
    return;
  }

  saving.value = true;
  try {
    const payload = {
      item_name: form.item_name,
      description: form.description,
      item_type: form.item_type,
      item_value: form.item_value,
      weight: form.weight,
      version: form.version,
      status: form.status,
      online_time: dateToTimestamp(form.online_time_date),
      offline_time: dateToTimestamp(form.offline_time_date),
      remark: form.remark,
      sys_code: form.sys_code,
      quarantine: form.quarantine
    };

    if (editRow.value) {
      await updateSystemConfig(editRow.value.id, payload);
      ElMessage.success('更新成功');
    } else {
      await createSystemConfig(payload);
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    loadData();
  } catch {
    ElMessage.error('操作失败');
  } finally {
    saving.value = false;
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条配置项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deleteSystemConfig(id);
    ElMessage.success('删除成功');
    loadData();
  } catch {
    // 取消删除
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
