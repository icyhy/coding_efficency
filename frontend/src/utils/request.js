import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import store from '@/store'
import router from '@/router'
import { getToken } from '@/utils/auth'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000',
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    const token = getToken()
    if (token) {
      // 让每个请求携带token
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 设置请求头
    config.headers['Content-Type'] = 'application/json'
    
    return config
  },
  error => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 是否正在刷新token
let isRefreshing = false
// 重试队列
let requests = []

// 响应拦截器
service.interceptors.response.use(
  /**
   * 如果你想获得http信息，如headers或status
   * 请返回 response => response
   */
  response => {
    const res = response.data
    
    // 如果自定义代码不是200，则判断为错误
    if (res.code !== undefined && res.code !== 200) {
      ElMessage({
        message: res.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
      
      // 401: 未授权，token过期等
      if (res.code === 401) {
        // 弹出确认对话框，重新登录
        ElMessageBox.confirm(
          '登录状态已过期，您可以继续留在该页面，或者重新登录',
          '系统提示',
          {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          store.dispatch('auth/resetToken').then(() => {
            location.reload()
          })
        })
      }
      
      // 403: 权限不足
      if (res.code === 403) {
        router.push('/403')
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res
    }
  },
  error => {
    console.error('响应错误:', error)
    
    let message = '网络错误'
    
    if (error.response) {
      const { status, data, config } = error.response
      
      // 401错误且不是刷新token接口，尝试刷新token
      if (status === 401 && !config.url.includes('/auth/refresh')) {
        if (!isRefreshing) {
          isRefreshing = true
          
          return store.dispatch('auth/refreshToken').then((newToken) => {
            isRefreshing = false
            // 重新发送所有等待的请求
            requests.forEach(cb => cb(newToken))
            requests = []
            
            // 重新发送当前请求
            config.headers['Authorization'] = `Bearer ${newToken}`
            return service(config)
          }).catch(() => {
            isRefreshing = false
            requests = []
            // 刷新失败，跳转到登录页
            store.dispatch('auth/resetToken')
            router.push('/login')
            return Promise.reject(error)
          })
        } else {
          // 正在刷新token，将请求加入队列
          return new Promise((resolve) => {
            requests.push((token) => {
              config.headers['Authorization'] = `Bearer ${token}`
              resolve(service(config))
            })
          })
        }
      }
      
      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 如果是刷新token接口返回401，直接跳转登录页
          if (config.url.includes('/auth/refresh')) {
            store.dispatch('auth/resetToken')
            router.push('/login')
          }
          break
        case 403:
          message = '权限不足，拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        default:
          message = data.message || `连接错误${status}`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时'
    } else if (error.message) {
      message = error.message
    }
    
    ElMessage({
      message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service