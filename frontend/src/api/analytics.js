import request from './index'

/**
 * 获取仪表盘数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {Array} params.repository_ids - 仓库ID列表
 * @returns {Promise} 仪表盘数据响应
 */
export function getDashboardData(params) {
  return request({
    url: '/analytics/dashboard',
    method: 'get',
    params
  })
}

/**
 * 获取提交分析数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {string} params.group_by - 分组方式 (author|day|week|month)
 * @param {Array} params.repository_ids - 仓库ID列表
 * @returns {Promise} 提交分析数据响应
 */
export function getCommitsAnalytics(params) {
  return request({
    url: '/analytics/commits',
    method: 'get',
    params
  })
}

/**
 * 获取合并请求分析数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {string} params.group_by - 分组方式 (author|state|day|week|month)
 * @param {Array} params.repository_ids - 仓库ID列表
 * @returns {Promise} 合并请求分析数据响应
 */
export function getMergeRequestsAnalytics(params) {
  return request({
    url: '/analytics/merge-requests',
    method: 'get',
    params
  })
}

/**
 * 获取效率评分数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {Array} params.repository_ids - 仓库ID列表
 * @param {string} params.group_by - 分组方式 (author|repository)
 * @returns {Promise} 效率评分数据响应
 */
export function getEfficiencyScore(params) {
  return request({
    url: '/analytics/efficiency-score',
    method: 'get',
    params
  })
}

/**
 * 获取时间分布数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {string} params.dimension - 时间维度 (hour|weekday|month)
 * @param {string} params.type - 数据类型 (commits|merge_requests)
 * @param {Array} params.repository_ids - 仓库ID列表
 * @returns {Promise} 时间分布数据响应
 */
export function getTimeDistribution(params) {
  return request({
    url: '/analytics/time-distribution',
    method: 'get',
    params
  })
}

/**
 * 获取仓库分析数据
 * @param {number} repositoryId - 仓库ID
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise} 仓库分析数据响应
 */
export function getRepositoryAnalytics(repositoryId, params) {
  return request({
    url: `/analytics/repository/${repositoryId}`,
    method: 'get',
    params
  })
}

/**
 * 获取用户分析数据
 * @param {number} userId - 用户ID
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise} 用户分析数据响应
 */
export function getUserAnalytics(userId, params) {
  return request({
    url: `/analytics/user/${userId}`,
    method: 'get',
    params
  })
}

/**
 * 获取团队生产力数据
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {Array} params.repository_ids - 仓库ID列表
 * @returns {Promise} 团队生产力数据响应
 */
export function getTeamProductivity(params) {
  return request({
    url: '/analytics/team/productivity',
    method: 'get',
    params
  })
}