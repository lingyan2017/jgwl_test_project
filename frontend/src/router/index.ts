import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { generateRoutes, getStoredMenus } from '@/utils/routes'

// 基础路由（不需要权限控制的路由）
const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
]

// 主布局路由（登录后动态添加子路由）
export const mainRoute: RouteRecordRaw = {
  path: '/',
  name: 'MainLayout',  // 添加 name，用于 addRoute
  component: () => import('@/layout/index.vue'),
  redirect: '/dashboard',
  meta: { requiresAuth: true },
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { title: '首页' },
    },
  ],
}

const router = createRouter({
  history: createWebHistory(),
  routes: [...constantRoutes, mainRoute],
})

// 标记是否已经添加过动态路由
let hasAddedRoutes = false

router.beforeEach(async (to, from) => {
  const auth = useAuthStore()

  console.log('[Router Guard]', { 
    to: to.path, 
    from: from.path,
    hasToken: !!auth.token,
    hasAddedRoutes,
    menusCount: auth.menus.length
  })

  // 未登录跳登录页
  if (to.meta.requiresAuth !== false && !auth.token) {
    console.log('[Router Guard] 未登录，跳转到登录页')
    return '/login'
  }

  // 如果访问登录页且已登录，跳转到首页
  if (to.path === '/login' && auth.token) {
    console.log('[Router Guard] 已登录，从登录页跳转到首页')
    return '/'
  }

  // 已登录但未加载菜单，先加载菜单和动态路由
  if (auth.token && !hasAddedRoutes && to.path !== '/login') {
    try {
      console.log('[Router Guard] 开始加载动态菜单...')
      
      // 尝试从 localStorage 恢复菜单
      const storedMenus = getStoredMenus()
      if (storedMenus.length > 0) {
        console.log('[Router Guard] 从缓存恢复菜单:', storedMenus.length, '个')
        auth.menus = storedMenus
      } else {
        // 如果没有缓存，则获取用户信息和菜单
        console.log('[Router Guard] 从服务器获取菜单...')
        await auth.fetchMe()
        await auth.fetchMenus()
        console.log('[Router Guard] 从服务器获取菜单成功:', auth.menus.length, '个')
      }
      
      // 生成动态路由并添加
      const dynamicRoutes = generateRoutes(auth.menus)
      console.log('[Router Guard] 生成动态路由:', dynamicRoutes.length, '个')
      console.log('[Router Guard] 路由详情:', JSON.stringify(dynamicRoutes.map(r => ({ 
        path: r.path, 
        name: r.name,
        hasChildren: !!r.children,
        hasComponent: !!r.component,
        redirect: r.redirect
      })), null, 2))
      
      dynamicRoutes.forEach(route => {
        try {
          // 所有动态路由都作为顶级路由添加（因为它们已经有完整路径）
          router.addRoute(route)
          console.log('[Router Guard] ✓ 添加路由:', route.path, '->', route.name)
          
          if (route.children) {
            console.log('[Router Guard]   子路由数量:', route.children.length)
            console.log('[Router Guard]   子路由路径:', route.children.map((c: any) => c.path))
            console.log('[Router Guard]   是否有component:', !!route.component)
          }
        } catch (error) {
          console.error('[Router Guard] ✗ 添加路由失败:', route.path, error)
        }
      })
      
      // 打印所有当前路由
      console.log('[Router Guard] 当前所有路由:', router.getRoutes().map(r => ({
        path: r.path,
        name: r.name,
        parent: r.meta?.parentPath
      })))
      
      hasAddedRoutes = true
      console.log('[Router Guard] ✓ 动态路由添加成功，标记 hasAddedRoutes = true')
      
      // 重要：不要 return，让导航继续，否则会导致重复触发守卫
      // return { ...to, replace: true }
    } catch (error) {
      console.error('[Router Guard] ✗ 加载菜单失败:', error)
      auth.logout()
      hasAddedRoutes = false
      return '/login'
    }
  }
  
  // 正常继续导航
  console.log('[Router Guard] 允许导航到:', to.path)
})

export default router