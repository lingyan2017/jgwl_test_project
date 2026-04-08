<template>
  <div class="test-query-data-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试查询数据管理</span>
          <el-button type="primary" @click="openDialog()">新增</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="query" class="mb-4">
        <el-form-item label="URL">
          <el-input v-model="query.url" placeholder="请输入URL" style="width: 300px" />
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="query.language" placeholder="请选择语言">
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统编码">
          <el-input v-model="query.sys_code" placeholder="请输入系统编码" style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="url" label="URL" min-width="300" />
        <el-table-column prop="language" label="语言" width="100">
          <template #default="{row}">
            {{ row.language === 'java' ? 'Java' : 'Go' }}
          </template>
        </el-table-column>
        <el-table-column prop="sys_code" label="系统编码" width="150" />
        <el-table-column prop="params" label="请求参数" min-width="200">
          <template #default="{row}">
            <el-tooltip :content="JSON.stringify(row.params, null, 2)" placement="top">
              <span>{{ JSON.stringify(row.params).substring(0, 50) }}{{ JSON.stringify(row.params).length > 50 ? '...' : '' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column prop="create_user" label="创建人" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" text @click="handleDelete(row.id)">删除</el-button>
            <el-button size="small" type="success" text @click="openCallDialog(row)">调用</el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑测试数据' : '新增测试数据'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="URL" required>
          <el-input v-model="form.url" placeholder="请输入URL" style="width: 100%" />
        </el-form-item>
        <el-form-item label="语言" required>
          <el-select v-model="form.language" placeholder="请选择语言">
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统编码" required>
          <el-input v-model="form.sys_code" placeholder="请输入系统编码" style="width: 100%" />
        </el-form-item>
        <el-form-item label="请求参数" required>
          <el-input
            v-model="form.paramsStr"
            type="textarea"
            placeholder="请输入JSON格式的请求参数"
            :rows="5"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveData">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 调用对话框 -->
    <el-dialog v-model="callDialogVisible" title="调用接口" width="600px">
      <el-form :model="callForm" label-width="100px">
        <el-form-item label="URL">
          <el-input v-model="callForm.url" disabled style="width: 100%" />
        </el-form-item>
        <el-form-item label="语言">
          <el-input v-model="callForm.language" disabled />
        </el-form-item>
        <el-form-item label="系统编码">
          <el-input v-model="callForm.sys_code" disabled />
        </el-form-item>
        <el-form-item label="请求参数">
          <el-input
            v-model="callForm.paramsStr"
            type="textarea"
            placeholder="请输入JSON格式的请求参数"
            :rows="5"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item v-if="callResponse" label="响应结果">
          <el-input
            v-model="callResponseStr"
            type="textarea"
            placeholder="响应结果"
            :rows="5"
            style="width: 100%"
            disabled
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="callDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="callApi">确认调用</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { getTestQueryDataList, createTestQueryData, updateTestQueryData, deleteTestQueryData, callTestQueryData } from '@/api/testQueryData';

const router = useRouter();
const dialogVisible = ref(false);
const callDialogVisible = ref(false);
const editRow = ref<any>(null);
const tableData = ref<any[]>([]);
const total = ref(0);
const callResponse = ref<any>(null);

const query = reactive({
  page: 1,
  page_size: 10,
  url: '',
  language: '',
  sys_code: ''
});

const form = reactive({
  url: '',
  language: 'java',
  sys_code: '',
  paramsStr: '{}'
});

const callForm = reactive({
  id: 0,
  url: '',
  language: '',
  sys_code: '',
  paramsStr: '{}'
});

const callResponseStr = computed(() => {
  return callResponse.value ? JSON.stringify(callResponse.value, null, 2) : '';
});

const loadData = async () => {
  try {
    const response = await getTestQueryDataList(query);
    tableData.value = response.data.items;
    total.value = response.data.total;
  } catch (error) {
    ElMessage.error('获取数据失败');
  }
};

const resetQuery = () => {
  query.url = '';
  query.language = '';
  query.sys_code = '';
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

const openDialog = (row?: any) => {
  if (row) {
    editRow.value = row;
    form.url = row.url;
    form.language = row.language;
    form.sys_code = row.sys_code;
    form.paramsStr = JSON.stringify(row.params, null, 2);
  } else {
    editRow.value = null;
    form.url = '';
    form.language = 'java';
    form.sys_code = '';
    form.paramsStr = '{}';
  }
  dialogVisible.value = true;
};

const saveData = async () => {
  try {
    let params;
    try {
      params = JSON.parse(form.paramsStr);
    } catch (error) {
      ElMessage.error('请求参数格式错误，请输入有效的JSON');
      return;
    }

    if (editRow.value) {
      await updateTestQueryData(editRow.value.id, {
        url: form.url,
        language: form.language,
        sys_code: form.sys_code,
        params
      });
      ElMessage.success('更新成功');
    } else {
      await createTestQueryData({
        url: form.url,
        language: form.language,
        sys_code: form.sys_code,
        params
      });
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    loadData();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deleteTestQueryData(id);
    ElMessage.success('删除成功');
    loadData();
  } catch (error) {
    // 取消删除
  }
};

const openCallDialog = (row: any) => {
  callForm.id = row.id;
  callForm.url = row.url;
  callForm.language = row.language === 'java' ? 'Java' : 'Go';
  callForm.sys_code = row.sys_code;
  callForm.paramsStr = JSON.stringify(row.params, null, 2);
  callResponse.value = null;
  callDialogVisible.value = true;
};

const callApi = async () => {
  try {
    let params;
    try {
      params = JSON.parse(callForm.paramsStr);
    } catch (error) {
      ElMessage.error('请求参数格式错误，请输入有效的JSON');
      return;
    }

    const response = await callTestQueryData({
      test_query_data_id: callForm.id,
      params
    });
    callResponse.value = response.data;
    ElMessage.success('调用成功');
  } catch (error: any) {
    ElMessage.error('调用失败: ' + (error.response?.data?.detail || '未知错误'));
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>