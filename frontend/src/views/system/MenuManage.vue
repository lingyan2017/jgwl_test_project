<template>
  <div>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :model="query" inline>
        <el-form-item label="菜单名称"><el-input v-model="query.menu_name" placeholder="请输入" clearable style="width:180px" /></el-form-item>
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
          <span>菜单列表</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()">新增菜单</el-button>
        </div>
      </template>
      
      <!-- 树形菜单结构 -->
      <el-table 
        :data="treeData" 
        border 
        stripe 
        v-loading="loading"
        row-key="id"
        :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
      >
        <el-table-column prop="menu_name" label="菜单名称" width="200">
          <template #default="{row}">
            <span>{{ row.menu_name }}</span>
            <el-tag 
              size="small" 
              :type="row.menu_type===1?'info':row.menu_type===2?'primary':'warning'" 
              style="margin-left: 8px;"
            >
              {{['','目录','菜单','按钮'][row.menu_type]||'-'}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path"      label="路由路径" width="180" />
        <el-table-column prop="component" label="组件路径" width="200" />
        <el-table-column prop="icon"      label="图标" width="100" />
        <el-table-column prop="order_num" label="排序" width="70" />
        <el-table-column prop="perms"     label="权限标识" width="150" />
        <el-table-column prop="visible"   label="显示" width="70">
          <template #default="{row}">
            <el-tag size="small" :type="row.visible===1?'success':'info'">
              {{row.visible===1?'显示':'隐藏'}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status"    label="状态" width="70">
          <template #default="{row}">
            <el-tag size="small" :type="row.status===1?'success':'danger'">
              {{row.status===1?'启用':'禁用'}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" text @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger"  text @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editRow?'编辑菜单':'新增菜单'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="父菜单ID"><el-input-number v-model="form.parent_id" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="菜单名称" prop="menu_name"><el-input v-model="form.menu_name" /></el-form-item>
        <el-form-item label="菜单类型">
          <el-radio-group v-model="form.menu_type">
            <el-radio :value="1">目录</el-radio><el-radio :value="2">菜单</el-radio><el-radio :value="3">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="路由路径"><el-input v-model="form.path" /></el-form-item>
        <el-form-item label="组件路径"><el-input v-model="form.component" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="form.icon" /></el-form-item>
        <el-form-item label="权限标识"><el-input v-model="form.perms" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.order_num" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="显示状态">
          <el-radio-group v-model="form.visible"><el-radio :value="1">显示</el-radio><el-radio :value="0">隐藏</el-radio></el-radio-group>
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
import { getMenuList, createMenu, updateMenu, deleteMenu } from '@/api/menu'
import type { FormInstance, FormRules } from 'element-plus'
import type { MenuInfo } from '@/types'

const loading=ref<boolean>(false); const submitting=ref<boolean>(false)
const tableData=ref<MenuInfo[]>([]); const treeData=ref<MenuInfo[]>([]); const total=ref<number>(0)
const dialogVisible=ref<boolean>(false); const editRow=ref<MenuInfo|null>(null); const formRef=ref<FormInstance>()

const query=reactive({page:1,page_size:10,menu_name:'',status:null})
const form=reactive({parent_id:0,menu_name:'',menu_type:2,path:'',component:'',icon:'',order_num:0,perms:'',is_frame:0,visible:1,status:1})
const rules={menu_name:[{required:true,message:'必填',trigger:'blur'}]}

async function loadData(){
  loading.value=true
  try{
    // 获取所有菜单数据（不分页）
    const p: Record<string,unknown> = { page: 1, page_size: 9999 }; // 获取所有数据
    if(query.menu_name) p.menu_name = query.menu_name;
    if(query.status !== null) p.status = query.status;
    
    const res = await getMenuList(p);
    tableData.value = res.data.items;
    // 构建树形结构
    treeData.value = buildTree(res.data.items);
  }
  finally{loading.value=false}
}

// 构建树形结构
function buildTree(data: MenuInfo[]): MenuInfo[] {
  // 先按 parent_id 分组
  const map: Record<number, MenuInfo> = {};
  const roots: MenuInfo[] = [];

  // 创建映射
  data.forEach(item => {
    map[item.id] = { ...item, children: [] };
  });

  // 构建树结构
  data.forEach(item => {
    const node = map[item.id];
    if (item.parent_id === 0) {
      // 根节点
      roots.push(node);
    } else {
      // 查找父节点并添加为子节点
      const parent = map[item.parent_id];
      if (parent) {
        if (!parent.children) parent.children = [];
        parent.children.push(node);
      }
    }
  });

  // 对每个节点的子节点按 order_num 排序
  const sortChildren = (nodes: MenuInfo[]) => {
    nodes.sort((a, b) => (a.order_num || 0) - (b.order_num || 0));
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        sortChildren(node.children);
      }
    });
  };

  sortChildren(roots);
  
  return roots;
}
function resetQuery(){
  Object.assign(query, {page:1, page_size:10, menu_name:'', status:null});
  loadData()
}
function openDialog(row: MenuInfo | null = null): void {
  editRow.value=row
  if(row) Object.assign(form,{parent_id:row.parent_id,menu_name:row.menu_name,menu_type:row.menu_type||2,path:row.path||'',component:row.component||'',icon:row.icon||'',order_num:row.order_num,perms:row.perms||'',is_frame:row.is_frame,visible:row.visible,status:row.status})
  else Object.assign(form,{parent_id:0,menu_name:'',menu_type:2,path:'',component:'',icon:'',order_num:0,perms:'',is_frame:0,visible:1,status:1})
  dialogVisible.value=true;formRef.value?.clearValidate()
}
async function handleSubmit(){
  await formRef.value?.validate();submitting.value=true
  try{
    const payload: Record<string, unknown> = {...form};Object.keys(payload).forEach(k=>{if((payload as Record<string,unknown>)[k]==='')(payload as Record<string,unknown>)[k]=null})
    payload.menu_name=form.menu_name;payload.parent_id=form.parent_id;payload.menu_type=form.menu_type;payload.order_num=form.order_num;payload.visible=form.visible;payload.status=form.status
    if(editRow.value) await updateMenu(editRow.value.id,payload)
    else await createMenu(payload)
    ElMessage.success(editRow.value?'更新成功':'创建成功');dialogVisible.value=false;loadData()
  }finally{submitting.value=false}
}
async function handleDelete(id: number): Promise<void> {await ElMessageBox.confirm('确认删除？','警告',{type:'warning'});await deleteMenu(id);ElMessage.success('删除成功');loadData()}
onMounted(loadData)
</script>