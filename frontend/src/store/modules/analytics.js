import {
  getDashboardData,
  getCommitsAnalytics,
  getMergeRequestsAnalytics,
  getEfficiencyScore,
  getTimeDistribution
} from '@/api/analytics'

const state = {
  dashboardData: null,
  commitsData: null,
  mergeRequestsData: null,
  efficiencyData: null,
  timeDistributionData: null,
  loading: {
    dashboard: false,
    commits: false,
    mergeRequests: false,
    efficiency: false,
    timeDistribution: false
  }
}

const mutations = {
  SET_DASHBOARD_DATA(state, data) {
    state.dashboardData = data
  },
  SET_COMMITS_DATA(state, data) {
    state.commitsData = data
  },
  SET_MERGE_REQUESTS_DATA(state, data) {
    state.mergeRequestsData = data
  },
  SET_EFFICIENCY_DATA(state, data) {
    state.efficiencyData = data
  },
  SET_TIME_DISTRIBUTION_DATA(state, data) {
    state.timeDistributionData = data
  },
  SET_LOADING(state, { type, loading }) {
    state.loading[type] = loading
  }
}

const actions = {
  /**
   * 获取仪表盘数据
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchDashboardData({ commit }, params = {}) {
    commit('SET_LOADING', { type: 'dashboard', loading: true })
    try {
      const response = await getDashboardData(params)
      commit('SET_DASHBOARD_DATA', response.data)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', { type: 'dashboard', loading: false })
    }
  },

  /**
   * 获取提交分析数据
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchCommitsAnalytics({ commit }, params = {}) {
    commit('SET_LOADING', { type: 'commits', loading: true })
    try {
      const response = await getCommitsAnalytics(params)
      commit('SET_COMMITS_DATA', response.data)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', { type: 'commits', loading: false })
    }
  },

  /**
   * 获取合并请求分析数据
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchMergeRequestsAnalytics({ commit }, params = {}) {
    commit('SET_LOADING', { type: 'mergeRequests', loading: true })
    try {
      const response = await getMergeRequestsAnalytics(params)
      commit('SET_MERGE_REQUESTS_DATA', response.data)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', { type: 'mergeRequests', loading: false })
    }
  },

  /**
   * 获取效率评分数据
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchEfficiencyScore({ commit }, params = {}) {
    commit('SET_LOADING', { type: 'efficiency', loading: true })
    try {
      const response = await getEfficiencyScore(params)
      commit('SET_EFFICIENCY_DATA', response.data)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', { type: 'efficiency', loading: false })
    }
  },

  /**
   * 获取时间分布数据
   * @param {Object} context - Vuex上下文
   * @param {Object} params - 查询参数
   */
  async fetchTimeDistribution({ commit }, params = {}) {
    commit('SET_LOADING', { type: 'timeDistribution', loading: true })
    try {
      const response = await getTimeDistribution(params)
      commit('SET_TIME_DISTRIBUTION_DATA', response.data)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', { type: 'timeDistribution', loading: false })
    }
  },

  /**
   * 清空分析数据
   * @param {Object} context - Vuex上下文
   */
  clearAnalyticsData({ commit }) {
    commit('SET_DASHBOARD_DATA', null)
    commit('SET_COMMITS_DATA', null)
    commit('SET_MERGE_REQUESTS_DATA', null)
    commit('SET_EFFICIENCY_DATA', null)
    commit('SET_TIME_DISTRIBUTION_DATA', null)
  }
}

const getters = {
  dashboardData: state => state.dashboardData,
  commitsData: state => state.commitsData,
  mergeRequestsData: state => state.mergeRequestsData,
  efficiencyData: state => state.efficiencyData,
  timeDistributionData: state => state.timeDistributionData,
  loading: state => state.loading,
  isDashboardLoading: state => state.loading.dashboard,
  isCommitsLoading: state => state.loading.commits,
  isMergeRequestsLoading: state => state.loading.mergeRequests,
  isEfficiencyLoading: state => state.loading.efficiency,
  isTimeDistributionLoading: state => state.loading.timeDistribution
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}