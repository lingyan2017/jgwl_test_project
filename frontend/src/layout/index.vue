<template>
  <el-container class="layout-wrapper">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon size="24"><Setting /></el-icon>
        <span v-if="!isCollapse" class="logo-text">JGWL 管理系统</span>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#001529"
          text-color="#ffffffa6"
          active-text-color="#ffffff"
          router
        >
          <!-- 所有用户可见 -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>

          <!-- 仅管理员(user_type <= 1)可见 -->
          <el-sub-menu v-if="isAdmin" index="/system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>

            <!-- 仅超级管理员可见 -->
            <el-menu-item v-if="isSuperAdmin" index="/system/tenant">
              <el-icon><OfficeBuilding /></el-icon>
              <template #title>租户管理</template>
            </el-menu-item>

            <el-menu-item index="/system/user">
              <el-icon><User /></el-icon>
              <template #title>用户管理</template>
            </el-menu-item>
            <el-menu-item index="/system/dept">
              <el-icon><Folder /></el-icon>
              <template #title>部门管理</template>
            </el-menu-item>
            <el-menu-item index="/system/post">
              <el-icon><Postcard /></el-icon>
              <template #title>岗位管理</template>
            </el-menu-item>
            <el-menu-item index="/system/role">
              <el-icon><UserFilled /></el-icon>
              <template #title>角色管理</template>
            </el-menu-item>

            <!-- 仅超级管理员可见 -->
            <el-menu-item v-if="isSuperAdmin" index="/system/menu">
              <el-icon><Menu /></el-icon>
              <template #title>菜单管理</template>
            </el-menu-item>
            <el-menu-item v-if="isSuperAdmin" index="/system/permission">
              <el-icon><Lock /></el-icon>
              <template #title>权限管理</template>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 测试管理菜单 - 仅管理员(user_type <= 1)可见 -->
          <el-sub-menu v-if="isAdmin" index="/test">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>测试管理</span>
            </template>
            
            <el-menu-item index="/test/test-query-data">
              <el-icon><Document /></el-icon>
              <template #title>测试查询数据</template>
            </el-menu-item>
            <el-menu-item index="/test/sys-config">
              <el-icon><Setting /></el-icon>
              <template #title>系统配置</template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <!-- 顶部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" size="20" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag
            v-if="authStore.user"
            :type="authStore.user.user_type === 0 ? 'danger' : authStore.user.user_type === 1 ? 'warning' : 'info'"
            size="small"
            style="margin-right:12px"
          >
            {{ userTypeLabel }}
          </el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar size="small" :style="{ backgroundColor: '#1890ff' }">
                {{ userInitial }}
              </el-avatar>
              <span class="username">{{ authStore.user?.real_name || authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapse = ref<boolean>(false)

// 权限计算属性
const isSuperAdmin = computed(() => authStore.user?.user_type === 0)
const isAdmin = computed(() => (authStore.user?.user_type ?? 2) <= 1)

const userTypeLabel = computed(() => {
  const map: Record<number, string> = { 0: '超级管理员', 1: '租户管理员', 2: '普通用户' }
  return map[authStore.user?.user_type ?? 2]
})

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => (route.meta?.title as string) ?? '')
const userInitial = computed(() => {
  const name = authStore.user?.real_name ?? authStore.user?.username ?? 'U'
  return name.charAt(0).toUpperCase()
})

async function handleCommand(cmd: string): Promise<void> {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-wrapper { height: 100vh; }

.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  border-bottom: 1px solid #1f2d3d;
}

.logo-text {
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left { display: flex; align-items: center; gap: 16px; }
.collapse-btn { cursor: pointer; color: #666; }

.header-right { display: flex; align-items: center; }
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}
.username { font-size: 14px; }

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

:deep(.el-menu) { border-right: none; }
</style>