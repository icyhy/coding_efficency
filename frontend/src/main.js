import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import './styles/index.scss'
import { getToken, getRefreshToken } from '@/utils/auth'

// 创建Vue应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(store)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})

// 初始化认证状态 - 从Cookie中恢复token
const token = getToken()
const refreshToken = getRefreshToken()
if (token) {
  store.commit('auth/SET_TOKEN', token)
}
if (refreshToken) {
  store.commit('auth/SET_REFRESH_TOKEN', refreshToken)
}

// 如果存在token但没有用户信息，则获取用户信息
if (token && !store.getters['auth/user']) {
  store.dispatch('auth/getUserInfo').catch(error => {
    console.error('获取用户信息失败:', error)
    // 如果获取用户信息失败，清除token
    store.dispatch('auth/resetToken')
  })
}

// 挂载应用
app.mount('#app')