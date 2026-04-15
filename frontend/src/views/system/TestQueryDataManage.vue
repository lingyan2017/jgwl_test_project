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
        <el-table-column prop="url" label="URL" min-width="250" />
        <el-table-column prop="url_desc" label="URL说明" min-width="150" />
        <el-table-column prop="language" label="语言" width="100">
          <template #default="{row}">
            {{ row.language === 'java' ? 'Java' : 'Go' }}
          </template>
        </el-table-column>
        <el-table-column prop="params" label="请求参数" min-width="200">
          <template #default="{row}">
            <el-tooltip :content="JSON.stringify(row.params, null, 2)" placement="top">
              <span>{{ JSON.stringify(row.params).substring(0, 50) }}{{ JSON.stringify(row.params).length > 50 ? '...' : '' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="has_image" label="包含图片" width="100">
          <template #default="{row}">
            <el-tag :type="row.has_image === 1 ? 'success' : 'info'">
              {{ row.has_image === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column prop="create_user" label="创建人" width="120" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" text @click="handleDelete(row.id)">删除</el-button>
            <el-button size="small" type="success" text @click="openCallDialog(row)">调用</el-button>
            <el-button size="small" type="info" text @click="viewLatestLog(row)">最新日志</el-button>
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
        <el-form-item label="URL说明">
          <el-input v-model="form.urlDesc" placeholder="请输入URL说明，如：设置密码接口" style="width: 100%" />
        </el-form-item>
        <el-form-item label="语言" required>
          <el-select v-model="form.language" placeholder="请选择语言">
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
          </el-select>
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
        <el-form-item label="包含图片">
          <el-switch
            v-model="form.hasImage"
            :active-value="1"
            :inactive-value="0"
            active-text="是"
            inactive-text="否"
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
        <el-form-item label="系统编码" required>
          <el-input v-model="callForm.sysCode" placeholder="请输入系统编码" style="width: 100%" />
        </el-form-item>
        <el-form-item label="运行模式" required>
          <el-radio-group v-model="callForm.run_mode">
            <el-radio :label="0">测试环境</el-radio>
            <el-radio :label="1">生产环境</el-radio>
          </el-radio-group>
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
        <!-- 文件上传区域，仅当hasImage为true时显示 -->
        <el-form-item v-if="selectedTestData?.has_image === 1" label="上传图片">
          <el-upload
            v-model:file-list="fileList"
            drag
            multiple
            :before-upload="beforeUpload"
            :on-remove="handleRemoveFile"
            :auto-upload="false"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">可上传多个图片文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="callDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="callApi">确认调用</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 响应结果弹窗 -->
    <el-dialog v-model="responseDialogVisible" title="响应结果" width="700px">
      <el-alert
        v-if="callSuccess"
        title="调用成功"
        type="success"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-alert
        v-else
        title="调用失败"
        type="error"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-input
        v-model="responseDisplayStr"
        type="textarea"
        placeholder="响应结果"
        :rows="15"
        style="width: 100%"
        readonly
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="responseDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 最新日志弹窗 -->
    <el-dialog v-model="logDialogVisible" title="最新调用日志" width="800px">
      <div v-if="latestLog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志ID">{{ latestLog.id }}</el-descriptions-item>
          <el-descriptions-item label="系统编码">{{ latestLog.sys_code }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="latestLog.status === 1 ? 'success' : 'danger'">
              {{ latestLog.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="调用时间">{{ latestLog.create_time }}</el-descriptions-item>
          <el-descriptions-item label="调用人">{{ latestLog.create_user }}</el-descriptions-item>
          <el-descriptions-item label="错误信息" v-if="latestLog.error_msg">
            {{ latestLog.error_msg }}
          </el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="left">请求参数</el-divider>
        <el-input
          v-model="latestLogRequestStr"
          type="textarea"
          :rows="8"
          readonly
        />
        <el-divider content-position="left">响应数据</el-divider>
        <el-input
          v-model="latestLogResponseStr"
          type="textarea"
          :rows="8"
          readonly
        />
      </div>
      <div v-else>
        <el-empty description="暂无日志记录" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="logDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { UploadFilled } from '@element-plus/icons-vue';
import { getTestQueryDataList, createTestQueryData, updateTestQueryData, deleteTestQueryData, callTestQueryData, callTestQueryDataWithFiles, getLatestTestQueryDataLog } from '@/api/testQueryData';

const router = useRouter();
const dialogVisible = ref(false);
const callDialogVisible = ref(false);
const responseDialogVisible = ref(false);
const logDialogVisible = ref(false);
const editRow = ref<any>(null);
const tableData = ref<any[]>([]);
const total = ref(0);
const callResponse = ref<any>(null);
const callSuccess = ref(false);
const latestLog = ref<any>(null);

const query = reactive({
  page: 1,
  page_size: 10,
  url: '',
  language: '',
  sys_code: ''
});

const form = reactive({
  url: '',
  urlDesc: '',
  language: 'java',
  hasImage: 0,
  paramsStr: '{}'
});

const callForm = reactive({
  id: 0,
  url: '',
  language: '',
  sysCode: '',  // 调用时填写的系统编码
  run_mode: 0,  // 0-测试环境, 1-生产环境
  paramsStr: '{}'
});

const selectedTestData = ref<any>(null);  // 当前选中的测试数据
const fileList = ref<any[]>([]);  // 文件列表

const callResponseStr = computed(() => {
  return callResponse.value ? JSON.stringify(callResponse.value, null, 2) : '';
});

const responseDisplayStr = computed(() => {
  if (!callResponse.value) return '';
  return JSON.stringify(callResponse.value, null, 2);
});

const latestLogRequestStr = computed(() => {
  if (!latestLog.value || !latestLog.value.request_params) return '';
  return JSON.stringify(latestLog.value.request_params, null, 2);
});

const latestLogResponseStr = computed(() => {
  if (!latestLog.value || !latestLog.value.response_data) return '';
  return JSON.stringify(latestLog.value.response_data, null, 2);
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
    form.urlDesc = row.url_desc || '';
    form.language = row.language;
    form.hasImage = row.has_image || 0;
    form.paramsStr = JSON.stringify(row.params, null, 2);
  } else {
    editRow.value = null;
    form.url = '';
    form.urlDesc = '';
    form.language = 'java';
    form.hasImage = 0;
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
        url_desc: form.urlDesc,
        language: form.language,
        params,
        has_image: form.hasImage
      });
      ElMessage.success('更新成功');
    } else {
      await createTestQueryData({
        url: form.url,
        url_desc: form.urlDesc,
        language: form.language,
        params,
        has_image: form.hasImage
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
  callForm.sysCode = '';  // 清空，需要用户重新输入
  callForm.run_mode = 0;  // 默认测试环境
  callForm.paramsStr = JSON.stringify(row.params, null, 2);
  selectedTestData.value = row;  // 设置当前选中的测试数据
  fileList.value = [];  // 清空文件列表
  callResponse.value = null;
  callSuccess.value = false;
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

    if (!callForm.sysCode) {
      ElMessage.error('请输入系统编码');
      return;
    }

    // 判断是否需要上传文件
    if (selectedTestData.value?.has_image === 1 && fileList.value.length > 0) {
      // 使用文件上传接口
      const formData = new FormData();
      formData.append('test_query_data_id', callForm.id.toString());
      formData.append('sys_code', callForm.sysCode);
      formData.append('run_mode', callForm.run_mode.toString());
      formData.append('params', JSON.stringify(params));
      
      // 添加文件
      fileList.value.forEach((fileObj, index) => {
        if (fileObj.raw) {
          formData.append('files', fileObj.raw);
        } else if (fileObj instanceof File) {
          formData.append('files', fileObj);
        }
      });

      const response = await callTestQueryDataWithFiles(formData);
      // 保存响应数据
      callResponse.value = response.data;
      callSuccess.value = response.data.success;
    } else {
      // 使用普通接口
      const response = await callTestQueryData({
        test_query_data_id: callForm.id,
        sys_code: callForm.sysCode,
        params,
        run_mode: callForm.run_mode
      });
      
      // 保存响应数据
      callResponse.value = response.data;
      callSuccess.value = response.data.success;
    }
    
    // 关闭调用对话框
    callDialogVisible.value = false;
    
    // 弹出显示响应结果
    responseDialogVisible.value = true;
    
    ElMessage.success(callSuccess.value ? '调用成功' : '调用失败');
  } catch (error: any) {
    ElMessage.error('调用失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

// 文件上传前的验证
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/');
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage.error('只能上传图片文件!');
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!');
  }
  return isImage && isLt2M;
};

// 移除文件
const handleRemoveFile = (file: any, fileList: any[]) => {
  // 处理移除文件的逻辑
  console.log('移除文件:', file, fileList);
};

const viewLatestLog = async (row: any) => {
  try {
    const response = await getLatestTestQueryDataLog(row.id);
    latestLog.value = response.data.log;
    logDialogVisible.value = true;
  } catch (error) {
    ElMessage.error('获取日志失败');
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