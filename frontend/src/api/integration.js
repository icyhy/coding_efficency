import request from './index'

/**
 * 获取所有集成配置
 * @returns {Promise} 集成配置列表响应
 */
export function getIntegrations() {
  return request({
    url: '/auth/integrations',
    method: 'get'
  })
}

/**
 * 创建集成配置
 * @param {Object} data - 集成配置数据
 * @param {string} data.platform - 平台类型
 * @param {string} data.config_name - 配置名称
 * @param {string} data.api_url - API地址
 * @param {string} data.access_token - 访问令牌
 * @param {string} data.organization - 组织名称
 * @returns {Promise} 创建响应
 */
export function createIntegration(data) {
  return request({
    url: '/auth/integrations',
    method: 'post',
    data
  })
}

/**
 * 更新集成配置
 * @param {number} configId - 配置ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新响应
 */
export function updateIntegration(configId, data) {
  return request({
    url: `/auth/integrations/${configId}`,
    method: 'put',
    data
  })
}

/**
 * 删除集成配置
 * @param {number} configId - 配置ID
 * @returns {Promise} 删除响应
 */
export function deleteIntegration(configId) {
  return request({
    url: `/auth/integrations/${configId}`,
    method: 'delete'
  })
}

/**
 * 测试集成配置连接
 * @param {number} configId - 配置ID
 * @returns {Promise} 测试响应
 */
export function testIntegration(configId) {
  return request({
    url: `/auth/integrations/${configId}/test`,
    method: 'post'
  })
}

// 导出为authApi以保持向后兼容
export const authApi = {
  getIntegrations,
  createIntegration,
  updateIntegration,
  deleteIntegration,
  testIntegration
}

export default authApi