<template>
  <div>
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form :model="query" inline>
        <el-form-item label="租户名称">
          <el-input v-model="query.tenant_name" placeholder="请输入" clearable style="width:200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width:120px">
            <el-option label="启用" :value="1" /><el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadData">搜索</el-button>
          <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>租户列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增租户</el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id"           label="ID"     width="80"  />
        <el-table-column prop="tenant_id"    label="租户ID" width="150" />
        <el-table-column prop="tenant_name"  label="租户名称" />
        <el-table-column prop="contact_name" label="联系人"  width="120" />
        <el-table-column prop="contact_phone"label="联系电话" width="140" />
        <el-table-column prop="contact_email"label="邮箱" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger"  text @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @change="loadData"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑租户' : '新增租户'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="租户ID" prop="tenant_id">
          <el-input v-model="form.tenant_id" :disabled="!!editRow" placeholder="唯一标识，创建后不可修改" />
        </el-form-item>
        <el-form-item label="租户名称" prop="tenant_name">
          <el-input v-model="form.tenant_name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.contact_email" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio><el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getTenantList, createTenant, updateTenant, deleteTenant } from '@/api/tenant'
import type { TenantInfo } from '@/types'

const loading = ref<boolean>(false)
const submitting = ref<boolean>(false)
const tableData = ref<TenantInfo[]>([])
const total = ref<number>(0)
const dialogVisible = ref<boolean>(false)
const editRow = ref<TenantInfo | null>(null)
const formRef = ref<FormInstance>()

interface TenantQuery { page: number; page_size: number; tenant_name: string; status: number | null }
interface TenantForm { tenant_id: string; tenant_name: string; contact_name: string; contact_phone: string; contact_email: string; status: number }

const query = reactive<TenantQuery>({ page: 1, page_size: 10, tenant_name: '', status: null })
const form = reactive<TenantForm>({ tenant_id: '', tenant_name: '', contact_name: '', contact_phone: '', contact_email: '', status: 1 })
const rules: FormRules<TenantForm> = {
  tenant_id: [{ required: true, message: '请输入租户ID', trigger: 'blur' }],
  tenant_name: [{ required: true, message: '请输入租户名称', trigger: 'blur' }],
}

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, unknown> = { ...query }
    if (params.status === null) delete params.status
    const res = await getTenantList(params)
    tableData.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function resetQuery(): void {
  Object.assign(query, { page: 1, page_size: 10, tenant_name: '', status: null })
  loadData()
}

function openDialog(row: TenantInfo | null = null): void {
  editRow.value = row
  if (row) {
    Object.assign(form, { tenant_id: row.tenant_id, tenant_name: row.tenant_name, contact_name: row.contact_name || '', contact_phone: row.contact_phone || '', contact_email: row.contact_email || '', status: row.status })
  } else {
    Object.assign(form, { tenant_id: '', tenant_name: '', contact_name: '', contact_phone: '', contact_email: '', status: 1 })
  }
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editRow.value) {
      await updateTenant(editRow.value.id, { tenant_name: form.tenant_name, contact_name: form.contact_name, contact_phone: form.contact_phone, contact_email: form.contact_email, status: form.status })
    } else {
      await createTenant({ ...form })
    }
    ElMessage.success(editRow.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleDelete(id: number): Promise<void> {
  await ElMessageBox.confirm('确认删除该租户？', '警告', { type: 'warning' })
  await deleteTenant(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
