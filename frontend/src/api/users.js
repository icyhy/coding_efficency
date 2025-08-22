import request from './index'

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.role - 用户角色
 * @param {string} params.status - 用户状态
 * @returns {Promise} 用户列表响应
 */
export function getUsers(params) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

/**
 * 获取用户详情
 * @param {string} id - 用户ID
 * @returns {Promise} 用户详情响应
 */
export function getUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

/**
 * 创建用户
 * @param {Object} data - 用户数据
 * @param {string} data.username - 用户名
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @param {string} data.role - 角色
 * @returns {Promise} 创建结果响应
 */
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

/**
 * 更新用户
 * @param {string} id - 用户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果响应
 */
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 * @param {string} id - 用户ID
 * @returns {Promise} 删除结果响应
 */
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

/**
 * 启用/禁用用户
 * @param {string} id - 用户ID
 * @param {boolean} status - 状态
 * @returns {Promise} 操作结果响应
 */
export function toggleUserStatus(id, status) {
  return request({
    url: `/users/${id}/status`,
    method: 'put',
    data: { status }
  })
}

/**
 * 重置用户密码
 * @param {string} id - 用户ID
 * @param {string} password - 新密码
 * @returns {Promise} 重置结果响应
 */
export function resetUserPassword(id, password) {
  return request({
    url: `/users/${id}/reset-password`,
    method: 'post',
    data: { password }
  })
}

/**
 * 获取用户权限
 * @param {string} id - 用户ID
 * @returns {Promise} 权限列表响应
 */
export function getUserPermissions(id) {
  return request({
    url: `/users/${id}/permissions`,
    method: 'get'
  })
}

/**
 * 更新用户权限
 * @param {string} id - 用户ID
 * @param {Array} permissions - 权限列表
 * @returns {Promise} 更新结果响应
 */
export function updateUserPermissions(id, permissions) {
  return request({
    url: `/users/${id}/permissions`,
    method: 'put',
    data: { permissions }
  })
}

/**
 * 获取用户活动日志
 * @param {string} id - 用户ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 活动日志响应
 */
export function getUserActivityLog(id, params) {
  return request({
    url: `/users/${id}/activity`,
    method: 'get',
    params
  })
}

/**
 * 批量导入用户
 * @param {FormData} formData - 包含用户数据的表单
 * @returns {Promise} 导入结果响应
 */
export function importUsers(formData) {
  return request({
    url: '/users/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出用户数据
 * @param {Object} params - 导出参数
 * @returns {Promise} 导出文件响应
 */
export function exportUsers(params) {
  return request({
    url: '/users/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}