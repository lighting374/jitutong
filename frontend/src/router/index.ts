import { createRouter, createWebHistory } from 'vue-router'
import auth from '../services/auth'
import adminApi from '../api/admin'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/user/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/user/Register.vue'),
    },
    {
      path: '/map',
      name: 'MapView',
      component: () => import('../views/MapView.vue'),
    },
    {
      path: '/wiki',
      name: 'WikiShowcase',
      component: () => import('../views/location/WikiShowcase.vue'),
    },
    {
      path: '/user',
      name: 'UserProfile',
      component: () => import('../views/user/UserProfile.vue'),
    },
    {
      path: '/my-comments',
      name: 'MyComments',
      component: () => import('../views/user/MyComments.vue'),
    },
    {
      path: '/my-favorites',
      name: 'MyFavorites',
      component: () => import('../views/user/MyFavorites.vue'),
    },
    {
      path: '/my-history',
      name: 'MyHistory',
      component: () => import('../views/user/MyHistory.vue'),
    },
    {
      path: '/my-messages',
      name: 'MyMessages',
      component: () => import('../views/MyMessages.vue'),
    },
    {
      path: '/my-routes',
      name: 'MyRoutes',
      component: () => import('../views/MyRoutes.vue'),
    },

    // Location routes
    {
      path: '/location/create',
      name: 'LocationWikiCreate',
      component: () => import('../views/location/LocationWikiEdit.vue'),
    },
    {
      path: '/location/:id',
      name: 'LocationWiki',
      component: () => import('../views/location/LocationWiki.vue'),
    },
    {
      path: '/locations/:id',
      redirect: to => `/location/${to.params.id}${to.fullPath.includes('?') ? to.fullPath.substring(to.fullPath.indexOf('?')) : ''}`,
    },
    {
      path: '/location/:id/edit',
      name: 'LocationWikiEdit',
      component: () => import('../views/location/LocationWikiEdit.vue'),
    },

    // Admin routes
    {
      path: '/admin',
      component: () => import('../layouts/AdminLayout.vue'),
      children: [
        { path: '', redirect: '/admin/login' },
        {
          path: 'login',
          component: () => import('../views/admin/AdminLogin.vue'),
          meta: { guest: true },
        },
        {
          path: 'dashboard',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: { requiresAuth: true },
        },
        // admin child routes
        {
          path: 'users',
          component: () => import('../views/admin/UsersManagement.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'locations',
          component: () => import('../views/admin/LocationsManagement.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'reviews',
          component: () => import('../views/admin/ContentReview.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'wiki',
          component: () => import('../views/admin/WikiManagement.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'analytics',
          component: () => import('../views/admin/AnalyticsDashboard.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'settings',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'logs',
          component: () => import('../views/admin/UserLogs.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

// Global guard for admin auth
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.meta.requiresAuth as boolean
  const guestOnly = to.meta.guest as boolean
  const wikiAdminOnly = to.meta.wikiAdminOnly as boolean
  const adminOnly = to.meta.adminOnly as boolean

  console.log('[路由守卫]', { to: to.path, requiresAuth, guestOnly, wikiAdminOnly, adminOnly })

  if (requiresAuth) {
    if (!auth.isAuthenticated()) {
      console.log('[路由守卫] 未认证，跳转到登录页')
      return next({ path: '/admin/login' })
    }
    // 尝试向后端验证 token 是否仍然有效
    try {
      const adminInfo = await adminApi.getAdminInfo()
      console.log('[路由守卫] Token 有效，管理员信息:', adminInfo)
    } catch (err) {
      console.log('[路由守卫] Token 无效或过期，清除并跳转登录')
      auth.logout()
      return next({ path: '/admin/login' })
    }
    const user = auth.getUser()
    console.log('[路由守卫] 当前用户:', user)
    
    // 检查角色是否为管理员角色
    if (user && user.role !== 'admin' && user.role !== 'wiki_admin') {
      console.log('[路由守卫] 角色不是管理员，拒绝访问')
      return next({ path: '/admin/login' })
    }

    // Wiki 管理员只能访问 Wiki 管理页面和 Wiki 编辑页面
    if (user && user.role === 'wiki_admin') {
      const allowedPaths = ['/admin/dashboard', '/admin/wiki']
      const locationPaths = ['/location/create', '/location/:id/edit']
      const isLocationPath = to.path.startsWith('/location/')
      if (!allowedPaths.includes(to.path) && !isLocationPath) {
        console.log('[路由守卫] Wiki 管理员无权访问此页面，跳转到 Wiki 管理')
        return next({ path: '/admin/wiki' })
      }
    }

    // 普通管理员不能访问 Wiki 管理页面
    if (user && user.role === 'admin' && to.path === '/admin/wiki') {
      console.log('[路由守卫] 普通管理员无权访问 Wiki 管理，跳转到仪表盘')
      return next({ path: '/admin/dashboard' })
    }

    console.log('[路由守卫] 验证通过，允许访问')
  }

  if (guestOnly) {
    if (auth.isAuthenticated()) {
      // 只有在后端确认 token 有效时才自动跳转到仪表盘
      try {
        await adminApi.getAdminInfo()
        console.log('[路由守卫] 已登录用户访问登录页，跳转到 dashboard')
        return next({ path: '/admin/dashboard' })
      } catch (err) {
        auth.logout()
        return next()
      }
    }
  }

  return next()
})

export default router
