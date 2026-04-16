from fastapi import APIRouter

from app.api.v1 import auth, dept, menu, permission, post, role, tenant, user, test_query_data, sys_config, test_trial

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(tenant.router, prefix="/tenants", tags=["租户管理"])
api_router.include_router(user.router, prefix="/users", tags=["用户管理"])
api_router.include_router(dept.router, prefix="/depts", tags=["部门管理"])
api_router.include_router(post.router, prefix="/posts", tags=["岗位管理"])
api_router.include_router(role.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(menu.router, prefix="/menus", tags=["菜单管理"])
api_router.include_router(permission.router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(test_query_data.router, prefix="/test-query-data", tags=["测试查询数据"])
api_router.include_router(sys_config.router, prefix="/sys-config", tags=["系统配置"])
api_router.include_router(test_trial.router, prefix="/test-trial", tags=["试算测试"])