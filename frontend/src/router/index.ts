import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
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
      {
        path: 'system',
        name: 'System',
        meta: { title: '系统管理', minUserType: 1 },   // user_type <= 1 才能访问系统管理
        children: [
          { path: 'tenant',     name: 'Tenant',     component: () => import('@/views/system/TenantManage.vue'),     meta: { title: '租户管理',  minUserType: 0 } },
          { path: 'user',       name: 'User',       component: () => import('@/views/system/UserManage.vue'),       meta: { title: '用户管理',  minUserType: 1 } },
          { path: 'dept',       name: 'Dept',       component: () => import('@/views/system/DeptManage.vue'),       meta: { title: '部门管理',  minUserType: 1 } },
          { path: 'post',       name: 'Post',       component: () => import('@/views/system/PostManage.vue'),       meta: { title: '岗位管理',  minUserType: 1 } },
          { path: 'role',       name: 'Role',       component: () => import('@/views/system/RoleManage.vue'),       meta: { title: '角色管理',  minUserType: 1 } },
          { path: 'menu',       name: 'Menu',       component: () => import('@/views/system/MenuManage.vue'),       meta: { title: '菜单管理',  minUserType: 0 } },
          { path: 'permission', name: 'Permission', component: () => import('@/views/system/PermissionManage.vue'), meta: { title: '权限管理',  minUserType: 0 } },
        ],
      },
      {
        path: 'test',
        name: 'Test',
        meta: { title: '测试管理', minUserType: 1 },   // user_type <= 1 才能访问测试管理
        children: [
          { path: 'test-query-data', name: 'TestQueryData', component: () => import('@/views/system/TestQueryDataManage.vue'), meta: { title: '测试查询数据',  minUserType: 1 } },
          { path: 'sys-config', name: 'SysConfig', component: () => import('@/views/system/SysConfigManage.vue'), meta: { title: '系统配置',  minUserType: 1 } },
        ],
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // 未登录跳登录页
  if (to.meta.requiresAuth !== false && !auth.token) {
    return '/login'
  }

  // 已登录时校验路由所需最低权限
  // minUserType: 0 = 超级管理员，1 = 租户管理员，不设 = 所有人
  if (auth.token && to.meta.minUserType !== undefined) {
    const userType = auth.user?.user_type ?? 2
    const required = to.meta.minUserType as number
    // user_type 数值越大权限越低（0最高，2最低），需满足 userType <= required
    if (userType > required) {
      return '/dashboard'
    }
  }
})

export default router