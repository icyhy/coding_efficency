import request from './index'

/**
 * 获取仓库列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {boolean} params.is_active - 是否激活
 * @returns {Promise} 仓库列表响应
 */
export function getRepositories(params) {
  return request({
    url: '/repositories',
    method: 'get',
    params
  })
}

/**
 * 获取仓库详情
 * @param {number} id - 仓库ID
 * @returns {Promise} 仓库详情响应
 */
export function getRepository(id) {
  return request({
    url: `/repositories/${id}`,
    method: 'get'
  })
}

/**
 * 添加仓库
 * @param {Object} data - 仓库数据
 * @param {string} data.name - 仓库名称
 * @param {string} data.url - 仓库URL
 * @param {string} data.description - 仓库描述
 * @param {string} data.access_token - 访问令牌
 * @returns {Promise} 添加仓库响应
 */
export function addRepository(data) {
  return request({
    url: '/repositories',
    method: 'post',
    data
  })
}

/**
 * 更新仓库
 * @param {number} id - 仓库ID
 * @param {Object} data - 更新数据
 * @param {string} data.name - 仓库名称
 * @param {string} data.description - 仓库描述
 * @param {boolean} data.is_active - 是否激活
 * @param {string} data.access_token - 访问令牌
 * @returns {Promise} 更新仓库响应
 */
export function updateRepository(id, data) {
  return request({
    url: `/repositories/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除仓库
 * @param {number} id - 仓库ID
 * @returns {Promise} 删除仓库响应
 */
export function deleteRepository(id) {
  return request({
    url: `/repositories/${id}`,
    method: 'delete'
  })
}

/**
 * 同步仓库数据
 * @param {number} id - 仓库ID
 * @param {Object} params - 同步参数
 * @param {boolean} params.force - 是否强制同步
 * @param {string} params.sync_type - 同步类型 (commits|merge_requests|all)
 * @returns {Promise} 同步仓库响应
 */
export function syncRepository(id, params = {}) {
  return request({
    url: `/repositories/${id}/sync`,
    method: 'post',
    params
  })
}

/**
 * 获取仓库同步状态
 * @param {number} id - 仓库ID
 * @returns {Promise} 同步状态响应
 */
export function getRepositorySyncStatus(id) {
  return request({
    url: `/repositories/${id}/sync-status`,
    method: 'get'
  })
}

/**
 * 测试仓库连接
 * @param {Object} data - 连接测试数据
 * @param {string} data.url - 仓库URL
 * @param {string} data.access_token - 访问令牌
 * @returns {Promise} 连接测试响应
 */
export function testRepositoryConnection(data) {
  return request({
    url: '/repositories/test-connection',
    method: 'post',
    data
  })
}

/**
 * 获取仓库统计信息
 * @param {number} id - 仓库ID
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise} 仓库统计信息响应
 */
export function getRepositoryStats(id, params) {
  return request({
    url: `/repositories/${id}/stats`,
    method: 'get',
    params
  })
}