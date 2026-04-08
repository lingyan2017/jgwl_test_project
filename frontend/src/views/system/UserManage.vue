<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :model="query" inline>
        <el-form-item label="用户名"><el-input v-model="query.username" placeholder="请输入" clearable style="width:180px" /></el-form-item>
        <el-form-item label="租户ID"><el-input v-model="query.tenant_id" placeholder="请输入" clearable style="width:150px" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width:100px">
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
          <span>用户列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增用户</el-button>
        </div>
      </template>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id"        label="ID"    width="70" />
        <el-table-column prop="username"  label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名"  width="90" />
        <el-table-column prop="tenant_id" label="租户"  width="110" />
        <el-table-column prop="dept_id"   label="部门"  width="110">
          <template #default="{ row }">{{ row.dept_id ? (deptMap[row.dept_id] ?? row.dept_id) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="post_id"   label="岗位"  width="110">
          <template #default="{ row }">{{ row.post_id ? (postMap[row.post_id] ?? row.post_id) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="user_type" label="类型"  width="110">
          <template #default="{ row }">
            <el-tag :type="row.user_type===0?'danger':row.user_type===1?'warning':'info'">
              {{ userTypeMap[row.user_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status===1?'success':'danger'">{{ row.status===1?'启用':'禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger"  text @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" style="margin-top:16px;justify-content:flex-end" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑用户':'新增用户'" width="580px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">

        <!-- 租户ID：新增时下拉，编辑时禁用展示 -->
        <el-form-item label="租户ID" prop="tenant_id">
          <template v-if="!editRow">
            <el-select
              v-model="form.tenant_id"
              placeholder="请选择租户ID"
              filterable
              style="width:100%"
              v-loading="tenantIdLoading"
              element-loading-text="加载中..."
            >
              <el-option v-for="opt in tenantIdOptions" :key="opt.value" :label="opt.label" :value="opt.value">
                <span style="float:left">{{ opt.value }}</span>
                <span style="float:right;color:#aaa;font-size:12px">{{ opt.tenantName }}</span>
              </el-option>
              <template v-if="tenantIdOptions.length === 0 && !tenantIdLoading" #empty>
                <div style="text-align:center;padding:12px;color:#aaa">暂无可用租户</div>
              </template>
            </el-select>
          </template>
          <el-input v-else :model-value="form.tenant_id" disabled />
        </el-form-item>

        <el-form-item label="用户名"   prop="username"><el-input v-model="form.username" :disabled="!!editRow" /></el-form-item>
        <el-form-item label="密码"     prop="password" v-if="!editRow"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone" /></el-form-item>

        <!-- 部门 -->
        <el-form-item label="部门">
          <el-select v-model="form.dept_id" clearable placeholder="请选择部门" style="width:100%" :disabled="!form.tenant_id">
            <el-option v-for="opt in deptOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>

        <!-- 岗位 -->
        <el-form-item label="岗位">
          <el-select v-model="form.post_id" clearable placeholder="请选择岗位" style="width:100%" :disabled="!form.tenant_id">
            <el-option v-for="opt in postOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>

        <!-- 角色 -->
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple clearable placeholder="请选择角色" style="width:100%" :disabled="!form.tenant_id">
            <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="用户类型">
          <el-select v-model="form.user_type" style="width:100%">
            <el-option label="超级管理员" :value="0" /><el-option label="租户管理员" :value="1" /><el-option label="普通用户" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status"><el-radio :value="1">启用</el-radio><el-radio :value="0">禁用</el-radio></el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser, getUserRoles } from '@/api/user'
import { getTenantList } from '@/api/tenant'
import { getDeptList } from '@/api/dept'
import { getPostList } from '@/api/post'
import { getRoleList } from '@/api/role'
import { useAuthStore } from '@/stores/auth'
import type { UserInfo } from '@/types'

const authStore = useAuthStore()
const userTypeMap: Record<number, string> = { 0: '超级管理员', 1: '租户管理员', 2: '普通用户' }

const loading = ref<boolean>(false)
const submitting = ref<boolean>(false)
const tableData = ref<UserInfo[]>([])
const total = ref<number>(0)
const dialogVisible = ref<boolean>(false)
const editRow = ref<UserInfo | null>(null)
const formRef = ref<FormInstance>()

// 表格展示用：部门/岗位 id->name 映射
const deptMap = ref<Record<number, string>>({})
const postMap = ref<Record<number, string>>({})

// 租户ID下拉
interface TenantIdOption { value: string; label: string; tenantName: string }
const tenantIdOptions = ref<TenantIdOption[]>([])
const tenantIdLoading = ref<boolean>(false)

// 对话框内的关联数据选项
interface SelectOption { value: number; label: string }
const deptOptions = ref<SelectOption[]>([])
const postOptions = ref<SelectOption[]>([])
const roleOptions = ref<SelectOption[]>([])

interface UserQuery { page: number; page_size: number; username: string; tenant_id: string; status: number | null }
interface UserForm {
  tenant_id: string; username: string; password: string; real_name: string
  email: string; phone: string; user_type: number
  dept_id: number | null; post_id: number | null; role_ids: number[]; status: number
}

const query = reactive<UserQuery>({ page: 1, page_size: 10, username: '', tenant_id: '', status: null })
const form = reactive<UserForm>({
  tenant_id: '', username: '', password: '', real_name: '', email: '', phone: '',
  user_type: 2, dept_id: null, post_id: null, role_ids: [], status: 1,
})
const rules: FormRules<UserForm> = {
  tenant_id: [{ required: true, message: '请选择租户ID', trigger: 'change' }],
  username:  [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password:  [{ required: true, message: '请输入密码',   trigger: 'blur' }],
}

/** 加载租户下拉选项（新增时使用） */
async function loadTenantIdOptions(): Promise<void> {
  tenantIdLoading.value = true
  try {
    const res = await getTenantList({ page: 1, page_size: 200, status: 1 })
    const currentUser = authStore.user
    tenantIdOptions.value = res.data.items
      .filter(t => currentUser?.user_type === 0 || t.tenant_id === currentUser?.tenant_id)
      .map(t => ({ value: t.tenant_id, label: `${t.tenant_id} - ${t.tenant_name}`, tenantName: t.tenant_name }))
  } finally {
    tenantIdLoading.value = false
  }
}

/** 加载指定租户下的部门/岗位/角色选项（对话框内联动） */
async function loadAssociatedOptions(tenantId: string): Promise<void> {
  const [deptRes, postRes, roleRes] = await Promise.all([
    getDeptList({ page: 1, page_size: 500, tenant_id: tenantId, status: 1 }),
    getPostList({ page: 1, page_size: 500, tenant_id: tenantId, status: 1 }),
    getRoleList({ page: 1, page_size: 500, tenant_id: tenantId, status: 1 }),
  ])
  deptOptions.value = deptRes.data.items.map(d => ({ value: d.id, label: d.dept_name }))
  postOptions.value = postRes.data.items.map(p => ({ value: p.id, label: p.post_name }))
  roleOptions.value = roleRes.data.items.map(r => ({ value: r.id, label: r.role_name }))
}

/** 新增时，选择租户后自动刷新部门/岗位/角色 */
watch(() => form.tenant_id, async (newTid) => {
  if (!editRow.value && newTid) {
    form.dept_id = null
    form.post_id = null
    form.role_ids = []
    await loadAssociatedOptions(newTid)
  }
})

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, unknown> = { ...query }
    if (!params.username) delete params.username
    if (!params.tenant_id) delete params.tenant_id
    if (params.status === null) delete params.status
    const res = await getUserList(params)
    tableData.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function resetQuery(): void {
  Object.assign(query, { page: 1, page_size: 10, username: '', tenant_id: '', status: null })
  loadData()
}

async function openDialog(row: UserInfo | null = null): Promise<void> {
  editRow.value = row
  deptOptions.value = []
  postOptions.value = []
  roleOptions.value = []

  if (row) {
    // 编辑：加载该用户所在租户的关联数据 + 当前角色
    const [roleRes] = await Promise.all([
      getUserRoles(row.id),
      loadAssociatedOptions(row.tenant_id),
    ])
    Object.assign(form, {
      tenant_id: row.tenant_id,
      username:  row.username,
      password:  '',
      real_name: row.real_name ?? '',
      email:     row.email ?? '',
      phone:     row.phone ?? '',
      user_type: row.user_type,
      dept_id:   row.dept_id ?? null,
      post_id:   row.post_id ?? null,
      role_ids:  roleRes.data as number[],
      status:    row.status ?? 1,
    })
  } else {
    // 新增：清空并加载租户选项（选择租户后再加载部门/岗位/角色）
    Object.assign(form, {
      tenant_id: '', username: '', password: '', real_name: '', email: '', phone: '',
      user_type: 2, dept_id: null, post_id: null, role_ids: [], status: 1,
    })
    await loadTenantIdOptions()
  }

  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function handleSubmit(): Promise<void> {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editRow.value) {
      await updateUser(editRow.value.id, {
        real_name: form.real_name,
        email:     form.email,
        phone:     form.phone,
        user_type: form.user_type,
        dept_id:   form.dept_id,
        post_id:   form.post_id,
        role_ids:  form.role_ids,
        status:    form.status,
      })
    } else {
      await createUser({ ...form })
    }
    ElMessage.success(editRow.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleDelete(id: number): Promise<void> {
  await ElMessageBox.confirm('确认删除该用户？', '警告', { type: 'warning' })
  await deleteUser(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(async () => {
  // 预加载部门/岗位映射，用于表格展示名称
  const [deptRes, postRes] = await Promise.all([
    getDeptList({ page: 1, page_size: 1000 }),
    getPostList({ page: 1, page_size: 1000 }),
  ])
  deptRes.data.items.forEach(d => { deptMap.value[d.id] = d.dept_name })
  postRes.data.items.forEach(p => { postMap.value[p.id] = p.post_name })
  loadData()
})
</script>
