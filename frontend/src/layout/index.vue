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

          <!-- 动态菜单 -->
          <template v-for="menu in authStore.menus" :key="menu.id">
            <!-- 无子菜单 -->
            <el-menu-item 
              v-if="!menu.children || menu.children.length === 0" 
              :index="menu.path || `/${menu.id}`"
            >
              <el-icon v-if="menu.icon">
                <component :is="getIconComponent(menu.icon)" />
              </el-icon>
              <template #title>{{ menu.menu_name }}</template>
            </el-menu-item>
            
            <!-- 有子菜单 -->
            <el-sub-menu v-else :index="menu.path || `/${menu.id}`">
              <template #title>
                <el-icon v-if="menu.icon">
                  <component :is="getIconComponent(menu.icon)" />
                </el-icon>
                <span>{{ menu.menu_name }}</span>
              </template>
              
              <template v-for="child in menu.children" :key="child.id">
                <!-- 二级菜单 - 构建完整路径 -->
                <el-menu-item 
                  v-if="!child.children || child.children.length === 0"
                  :index="`${menu.path}/${child.path}`"
                >
                  <el-icon v-if="child.icon">
                    <component :is="getIconComponent(child.icon)" />
                  </el-icon>
                  <template #title>{{ child.menu_name }}</template>
                </el-menu-item>
                
                <!-- 三级菜单 -->
                <el-sub-menu v-else :index="`${menu.path}/${child.path}`">
                  <template #title>
                    <el-icon v-if="child.icon">
                      <component :is="getIconComponent(child.icon)" />
                    </el-icon>
                    <span>{{ child.menu_name }}</span>
                  </template>
                  
                  <el-menu-item 
                    v-for="grandChild in child.children" 
                    :key="grandChild.id"
                    :index="`${menu.path}/${child.path}/${grandChild.path}`"
                  >
                    <el-icon v-if="grandChild.icon">
                      <component :is="getIconComponent(grandChild.icon)" />
                    </el-icon>
                    <template #title>{{ grandChild.menu_name }}</template>
                  </el-menu-item>
                </el-sub-menu>
              </template>
            </el-sub-menu>
          </template>
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
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

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

// 获取图标组件
const getIconComponent = (iconName: string | null) => {
  if (!iconName) return null
  // 将数据库中的图标名称转换为 Element Plus 图标组件
  // 例如: 'HomeFilled' -> HomeFilled 组件
  return (ElementPlusIconsVue as any)[iconName] || null
}

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