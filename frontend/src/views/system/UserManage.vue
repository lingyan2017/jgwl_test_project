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
        <el-table-column prop="username"  label="用户名" width="130" />
        <el-table-column prop="real_name" label="姓名"  width="100" />
        <el-table-column prop="tenant_id" label="租户"  width="120" />
        <el-table-column prop="email"     label="邮箱" />
        <el-table-column prop="phone"     label="手机"  width="130" />
        <el-table-column prop="user_type" label="类型"  width="110">
          <template #default="{ row }">
            <el-tag :type="row.user_type===0?'danger':row.user_type===1?'warning':'info'">
              {{ {0:'超级管理员',1:'租户管理员',2:'普通用户'}[row.user_type] }}
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

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑用户':'新增用户'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="租户ID"   prop="tenant_id"><el-input v-model="form.tenant_id" :disabled="!!editRow" /></el-form-item>
        <el-form-item label="用户名"   prop="username"><el-input v-model="form.username" :disabled="!!editRow" /></el-form-item>
        <el-form-item label="密码"     prop="password" v-if="!editRow"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone" /></el-form-item>
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
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import type { UserInfo } from '@/types'

const loading = ref<boolean>(false); const submitting = ref<boolean>(false)
const tableData = ref<UserInfo[]>([]); const total = ref<number>(0)
const dialogVisible = ref<boolean>(false); const editRow = ref<UserInfo | null>(null); const formRef = ref<FormInstance>()

interface UserQuery { page: number; page_size: number; username: string; tenant_id: string; status: number | null }
interface UserForm { tenant_id: string; username: string; password: string; real_name: string; email: string; phone: string; user_type: number; status: number }

const query = reactive<UserQuery>({ page:1, page_size:10, username:'', tenant_id:'', status:null })
const form = reactive<UserForm>({ tenant_id:'', username:'', password:'', real_name:'', email:'', phone:'', user_type:2, status:1 })
const rules: FormRules<UserForm> = {
  tenant_id: [{ required:true, message:'请输入租户ID', trigger:'blur' }],
  username:  [{ required:true, message:'请输入用户名', trigger:'blur' }],
  password:  [{ required:true, message:'请输入密码',   trigger:'blur' }],
}

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const params: Record<string, unknown> = { ...query }
    if (!params.username) delete params.username
    if (!params.tenant_id) delete params.tenant_id
    if (params.status === null) delete params.status
    const res = await getUserList(params)
    tableData.value = res.data.items; total.value = res.data.total
  } finally { loading.value = false }
}

function resetQuery(): void { Object.assign(query,{page:1,page_size:10,username:'',tenant_id:'',status:null}); loadData() }

function openDialog(row: UserInfo | null = null): void {
  editRow.value = row
  if (row) Object.assign(form, { tenant_id:row.tenant_id, username:row.username, password:'', real_name:row.real_name??'', email:row.email??'', phone:row.phone??'', user_type:row.user_type, status:row.status })
  else Object.assign(form, { tenant_id:'default', username:'', password:'', real_name:'', email:'', phone:'', user_type:2, status:1 })
  dialogVisible.value = true; formRef.value?.clearValidate()
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editRow.value) await updateUser(editRow.value.id, { real_name:form.real_name, email:form.email, phone:form.phone, user_type:form.user_type, status:form.status })
    else await createUser({ ...form })
    ElMessage.success(editRow.value?'更新成功':'创建成功'); dialogVisible.value=false; loadData()
  } finally { submitting.value=false }
}

async function handleDelete(id: number): Promise<void> {
  await ElMessageBox.confirm('确认删除该用户？','警告',{type:'warning'})
  await deleteUser(id); ElMessage.success('删除成功'); loadData()
}

onMounted(loadData)
</script>
