import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken, clearAuth } from '@/utils/auth'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: '/api', // 使用代理路径
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 如果是refresh token请求，不要覆盖已设置的Authorization头
    if (config.url.includes('/auth/refresh')) {
      return config
    }
    
    // 添加认证token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 是否正在刷新token
let isRefreshing = false
// 失败队列
let failedQueue = []

// 处理队列
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

// 响应拦截器
service.interceptors.response.use(
  response => {
    const { data } = response
    
    // 将所有2xx状态码视为成功
    if (response.status >= 200 && response.status < 300) {
      return data
    }
    
    // 其他情况均为错误
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  async error => {
    console.error('响应错误:', error)
    
    const originalRequest = error.config
    
    // 处理不同的HTTP状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 如果是刷新token的请求失败，直接登出
          if (originalRequest.url.includes('/auth/refresh')) {
            ElMessage.error('登录已过期，请重新登录')
            clearAuth()
            router.push('/login')
            return Promise.reject(error)
          }
          
          // 如果是云效API相关的请求失败，不清除用户登录状态
          if (originalRequest.url.includes('/repositories') || 
              originalRequest.url.includes('/integrations')) {
            // 这些可能是云效API调用失败，不影响用户登录状态
            const errorMsg = data?.message || '访问云效API失败，请检查集成配置'
            ElMessage.error(errorMsg)
            return Promise.reject(error)
          }
          
          // 如果是分析API相关的请求失败，尝试刷新Token
          if (originalRequest.url.includes('/analytics')) {
            // 这些是分析API调用，可能需要刷新Token
            console.log('分析API请求失败，尝试刷新Token')
            // 继续执行下面的Token刷新逻辑
          }
          
          // 避免重复刷新
          if (originalRequest._retry) {
            ElMessage.error('登录已过期，请重新登录')
            clearAuth()
            router.push('/login')
            return Promise.reject(error)
          }
          
          if (isRefreshing) {
            // 如果正在刷新token，将请求加入队列
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject })
            }).then(token => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return service(originalRequest)
            }).catch(err => {
              return Promise.reject(err)
            })
          }
          
          originalRequest._retry = true
          isRefreshing = true
          
          // 尝试刷新token
          try {
            // 检查是否存在刷新Token
            const store = (await import('@/store')).default
            const refreshTokenValue = store.getters['auth/refreshToken']
            
            if (!refreshTokenValue) {
              throw new Error('Refresh Token不存在')
            }
            
            await store.dispatch('auth/refreshToken')
            const newToken = store.getters['auth/token']
            
            processQueue(null, newToken)
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return service(originalRequest)
          } catch (refreshError) {
            processQueue(refreshError, null)
            ElMessage.error('登录已过期，请重新登录')
            clearAuth()
            router.push('/login')
            return Promise.reject(refreshError)
          } finally {
            isRefreshing = false
          }
          
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请稍后重试')
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default service