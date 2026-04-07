import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
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
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      {
        path: 'system',
        name: 'System',
        meta: { title: '系统管理', icon: 'Setting' },
        children: [
          { path: 'tenant',     name: 'Tenant',     component: () => import('@/views/system/TenantManage.vue'),     meta: { title: '租户管理' } },
          { path: 'user',       name: 'User',       component: () => import('@/views/system/UserManage.vue'),       meta: { title: '用户管理' } },
          { path: 'dept',       name: 'Dept',       component: () => import('@/views/system/DeptManage.vue'),       meta: { title: '部门管理' } },
          { path: 'post',       name: 'Post',       component: () => import('@/views/system/PostManage.vue'),       meta: { title: '岗位管理' } },
          { path: 'role',       name: 'Role',       component: () => import('@/views/system/RoleManage.vue'),       meta: { title: '角色管理' } },
          { path: 'menu',       name: 'Menu',       component: () => import('@/views/system/MenuManage.vue'),       meta: { title: '菜单管理' } },
          { path: 'permission', name: 'Permission', component: () => import('@/views/system/PermissionManage.vue'), meta: { title: '权限管理' } },
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
  if (to.meta.requiresAuth !== false && !auth.token) {
    return '/login'
  }
})

export default router
