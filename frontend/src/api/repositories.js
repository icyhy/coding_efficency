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
 * 搜索云效仓库候选列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @returns {Promise} 云效仓库候选列表响应
 */
export function searchYunxiaoRepositories(params) {
  return request({
    url: '/repositories/yunxiao/search',
    method: 'get',
    params
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

/**
 * 获取云效仓库列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.search - 搜索关键词
 * @returns {Promise} 云效仓库列表响应
 */
/**
 * 按仓库名称搜索云效仓库
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索关键词（必填）
 * @param {number} params.page - 页码，默认1
 * @param {number} params.per_page - 每页数量，默认50
 * @returns {Promise} 云效仓库搜索响应
 */
export function getYunxiaoRepositoriesAPI(params = {}) {
  return request({
    url: '/repositories/yunxiao/search',
    method: 'get',
    params
  })
}

/**
 * 从云效列表添加仓库到当前用户的仓库管理
 * 注意：该接口仅创建仓库记录，默认不纳入统计。如需纳入统计，请在成功后调用 addToTrackingAPI。
 * @param {Object} data - 云效仓库数据
 * @param {number|string} data.repository_id - 云效仓库ID（必填）
 * @param {string} data.name - 仓库名称（必填）
 * @param {string} data.clone_url - 仓库克隆地址（必填）
 * @param {string} [data.web_url] - 仓库网页地址
 * @param {string} [data.description] - 仓库描述
 * @returns {Promise} 创建仓库响应
 */
export function addYunxiaoRepository(data) {
  return request({
    url: '/repositories/yunxiao/add',
    method: 'post',
    data
  })
}

/**
 * 将仓库加入统计
 * @param {number} id - 仓库ID
 * @returns {Promise} 加入统计响应
 */
export function addToTrackingAPI(id) {
  return request({
    url: `/repositories/${id}/track`,
    method: 'post'
  })
}

/**
 * 将仓库移出统计
 * @param {number} id - 仓库ID
 * @returns {Promise} 移出统计响应
 */
export function removeFromTrackingAPI(id) {
  return request({
    url: `/repositories/${id}/untrack`,
    method: 'post'
  })
}

/**
 * 同步所有仓库（已废弃，保留兼容性）
 * @param {Object} params - 同步参数
 * @returns {Promise} 同步响应
 */
export function syncAllRepositories(params = {}) {
  return getYunxiaoRepositoriesAPI(params)
}