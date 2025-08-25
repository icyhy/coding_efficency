import { login, getUserInfo, logout, refreshToken } from '@/api/auth'
import { getToken, setToken, removeToken, getRefreshToken, setRefreshToken, getUserInfo as getStoredUserInfo, setUserInfo, removeUserInfo } from '@/utils/auth'
import router from '@/router'

const state = {
  token: getToken(),
  refreshToken: getRefreshToken(),
  user: getStoredUserInfo(), // 从localStorage恢复用户信息
  permissions: []
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
  },
  SET_REFRESH_TOKEN(state, refreshToken) {
    state.refreshToken = refreshToken
  },
  SET_USER(state, user) {
    state.user = user
    // 同时保存到localStorage
    if (user) {
      setUserInfo(user)
    }
  },
  SET_PERMISSIONS(state, permissions) {
    state.permissions = permissions
  },
  CLEAR_AUTH(state) {
    state.token = null
    state.refreshToken = null
    state.user = null
    state.permissions = []
    // 清除localStorage中的用户信息
    removeUserInfo()
  }
}

const actions = {
  /**
   * 用户登录
   * @param {Object} context - Vuex上下文
   * @param {Object} loginForm - 登录表单数据
   */
  async login({ commit }, loginForm) {
    try {
      const response = await login(loginForm)
      const userData = response.data
      
      // 后端返回的数据结构中token包含在用户数据中
      const token = userData.access_token
      const refreshTokenValue = userData.refresh_token
      const user = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        is_active: userData.is_active,
        created_at: userData.created_at,
        updated_at: userData.updated_at
      }
      
      // 确保刷新Token存在
      if (!refreshTokenValue) {
        console.error('登录响应中缺少refresh_token')
        throw new Error('登录失败：服务器未返回刷新令牌')
      }
      
      commit('SET_TOKEN', token)
      commit('SET_REFRESH_TOKEN', refreshTokenValue)
      commit('SET_USER', user)
      setToken(token)
      setRefreshToken(refreshTokenValue)
      
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * 获取用户信息
   * @param {Object} context - Vuex上下文
   */
  async getUserInfo({ commit, state }) {
    try {
      if (!state.token) {
        throw new Error('Token不存在')
      }
      
      const response = await getUserInfo()
      const { user, permissions } = response.data
      
      commit('SET_USER', user)
      commit('SET_PERMISSIONS', permissions || [])
      
      return response
    } catch (error) {
      commit('CLEAR_AUTH')
      removeToken()
      throw error
    }
  },

  /**
   * 用户登出
   * @param {Object} context - Vuex上下文
   */
  async logout({ commit }) {
    try {
      await logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      commit('CLEAR_AUTH')
      removeToken()
      router.push('/login')
    }
  },

  /**
   * 刷新Token
   * @param {Object} context - Vuex上下文
   */
  async refreshToken({ commit, state }) {
    try {
      if (!state.refreshToken) {
        console.warn('Refresh Token不存在，无法刷新Token')
        // 清除认证状态
        commit('CLEAR_AUTH')
        removeToken()
        throw new Error('Refresh Token不存在')
      }
      
      const response = await refreshToken()
      const { access_token } = response.data
      
      commit('SET_TOKEN', access_token)
      setToken(access_token)
      
      // 注意：后端只返回新的access_token，refresh_token保持不变
      return access_token
    } catch (error) {
      // 刷新失败，清除所有认证信息
      commit('CLEAR_AUTH')
      removeToken()
      throw error
    }
  },

  /**
   * 重置Token
   * @param {Object} context - Vuex上下文
   */
  resetToken({ commit }) {
    commit('CLEAR_AUTH')
    removeToken()
  }
}

const getters = {
  token: state => state.token,
  refreshToken: state => state.refreshToken,
  user: state => state.user,
  permissions: state => state.permissions,
  isLoggedIn: state => !!state.token,
  userId: state => state.user?.id,
  username: state => state.user?.username,
  email: state => state.user?.email,
  avatar: state => state.user?.avatar
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}