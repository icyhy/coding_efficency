import { login, getUserInfo, logout } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'
import router from '@/router'

const state = {
  token: getToken(),
  user: null,
  permissions: []
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
  },
  SET_USER(state, user) {
    state.user = user
  },
  SET_PERMISSIONS(state, permissions) {
    state.permissions = permissions
  },
  CLEAR_AUTH(state) {
    state.token = null
    state.user = null
    state.permissions = []
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
      const user = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        is_active: userData.is_active,
        created_at: userData.created_at,
        updated_at: userData.updated_at
      }
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      setToken(token)
      
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