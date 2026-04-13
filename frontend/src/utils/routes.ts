import type { RouteRecordRaw } from 'vue-router'
import type { MenuInfo } from '@/types'

// 组件映射表：将数据库中的 component 路径映射到实际的 Vue 组件
const componentMap: Record<string, any> = {
  // 布局组件
  Layout: () => import('@/layout/index.vue'),
  
  // 系统管理
  'system/TenantManage': () => import('@/views/system/TenantManage.vue'),
  'system/UserManage': () => import('@/views/system/UserManage.vue'),
  'system/DeptManage': () => import('@/views/system/DeptManage.vue'),
  'system/PostManage': () => import('@/views/system/PostManage.vue'),
  'system/RoleManage': () => import('@/views/system/RoleManage.vue'),
  'system/MenuManage': () => import('@/views/system/MenuManage.vue'),
  'system/PermissionManage': () => import('@/views/system/PermissionManage.vue'),
  
  // 测试管理
  'system/TestQueryDataManage': () => import('@/views/system/TestQueryDataManage.vue'),
  'system/SysConfigManage': () => import('@/views/system/SysConfigManage.vue'),
  
  // 其他页面
  Dashboard: () => import('@/views/Dashboard.vue'),
}

/**
 * 根据菜单数据生成路由配置
 */
export function generateRoutes(menus: MenuInfo[]): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []
  
  // 只处理顶级菜单（parent_id === 0）
  const topMenus = menus.filter(menu => menu.parent_id === 0)
  
  topMenus.forEach(menu => {
    const route = menuToRoute(menu, menus)
    if (route) {
      // 如果顶级路由有 children 但没有 component，添加 Layout 组件
      if (route.children && !route.component) {
        route.component = componentMap['Layout']
      }
      routes.push(route)
    }
  })
  
  return routes
}

/**
 * 将单个菜单项转换为路由配置
 */
function menuToRoute(menu: MenuInfo, allMenus: MenuInfo[], parentPath?: string): RouteRecordRaw | null {
  // 如果菜单不可见或禁用，则不生成路由
  if (menu.visible === 0 || menu.status === 0) {
    return null
  }
  
  // 查找当前菜单的子菜单
  const children = allMenus
    .filter(m => m.parent_id === menu.id)
    .map(child => menuToRoute(child, allMenus, menu.path || undefined))
    .filter((r): r is RouteRecordRaw => r !== null)
  
  // 构建基础路由配置
  // 如果有父级路径，需要构建完整路径（因为所有路由都作为顶级路由添加）
  const fullPath = parentPath 
    ? `${parentPath}/${menu.path || menu.id}`
    : (menu.path || `/${menu.id}`)
  
  const routeConfig: any = {
    path: fullPath,
    name: menu.menu_name,
    meta: {
      title: menu.menu_name,
      icon: menu.icon,
      menuId: menu.id,
    },
  }
  
  // 如果有子菜单
  if (children.length > 0) {
    routeConfig.children = children
    
    // 如果父菜单没有组件，需要设置 redirect 到第一个子菜单
    if (!menu.component || menu.component === 'Layout') {
      // 找到第一个有路径的子菜单
      const firstChild = children.find(c => c.path)
      if (firstChild && firstChild.path) {
        // 确保 redirect 路径正确
        const redirectPath = firstChild.path.startsWith('/') 
          ? firstChild.path 
          : `${routeConfig.path}/${firstChild.path}`
        routeConfig.redirect = redirectPath
      }
    }
  }
  
  // 如果有组件路径，则添加 component
  if (menu.component && menu.component !== 'Layout') {
    const componentLoader = componentMap[menu.component]
    if (componentLoader) {
      routeConfig.component = componentLoader
    } else {
      console.warn(`未找到组件: ${menu.component}`)
      return null
    }
  }
  
  return routeConfig as RouteRecordRaw
}

/**
 * 从 localStorage 恢复菜单数据
 */
export function getStoredMenus(): MenuInfo[] {
  try {
    const menusStr = localStorage.getItem('menus')
    return menusStr ? JSON.parse(menusStr) : []
  } catch (error) {
    console.error('解析菜单数据失败:', error)
    return []
  }
}
