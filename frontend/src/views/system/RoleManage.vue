<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :model="query" inline>
        <el-form-item label="租户ID"><el-input v-model="query.tenant_id" placeholder="请输入" clearable style="width:150px" /></el-form-item>
        <el-form-item label="角色名称"><el-input v-model="query.role_name" placeholder="请输入" clearable style="width:180px" /></el-form-item>
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
          <span>角色列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增角色</el-button>
        </div>
      </template>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id"         label="ID"    width="70" />
        <el-table-column prop="role_name"  label="角色名称" width="160" />
        <el-table-column prop="role_key"   label="角色标识" width="160" />
        <el-table-column prop="tenant_id"  label="租户"  width="120" />
        <el-table-column prop="role_sort"  label="排序"  width="80" />
        <el-table-column prop="data_scope" label="数据范围" width="110">
          <template #default="{row}">
            {{ {1:'全部数据',2:'自定义',3:'本部门',4:'本部门及以下'}[row.data_scope] }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
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

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑角色':'新增角色'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="租户ID"   prop="tenant_id"><el-input v-model="form.tenant_id" :disabled="!!editRow" /></el-form-item>
        <el-form-item label="角色名称" prop="role_name"><el-input v-model="form.role_name" /></el-form-item>
        <el-form-item label="角色标识" prop="role_key"><el-input v-model="form.role_key" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.role_sort" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="数据范围">
          <el-select v-model="form.data_scope" style="width:100%">
            <el-option label="全部数据" :value="1" /><el-option label="自定义数据" :value="2" />
            <el-option label="本部门数据" :value="3" /><el-option label="本部门及以下" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="菜单权限">
          <el-tree
            ref="menuTreeRef"
            :data="menuTree"
            show-checkbox
            node-key="id"
            :default-checked-keys="form.menu_ids"
            :props="{ children: 'children', label: 'menu_name' }"
            style="border:1px solid #ddd;border-radius:4px;padding:8px;width:100%"
          />
        </el-form-item>
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
import { getRoleList, createRole, updateRole, deleteRole, getRole } from '@/api/role'
import { getMenuTree } from '@/api/menu'
import type { FormInstance, FormRules } from 'element-plus'
import type { RoleInfo, MenuInfo } from '@/types'

const loading=ref<boolean>(false); const submitting=ref<boolean>(false)
const tableData=ref<RoleInfo[]>([]); const total=ref<number>(0)
const dialogVisible=ref<boolean>(false); const editRow=ref<RoleInfo|null>(null); const formRef=ref<FormInstance>(); const menuTreeRef=ref()
const menuTree=ref<MenuInfo[]>([])

const query=reactive({page:1,page_size:10,tenant_id:'',role_name:'',status:null})
const form=reactive({tenant_id:'default',role_name:'',role_key:'',role_sort:0,data_scope:1,remark:'',status:1,menu_ids:[]})
const rules={tenant_id:[{required:true,message:'必填',trigger:'blur'}],role_name:[{required:true,message:'必填',trigger:'blur'}],role_key:[{required:true,message:'必填',trigger:'blur'}]}

async function loadData(){
  loading.value=true
  try{const p={...query};if(!p.tenant_id)delete p.tenant_id;if(!p.role_name)delete p.role_name;if(p.status===null)delete p.status;const res=await getRoleList(p);tableData.value=res.data.items;total.value=res.data.total}
  finally{loading.value=false}
}
function resetQuery(){Object.assign(query,{page:1,page_size:10,tenant_id:'',role_name:'',status:null});loadData()}

async function openDialog(row: RoleInfo | null = null): Promise<void> {
  editRow.value=row
  const tree=await getMenuTree();menuTree.value=tree.data
  if(row){
    const detail=await getRole(row.id)
    Object.assign(form,{tenant_id:row.tenant_id,role_name:row.role_name,role_key:row.role_key,role_sort:row.role_sort,data_scope:row.data_scope,remark:row.remark||'',status:row.status,menu_ids:detail.data.menu_ids||[]})
  } else {
    Object.assign(form,{tenant_id:'default',role_name:'',role_key:'',role_sort:0,data_scope:1,remark:'',status:1,menu_ids:[]})
  }
  dialogVisible.value=true;formRef.value?.clearValidate()
}

async function handleSubmit(){
  await formRef.value?.validate();submitting.value=true
  try{
    const checkedIds=menuTreeRef.value?.getCheckedKeys(false)||[]
    const halfCheckedIds=menuTreeRef.value?.getHalfCheckedKeys()||[]
    const allMenuIds=[...new Set([...checkedIds,...halfCheckedIds])]
    if(editRow.value) await updateRole(editRow.value.id,{role_name:form.role_name,role_key:form.role_key,role_sort:form.role_sort,data_scope:form.data_scope,remark:form.remark,status:form.status,menu_ids:allMenuIds})
    else await createRole({...form,menu_ids:allMenuIds})
    ElMessage.success(editRow.value?'更新成功':'创建成功');dialogVisible.value=false;loadData()
  }finally{submitting.value=false}
}
async function handleDelete(id: number): Promise<void> {await ElMessageBox.confirm('确认删除？','警告',{type:'warning'});await deleteRole(id);ElMessage.success('删除成功');loadData()}
onMounted(loadData)
</script>
