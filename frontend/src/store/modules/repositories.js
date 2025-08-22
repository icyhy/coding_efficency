import {
  getRepositories,
  addRepository,
  updateRepository,
  deleteRepository,
  syncRepository
} from '@/api/repositories'

const state = {
  repositories: [],
  currentRepository: null,
  loading: false,
  syncing: {}
}

const mutations = {
  SET_REPOSITORIES(state, repositories) {
    state.repositories = repositories
  },
  SET_CURRENT_REPOSITORY(state, repository) {
    state.currentRepository = repository
  },
  ADD_REPOSITORY(state, repository) {
    state.repositories.push(repository)
  },
  UPDATE_REPOSITORY(state, repository) {
    const index = state.repositories.findIndex(repo => repo.id === repository.id)
    if (index !== -1) {
      state.repositories.splice(index, 1, repository)
    }
  },
  REMOVE_REPOSITORY(state, repositoryId) {
    const index = state.repositories.findIndex(repo => repo.id === repositoryId)
    if (index !== -1) {
      state.repositories.splice(index, 1)
    }
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_SYNCING(state, { repositoryId, syncing }) {
    state.syncing = {
      ...state.syncing,
      [repositoryId]: syncing
    }
  }
}

const actions = {
  /**
   * 获取仓库列表
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchRepositories({ commit }, params = {}) {
    commit('SET_LOADING', true)
    try {
      const response = await getRepositories(params)
      commit('SET_REPOSITORIES', response.data.items || [])
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * 添加仓库
   * @param {Object} context - Vuex上下文
   * @param {Object} repositoryData - 仓库数据
   */
  async addRepository({ commit }, repositoryData) {
    try {
      const response = await addRepository(repositoryData)
      commit('ADD_REPOSITORY', response.data)
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * 更新仓库
   * @param {Object} context - Vuex上下文
   * @param {Object} payload - 包含仓库ID和更新数据
   */
  async updateRepository({ commit }, { id, data }) {
    try {
      const response = await updateRepository(id, data)
      commit('UPDATE_REPOSITORY', response.data)
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * 删除仓库
   * @param {Object} context - Vuex上下文
   * @param {number} repositoryId - 仓库ID
   */
  async deleteRepository({ commit }, repositoryId) {
    try {
      const response = await deleteRepository(repositoryId)
      commit('REMOVE_REPOSITORY', repositoryId)
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * 同步仓库数据
   * @param {Object} context - Vuex上下文
   * @param {number} repositoryId - 仓库ID
   */
  async syncRepository({ commit }, repositoryId) {
    commit('SET_SYNCING', { repositoryId, syncing: true })
    try {
      const response = await syncRepository(repositoryId)
      // 同步完成后更新仓库信息
      if (response.data) {
        commit('UPDATE_REPOSITORY', response.data)
      }
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_SYNCING', { repositoryId, syncing: false })
    }
  },

  /**
   * 设置当前仓库
   * @param {Object} context - Vuex上下文
   * @param {Object} repository - 仓库对象
   */
  setCurrentRepository({ commit }, repository) {
    commit('SET_CURRENT_REPOSITORY', repository)
  },

  /**
   * 清空仓库数据
   * @param {Object} context - Vuex上下文
   */
  clearRepositories({ commit }) {
    commit('SET_REPOSITORIES', [])
    commit('SET_CURRENT_REPOSITORY', null)
  }
}

const getters = {
  repositories: state => state.repositories,
  currentRepository: state => state.currentRepository,
  loading: state => state.loading,
  syncing: state => state.syncing,
  repositoryCount: state => state.repositories.length,
  activeRepositories: state => state.repositories.filter(repo => repo.is_active),
  getRepositoryById: state => id => state.repositories.find(repo => repo.id === id),
  isSyncing: state => repositoryId => state.syncing[repositoryId] || false
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}