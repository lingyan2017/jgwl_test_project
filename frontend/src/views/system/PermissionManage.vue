<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :model="query" inline>
        <el-form-item label="权限名称"><el-input v-model="query.perm_name" placeholder="请输入" clearable style="width:180px" /></el-form-item>
        <el-form-item label="权限类型">
          <el-select v-model="query.perm_type" placeholder="全部" clearable style="width:120px">
            <el-option label="菜单" :value="1" /><el-option label="按钮" :value="2" /><el-option label="接口" :value="3" />
          </el-select>
        </el-form-item>
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
          <span>权限列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增权限</el-button>
        </div>
      </template>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id"           label="ID"     width="70" />
        <el-table-column prop="perm_code"    label="权限编码" width="200" />
        <el-table-column prop="perm_name"    label="权限名称" width="150" />
        <el-table-column prop="perm_type"    label="类型"    width="80">
          <template #default="{row}">
            <el-tag size="small" :type="row.perm_type===1?'primary':row.perm_type===2?'warning':'success'">
              {{['','菜单','按钮','接口'][row.perm_type]||'-'}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_url" label="资源URL" />
        <el-table-column prop="method"       label="HTTP方法" width="100" />
        <el-table-column prop="status"       label="状态"    width="80">
          <template #default="{row}"><el-tag size="small" :type="row.status===1?'success':'danger'">{{row.status===1?'启用':'禁用'}}</el-tag></template>
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

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑权限':'新增权限'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="权限编码" prop="perm_code"><el-input v-model="form.perm_code" :disabled="!!editRow" /></el-form-item>
        <el-form-item label="权限名称" prop="perm_name"><el-input v-model="form.perm_name" /></el-form-item>
        <el-form-item label="权限类型">
          <el-select v-model="form.perm_type" style="width:100%">
            <el-option label="菜单" :value="1" /><el-option label="按钮" :value="2" /><el-option label="接口" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源URL"><el-input v-model="form.resource_url" placeholder="/api/v1/..." /></el-form-item>
        <el-form-item label="HTTP方法">
          <el-select v-model="form.method" clearable style="width:100%">
            <el-option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :label="m" :value="m" />
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
import { getPermissionList, createPermission, updatePermission, deletePermission } from '@/api/permission'

const loading=ref(false); const submitting=ref(false)
const tableData=ref([]); const total=ref(0)
const dialogVisible=ref(false); const editRow=ref(null); const formRef=ref()

const query=reactive({page:1,page_size:10,perm_name:'',perm_type:null,status:null})
const form=reactive({perm_code:'',perm_name:'',perm_type:3,resource_url:'',method:'GET',status:1})
const rules={perm_code:[{required:true,message:'必填',trigger:'blur'}],perm_name:[{required:true,message:'必填',trigger:'blur'}]}

async function loadData(){
  loading.value=true
  try{
    const p={...query};if(!p.perm_name)delete p.perm_name;if(p.perm_type===null)delete p.perm_type;if(p.status===null)delete p.status
    const res=await getPermissionList(p);tableData.value=res.data.items;total.value=res.data.total
  }finally{loading.value=false}
}
function resetQuery(){Object.assign(query,{page:1,page_size:10,perm_name:'',perm_type:null,status:null});loadData()}
function openDialog(row=null){
  editRow.value=row
  if(row) Object.assign(form,{perm_code:row.perm_code,perm_name:row.perm_name,perm_type:row.perm_type,resource_url:row.resource_url||'',method:row.method||'GET',status:row.status})
  else Object.assign(form,{perm_code:'',perm_name:'',perm_type:3,resource_url:'',method:'GET',status:1})
  dialogVisible.value=true;formRef.value?.clearValidate()
}
async function handleSubmit(){
  await formRef.value?.validate();submitting.value=true
  try{
    const payload={...form};if(!payload.resource_url)payload.resource_url=null;if(!payload.method)payload.method=null
    if(editRow.value) await updatePermission(editRow.value.id,{perm_name:payload.perm_name,perm_type:payload.perm_type,resource_url:payload.resource_url,method:payload.method,status:payload.status})
    else await createPermission(payload)
    ElMessage.success(editRow.value?'更新成功':'创建成功');dialogVisible.value=false;loadData()
  }finally{submitting.value=false}
}
async function handleDelete(id){await ElMessageBox.confirm('确认删除？','警告',{type:'warning'});await deletePermission(id);ElMessage.success('删除成功');loadData()}
onMounted(loadData)
</script>
