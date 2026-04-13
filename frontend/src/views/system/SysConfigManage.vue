<template>
  <div class="sys-config-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置管理</span>
          <el-button type="primary" @click="openDialog()">新增</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="query" class="mb-4">
        <el-form-item label="系统编码">
          <el-input v-model="query.sys_code" placeholder="请输入系统编码" style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="请选择状态" clearable>
            <el-option label="不可用" :value="0" />
            <el-option label="可用" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sys_code" label="系统编码" width="150" />
        <el-table-column prop="aes_key" label="AES Key" min-width="200" show-overflow-tooltip />
        <el-table-column prop="aes_iv" label="AES IV" min-width="200" show-overflow-tooltip />
        <el-table-column prop="java_domain_name" label="Java域名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="go_domain_name" label="Go域名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '可用' : '不可用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="run_mode" label="运行模式" width="120">
          <template #default="{row}">
            <el-tag :type="row.run_mode === 1 ? 'warning' : 'info'">
              {{ row.run_mode === 1 ? '生产环境' : '测试环境' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column prop="create_user" label="创建人" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" text @click="handleDelete(row.id)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑配置' : '新增配置'" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="系统编码" required>
          <el-input v-model="form.sys_code" placeholder="请输入系统编码" style="width: 100%" />
        </el-form-item>
        <el-form-item label="AES Key" required>
          <el-input v-model="form.aes_key" placeholder="请输入AES加密Key" style="width: 100%" />
        </el-form-item>
        <el-form-item label="AES IV" required>
          <el-input v-model="form.aes_iv" placeholder="请输入AES加密IV" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Java域名">
          <el-input v-model="form.java_domain_name" placeholder="请输入Java服务域名" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Go域名">
          <el-input v-model="form.go_domain_name" placeholder="请输入Go服务域名" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-radio-group v-model="form.status">
            <el-radio :label="0">不可用</el-radio>
            <el-radio :label="1">可用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="运行模式" required>
          <el-radio-group v-model="form.run_mode">
            <el-radio :label="0">测试环境</el-radio>
            <el-radio :label="1">生产环境</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveData">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { getSysConfigList, createSysConfig, updateSysConfig, deleteSysConfig } from '@/api/sysConfig';

const router = useRouter();
const dialogVisible = ref(false);
const editRow = ref<any>(null);
const tableData = ref<any[]>([]);
const total = ref(0);

const query = reactive({
  page: 1,
  page_size: 10,
  sys_code: '',
  status: undefined as number | undefined
});

const form = reactive({
  aes_key: '',
  aes_iv: '',
  java_domain_name: '',
  go_domain_name: '',
  status: 0,
  run_mode: 0,
  sys_code: ''
});

const loadData = async () => {
  try {
    const response = await getSysConfigList(query);
    tableData.value = response.data.items;
    total.value = response.data.total;
  } catch (error) {
    ElMessage.error('获取数据失败');
  }
};

const resetQuery = () => {
  query.sys_code = '';
  query.status = undefined;
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
    form.aes_key = row.aes_key;
    form.aes_iv = row.aes_iv;
    form.java_domain_name = row.java_domain_name;
    form.go_domain_name = row.go_domain_name;
    form.status = row.status;
    form.run_mode = row.run_mode;
    form.sys_code = row.sys_code;
  } else {
    editRow.value = null;
    form.aes_key = '';
    form.aes_iv = '';
    form.java_domain_name = '';
    form.go_domain_name = '';
    form.status = 0;
    form.run_mode = 0;
    form.sys_code = '';
  }
  dialogVisible.value = true;
};

const saveData = async () => {
  try {
    if (editRow.value) {
      await updateSysConfig(editRow.value.id, {
        aes_key: form.aes_key,
        aes_iv: form.aes_iv,
        java_domain_name: form.java_domain_name,
        go_domain_name: form.go_domain_name,
        status: form.status,
        run_mode: form.run_mode,
        sys_code: form.sys_code
      });
      ElMessage.success('更新成功');
    } else {
      await createSysConfig({
        aes_key: form.aes_key,
        aes_iv: form.aes_iv,
        java_domain_name: form.java_domain_name,
        go_domain_name: form.go_domain_name,
        status: form.status,
        run_mode: form.run_mode,
        sys_code: form.sys_code
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
    await deleteSysConfig(id);
    ElMessage.success('删除成功');
    loadData();
  } catch (error) {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>