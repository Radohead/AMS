import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'Odometer' }
      },
      {
        path: 'assets',
        name: 'AssetList',
        component: () => import('@/views/assets/AssetList.vue'),
        meta: { title: '资产管理', icon: 'Box' }
      },
      {
        path: 'assets/create',
        name: 'AssetCreate',
        component: () => import('@/views/assets/AssetForm.vue'),
        meta: { title: '新建资产', icon: 'Plus' }
      },
      {
        path: 'assets/:id',
        name: 'AssetDetail',
        component: () => import('@/views/assets/AssetDetail.vue'),
        meta: { title: '资产详情' }
      },
      {
        path: 'categories',
        name: 'CategoryList',
        component: () => import('@/views/category/CategoryList.vue'),
        meta: { title: '资产分类', icon: 'Folder' }
      },
      {
        path: 'employees',
        name: 'EmployeeList',
        component: () => import('@/views/employee/EmployeeList.vue'),
        meta: { title: '员工管理', icon: 'User' }
      },
      {
        path: 'departments',
        name: 'DepartmentList',
        component: () => import('@/views/department/DepartmentList.vue'),
        meta: { title: '部门管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'consumables',
        name: 'ConsumableList',
        component: () => import('@/views/inventory/ConsumableList.vue'),
        meta: { title: '易耗品管理', icon: 'Shop' }
      },
      {
        path: 'repair',
        name: 'RepairList',
        component: () => import('@/views/repair/RepairList.vue'),
        meta: { title: '报修管理', icon: 'Tools' }
      },
      {
        path: 'scrap',
        name: 'ScrapList',
        component: () => import('@/views/scrap/ScrapList.vue'),
        meta: { title: '报废管理', icon: 'Delete' }
      },
      {
        path: 'inventory-check',
        name: 'InventoryCheckList',
        component: () => import('@/views/inventory/InventoryCheckList.vue'),
        meta: { title: '盘点管理', icon: 'Search' }
      },
      {
        path: 'inventory-check/:id/scan',
        name: 'InventoryCheckScan',
        component: () => import('@/views/inventory/InventoryCheckScan.vue'),
        meta: { title: '扫码盘点' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/system/UserList.vue'),
        meta: { title: '用户管理', icon: 'UserFilled' }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: () => import('@/views/system/RoleList.vue'),
        meta: { title: '角色管理', icon: 'Key' }
      },
      {
        path: 'logs',
        name: 'LogList',
        component: () => import('@/views/system/LogList.vue'),
        meta: { title: '操作日志', icon: 'Document' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.path !== '/login' && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
