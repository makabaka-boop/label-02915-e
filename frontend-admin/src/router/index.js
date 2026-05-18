import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/products',
    children: [
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue'),
        meta: { title: '商品管理' },
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/Categories.vue'),
        meta: { title: '分类管理' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('../views/Logs.vue'),
        meta: { title: '操作日志' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || ''} - 商品管理系统`
  const token = localStorage.getItem('token')
  if (to.path === '/login' && token) {
    next('/')
  } else if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
