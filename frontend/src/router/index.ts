import { createRouter, createWebHistory, type RouteRecordRaw, RouteRecordName } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getUserMenus } from '@/api/menu'
import type { MenuInfo } from '@/types'

// 静态路由
const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      // 基本页面路由
      { 
        path: 'dashboard', 
        name: 'Dashboard', 
        component: () => import('@/views/Dashboard.vue'), 
        meta: { title: '首页', requiresAuth: true } 
      },
      // 系统管理相关路由（作为后备路由）
      { 
        path: 'system/user', 
        name: 'SystemUser', 
        component: () => import('@/views/system/UserManage.vue'), 
        meta: { title: '用户管理', requiresAuth: true } 
      },
      { 
        path: 'system/role', 
        name: 'SystemRole', 
        component: () => import('@/views/system/RoleManage.vue'), 
        meta: { title: '角色管理', requiresAuth: true } 
      },
      { 
        path: 'system/menu', 
        name: 'SystemMenu', 
        component: () => import('@/views/system/MenuManage.vue'), 
        meta: { title: '菜单管理', requiresAuth: true } 
      },
      { 
        path: 'system/tenant', 
        name: 'SystemTenant', 
        component: () => import('@/views/system/TenantManage.vue'), 
        meta: { title: '租户管理', requiresAuth: true } 
      },
      { 
        path: 'system/dept', 
        name: 'SystemDept', 
        component: () => import('@/views/system/DeptManage.vue'), 
        meta: { title: '部门管理', requiresAuth: true } 
      },
      { 
        path: 'system/post', 
        name: 'SystemPost', 
        component: () => import('@/views/system/PostManage.vue'), 
        meta: { title: '岗位管理', requiresAuth: true } 
      },
      { 
        path: 'system/permission', 
        name: 'SystemPermission', 
        component: () => import('@/views/system/PermissionManage.vue'), 
        meta: { title: '权限管理', requiresAuth: true } 
      },
      // 测试管理相关路由
      { 
        path: 'test/test-query-data', 
        name: 'TestQueryData', 
        component: () => import('@/views/system/TestQueryDataManage.vue'), 
        meta: { title: '测试查询数据', requiresAuth: true } 
      },
      { 
        path: 'test/sys-config', 
        name: 'SysConfig', 
        component: () => import('@/views/system/SysConfigManage.vue'), 
        meta: { title: '系统配置', requiresAuth: true } 
      },
      {
        path: 'test/trial-calculator',
        name: 'TrialCalculator',
        component: () => import('@/views/system/TrialCalculator.vue'),
        meta: { title: '试算测试', requiresAuth: true }
      },
      {
        path: 'test/payment-test',
        name: 'PaymentTest',
        component: () => import('@/views/system/PaymentTest.vue'),
        meta: { title: '支付测试', requiresAuth: true }
      },
      {
        path: 'test/system-config',
        name: 'SystemConfig',
        component: () => import('@/views/system/SystemConfigManage.vue'),
        meta: { title: '系统配置项', requiresAuth: true }
      },
    ], // 包含基本的子路由作为后备
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes,
})

// 动态加载组件
function loadView(viewPath: string) {
  // 如果是外部链接，则返回空白组件
  if (viewPath.startsWith('http')) {
    return () => import('@/views/ExternalLink.vue')
  }
  
  // 根据路径动态导入组件
  try {
    // 处理相对路径
    let path = viewPath
    if (path.startsWith('/')) {
      path = path.substring(1)
    }
    
    // 尝试导入指定路径的组件
    return () => import(`@/views/${path}.vue`).catch(() => {
      // 如果找不到具体组件，尝试导入目录下的index.vue
      return import(`@/views/${path}/index.vue`)
    })
  } catch (e) {
    console.error(`Failed to load view: ${viewPath}`, e)
    return () => import('@/views/NotFound.vue')
  }
}

let routesAdded = false;

// 添加动态路由
export function addDynamicRoutes() {
  return new Promise<void>((resolve, reject) => {
    // 如果已经添加过动态路由，则不再重复添加
    if (routesAdded) {
      console.log('Dynamic routes already added');
      resolve();
      return;
    }
    
    getUserMenus().then(res => {
      if (res.code === 0) {
        const menus = res.data || []

        // 将菜单树扁平化为路由列表，直接挂载到 Layout 下
        function flattenMenuRoutes(menus: MenuInfo[], parentPath = ''): RouteRecordRaw[] {
          const routes: RouteRecordRaw[] = []

          menus.forEach(menu => {
            const currentPath = parentPath ? `${parentPath}/${menu.path}` : menu.path || ''

            if (menu.menu_type === 1) {
              // 目录：不创建路由，只递归子菜单
              if (menu.children && menu.children.length > 0) {
                routes.push(...flattenMenuRoutes(menu.children, currentPath))
              }
            } else if (menu.menu_type === 2) {
              // 菜单：创建扁平路由直接挂载到 Layout
              routes.push({
                path: currentPath,
                name: `dyn-${currentPath.replace(/\//g, '-')}`,
                component: loadView(menu.component || ''),
                meta: {
                  title: menu.menu_name,
                  icon: menu.icon,
                  requiresAuth: true,
                  order_num: menu.order_num,
                },
              })
            }
          })

          return routes
        }

        const dynamicRoutes = flattenMenuRoutes(menus)

        // 添加扁平路由到 Layout
        dynamicRoutes.forEach(route => {
          if (!router.hasRoute(route.name as string)) {
            router.addRoute('Layout', route);
          }
        });
        
        routesAdded = true;
        resolve()
      } else {
        console.error('Failed to get user menus:', res.msg);
        routesAdded = true; // 即使失败也标记为已尝试添加
        resolve(); // 不拒绝Promise，让应用继续运行
      }
    }).catch(err => {
      console.error('Error loading user menus:', err)
      routesAdded = true; // 发生错误也标记为已尝试添加
      resolve(); // 不拒绝Promise，让应用继续运行
    })
  })
}

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 未登录跳转登录页
  if (to.meta.requiresAuth !== false && !auth.token) {
    return '/login'
  }

  // 访问需要权限的页面且路由尚未加载时，尝试加载动态路由
  if (auth.token) {
    if (!routesAdded) {
      try {
        await addDynamicRoutes()
        return to.fullPath
      } catch (error) {
        console.error('Failed to add dynamic routes:', error)
        if (to.path !== '/dashboard') {
          return '/dashboard'
        }
      }
    }
  }

  return true
})

export default router