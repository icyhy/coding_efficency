import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false })

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    redirect: '/dashboard',
    component: () => import('@/components/Layout/index.vue'),
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          icon: 'DataBoard'
        }
      },
      {
        path: '/analytics',
        name: 'Analytics',
        redirect: '/analytics/commits',
        meta: {
          title: '数据分析',
          icon: 'DataAnalysis'
        },
        children: [
          {
            path: '/analytics/commits',
            name: 'CommitAnalytics',
            component: () => import('@/views/analytics/Commits.vue'),
            meta: {
              title: '提交分析',
              icon: 'Document'
            }
          },
          {
            path: '/analytics/merge-requests',
            name: 'MergeRequestAnalytics',
            component: () => import('@/views/analytics/MergeRequests.vue'),
            meta: {
              title: '合并请求分析',
              icon: 'Connection'
            }
          },
          {
            path: '/analytics/efficiency',
            name: 'EfficiencyAnalytics',
            component: () => import('@/views/analytics/Efficiency.vue'),
            meta: {
              title: '效率分析',
              icon: 'TrendCharts'
            }
          },
          {
            path: '/analytics/time-distribution',
            name: 'TimeDistribution',
            component: () => import('@/views/analytics/TimeDistribution.vue'),
            meta: {
              title: '时间分布',
              icon: 'Timer'
            }
          }
        ]
      },
      {
        path: '/repositories',
        name: 'Repositories',
        component: () => import('@/views/Repositories.vue'),
        meta: {
          title: '仓库管理',
          icon: 'FolderOpened'
        }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: {
          title: '系统设置',
          icon: 'Setting'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 编程效率分析系统` : '编程效率分析系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    const token = store.getters['auth/token']
    if (!token) {
      next('/login')
      return
    }
    
    // 检查用户信息
    if (!store.getters['auth/user']) {
      try {
        await store.dispatch('auth/getUserInfo')
      } catch (error) {
        console.error('获取用户信息失败:', error)
        store.dispatch('auth/logout')
        next('/login')
        return
      }
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && store.getters['auth/token']) {
    next('/')
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router