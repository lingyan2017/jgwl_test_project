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
          <!-- 首页菜单项 -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>

          <!-- 动态菜单项 -->
          <template v-if="menuTree.length > 0">
            <template v-for="menu in menuTree" :key="menu.id">
              <el-menu-item 
                v-if="menu.menu_type === 2" 
                :index="`/${menu.path}`"
              >
                <el-icon v-if="menu.icon">
                  <component :is="getIconComponent(menu.icon)" />
                </el-icon>
                <template #title>{{ menu.menu_name }}</template>
              </el-menu-item>
              
              <el-sub-menu 
                v-else-if="menu.menu_type === 1 && menu.children && menu.children.length > 0" 
                :index="`/${menu.path}`"
              >
                <template #title>
                  <el-icon v-if="menu.icon">
                    <component :is="getIconComponent(menu.icon)" />
                  </el-icon>
                  <span>{{ menu.menu_name }}</span>
                </template>
                
                <template v-for="child in menu.children" :key="child.id">
                  <el-menu-item 
                    v-if="child.menu_type === 2" 
                    :index="`/${menu.path}/${child.path}`"
                  >
                    <el-icon v-if="child.icon">
                      <component :is="getIconComponent(child.icon)" />
                    </el-icon>
                    <template #title>{{ child.menu_name }}</template>
                  </el-menu-item>
                  
                  <el-sub-menu 
                    v-else-if="child.menu_type === 1 && child.children && child.children.length > 0" 
                    :index="`/${menu.path}/${child.path}`"
                  >
                    <template #title>
                      <el-icon v-if="child.icon">
                        <component :is="getIconComponent(child.icon)" />
                      </el-icon>
                      <span>{{ child.menu_name }}</span>
                    </template>
                    
                    <template v-for="grandChild in child.children" :key="grandChild.id">
                      <el-menu-item 
                        v-if="grandChild.menu_type === 2" 
                        :index="`/${menu.path}/${child.path}/${grandChild.path}`"
                      >
                        <el-icon v-if="grandChild.icon">
                          <component :is="getIconComponent(grandChild.icon)" />
                        </el-icon>
                        <template #title>{{ grandChild.menu_name }}</template>
                      </el-menu-item>
                    </template>
                  </el-sub-menu>
                </template>
              </el-sub-menu>
            </template>
          </template>
          <!-- 当没有动态菜单时，显示默认菜单项 -->
          <template v-else-if="!loadingMenus">
            <el-sub-menu v-if="isAdmin" index="/system">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统管理</span>
              </template>
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
              <el-menu-item v-if="isSuperAdmin" index="/system/menu">
                <el-icon><Menu /></el-icon>
                <template #title>菜单管理</template>
              </el-menu-item>
              <el-menu-item v-if="isSuperAdmin" index="/system/permission">
                <el-icon><Lock /></el-icon>
                <template #title>权限管理</template>
              </el-menu-item>
            </el-sub-menu>
            
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
          </template>
          <el-menu-item v-else>
            <el-icon><Loading /></el-icon>
            <template #title>加载中...</template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import { getUserMenus } from '@/api/menu'
import type { MenuInfo } from '@/types'

// 导入Element Plus图标
import { HomeFilled, Setting, OfficeBuilding, User, Folder, Postcard, UserFilled, Menu as MenuIcon, Lock, Document, Expand, Fold, ArrowDown, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapse = ref<boolean>(false)
const menuTree = ref<MenuInfo[]>([])
const loadingMenus = ref<boolean>(true)

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

// 加载用户菜单
onMounted(() => {
  loadUserMenus()
})

// 加载用户菜单
async function loadUserMenus() {
  loadingMenus.value = true
  try {
    const res = await getUserMenus()
    if (res.code === 0) {
      menuTree.value = res.data || []
      console.log('用户菜单加载成功:', res.data)
    } else {
      console.error('获取用户菜单失败:', res.msg)
      // 即使API返回错误，也不清空菜单树，保持原有内容或显示默认内容
    }
  } catch (error) {
    console.error('加载用户菜单失败:', error)
    // 发生错误时不中断UI，仍然显示默认菜单
  } finally {
    loadingMenus.value = false
  }
}

// 获取图标组件
function getIconComponent(iconName: string) {
  // 映射后端传来的图标名称到Element Plus图标
  const iconMap: Record<string, any> = {
    'HomeFilled': HomeFilled,
    'Setting': Setting,
    'OfficeBuilding': OfficeBuilding,
    'User': User,
    'Folder': Folder,
    'Postcard': Postcard,
    'UserFilled': UserFilled,
    'Menu': MenuIcon,
    'Lock': Lock,
    'Document': Document,
    'Expand': Expand,
    'Fold': Fold,
    'ArrowDown': ArrowDown,
    // 添加其他可能的图标映射
    'home': HomeFilled,
    'setting': Setting,
    'office-building': OfficeBuilding,
    'user': User,
    'folder': Folder,
    'postcard': Postcard,
    'user-filled': UserFilled,
    'menu': MenuIcon,
    'lock': Lock,
    'document': Document,
  }
  
  return iconMap[iconName] || MenuIcon // 默认返回Menu图标
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