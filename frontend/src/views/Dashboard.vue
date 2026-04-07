<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card" :style="{ borderTop: `3px solid ${card.color}` }">
          <div class="stat-body">
            <div>
              <div class="stat-num">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
            <el-icon :size="40" :color="card.color"><component :is="card.icon" /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover">
      <template #header>
        <span>欢迎使用 JGWL 管理系统</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="当前用户">
          {{ authStore.user?.real_name || authStore.user?.username }}
        </el-descriptions-item>
        <el-descriptions-item label="所属租户">{{ authStore.user?.tenant_id }}</el-descriptions-item>
        <el-descriptions-item label="用户类型">
          <el-tag :type="authStore.user?.user_type === 0 ? 'danger' : 'primary'">
            {{ userTypeMap[authStore.user?.user_type] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getTenantList } from '@/api/tenant'
import { getUserList } from '@/api/user'
import { getRoleList } from '@/api/role'
import { getDeptList } from '@/api/dept'

const authStore = useAuthStore()
const userTypeMap = { 0: '超级管理员', 1: '租户管理员', 2: '普通用户' }

const statCards = ref([
  { title: '租户数量', value: 0, icon: 'OfficeBuilding', color: '#1890ff' },
  { title: '用户数量', value: 0, icon: 'User',           color: '#52c41a' },
  { title: '角色数量', value: 0, icon: 'UserFilled',     color: '#fa8c16' },
  { title: '部门数量', value: 0, icon: 'Folder',         color: '#f5222d' },
])

onMounted(async () => {
  try {
    const [t, u, r, d] = await Promise.all([
      getTenantList({ page: 1, page_size: 1 }),
      getUserList({ page: 1, page_size: 1 }),
      getRoleList({ page: 1, page_size: 1 }),
      getDeptList({ page: 1, page_size: 1 }),
    ])
    statCards.value[0].value = t.data.total
    statCards.value[1].value = u.data.total
    statCards.value[2].value = r.data.total
    statCards.value[3].value = d.data.total
  } catch {}
})
</script>

<style scoped>
.dashboard { padding: 0; }
.stat-card { cursor: default; }
.stat-body { display: flex; align-items: center; justify-content: space-between; }
.stat-num { font-size: 36px; font-weight: bold; color: #333; }
.stat-title { font-size: 14px; color: #999; margin-top: 4px; }
</style>
