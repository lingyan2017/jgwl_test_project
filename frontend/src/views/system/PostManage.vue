<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :model="query" inline>
        <el-form-item label="租户ID"><el-input v-model="query.tenant_id" placeholder="请输入" clearable style="width:150px" /></el-form-item>
        <el-form-item label="岗位名称"><el-input v-model="query.post_name" placeholder="请输入" clearable style="width:180px" /></el-form-item>
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
          <span>岗位列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增岗位</el-button>
        </div>
      </template>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id"        label="ID"    width="70" />
        <el-table-column prop="post_code" label="岗位编码" width="140" />
        <el-table-column prop="post_name" label="岗位名称" />
        <el-table-column prop="tenant_id" label="租户"  width="120" />
        <el-table-column prop="post_sort" label="排序"  width="80" />
        <el-table-column prop="remark"    label="备注" />
        <el-table-column prop="status"    label="状态"  width="80">
          <template #default="{row}"><el-tag :type="row.status===1?'success':'danger'">{{row.status===1?'启用':'禁用'}}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger"  text @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" style="margin-top:16px;justify-content:flex-end" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑岗位':'新增岗位'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
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
        <el-form-item label="岗位编码" prop="post_code"><el-input v-model="form.post_code" /></el-form-item>
        <el-form-item label="岗位名称" prop="post_name"><el-input v-model="form.post_name" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.post_sort" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
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
import { getPostList, createPost, updatePost, deletePost } from '@/api/post'
import { getTenantList } from '@/api/tenant'
import { useAuthStore } from '@/stores/auth'
import type { PostInfo } from '@/types'

const authStore = useAuthStore()

const loading=ref<boolean>(false); const submitting=ref<boolean>(false)
const tableData=ref<PostInfo[]>([]); const total=ref<number>(0)
const dialogVisible=ref<boolean>(false); const editRow=ref<PostInfo|null>(null); const formRef=ref<FormInstance>()

interface TenantIdOption { value: string; label: string; tenantName: string }
const tenantIdOptions = ref<TenantIdOption[]>([])
const tenantIdLoading = ref<boolean>(false)

interface PostQuery { page: number; page_size: number; tenant_id: string; post_name: string; status: number | null }
interface PostForm { tenant_id: string; post_code: string; post_name: string; post_sort: number; remark: string; status: number }

const query=reactive<PostQuery>({page:1,page_size:10,tenant_id:'',post_name:'',status:null})
const form=reactive<PostForm>({tenant_id:'',post_code:'',post_name:'',post_sort:0,remark:'',status:1})
const rules: FormRules<PostForm> = {
  tenant_id: [{ required:true, message:'请选择租户ID', trigger:'change' }],
  post_code: [{ required:true, message:'必填', trigger:'blur' }],
  post_name: [{ required:true, message:'必填', trigger:'blur' }],
}

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

async function loadData(): Promise<void> {
  loading.value=true
  try {
    const p: Record<string,unknown>={...query}; if(!p.tenant_id) delete p.tenant_id; if(!p.post_name) delete p.post_name; if(p.status===null) delete p.status
    const res=await getPostList(p); tableData.value=res.data.items; total.value=res.data.total
  } finally { loading.value=false }
}

function resetQuery(): void { Object.assign(query,{page:1,page_size:10,tenant_id:'',post_name:'',status:null}); loadData() }

async function openDialog(row: PostInfo | null = null): Promise<void> {
  editRow.value=row
  if (row) {
    Object.assign(form,{tenant_id:row.tenant_id,post_code:row.post_code,post_name:row.post_name,post_sort:row.post_sort,remark:row.remark??'',status:row.status})
  } else {
    Object.assign(form,{tenant_id:'',post_code:'',post_name:'',post_sort:0,remark:'',status:1})
    await loadTenantIdOptions()
  }
  dialogVisible.value=true; formRef.value?.clearValidate()
}

async function handleSubmit(): Promise<void> {
  await formRef.value?.validate(); submitting.value=true
  try {
    if(editRow.value) await updatePost(editRow.value.id,{post_code:form.post_code,post_name:form.post_name,post_sort:form.post_sort,remark:form.remark,status:form.status})
    else await createPost({...form})
    ElMessage.success(editRow.value?'更新成功':'创建成功'); dialogVisible.value=false; loadData()
  } finally { submitting.value=false }
}

async function handleDelete(id: number): Promise<void> {
  await ElMessageBox.confirm('确认删除？','警告',{type:'warning'})
  await deletePost(id); ElMessage.success('删除成功'); loadData()
}

onMounted(loadData)
</script>
