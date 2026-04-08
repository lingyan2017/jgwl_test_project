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
        <el-form-item label="配置项名称">
          <el-input v-model="query.item_name" placeholder="请输入配置项名称" style="width: 200px" />
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
        <el-table-column prop="item_name" label="配置项名称" width="200" />
        <el-table-column prop="item_value" label="配置值" min-width="300" />
        <el-table-column prop="sys_code" label="系统编码" width="150" />
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
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑配置' : '新增配置'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="配置项名称" required>
          <el-input v-model="form.item_name" placeholder="请输入配置项名称" style="width: 100%" />
        </el-form-item>
        <el-form-item label="配置值" required>
          <el-input v-model="form.item_value" placeholder="请输入配置值" style="width: 100%" />
        </el-form-item>
        <el-form-item label="系统编码" required>
          <el-input v-model="form.sys_code" placeholder="请输入系统编码" style="width: 100%" />
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
  item_name: '',
  sys_code: ''
});

const form = reactive({
  item_name: '',
  item_value: '',
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
  query.item_name = '';
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
    form.item_name = row.item_name;
    form.item_value = row.item_value;
    form.sys_code = row.sys_code;
  } else {
    editRow.value = null;
    form.item_name = '';
    form.item_value = '';
    form.sys_code = '';
  }
  dialogVisible.value = true;
};

const saveData = async () => {
  try {
    if (editRow.value) {
      await updateSysConfig(editRow.value.id, {
        item_name: form.item_name,
        item_value: form.item_value,
        sys_code: form.sys_code
      });
      ElMessage.success('更新成功');
    } else {
      await createSysConfig({
        item_name: form.item_name,
        item_value: form.item_value,
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