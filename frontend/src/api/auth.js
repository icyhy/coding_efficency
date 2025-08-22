import request from './index'

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise} 登录响应
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户名
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @returns {Promise} 注册响应
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 * @returns {Promise} 用户信息响应
 */
export function getUserInfo() {
  return request({
    url: '/auth/user',
    method: 'get'
  })
}

/**
 * 用户登出
 * @returns {Promise} 登出响应
 */
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

/**
 * 刷新Token
 * @returns {Promise} 刷新Token响应
 */
export function refreshToken() {
  return request({
    url: '/auth/refresh',
    method: 'post'
  })
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} 修改密码响应
 */
export function changePassword(data) {
  return request({
    url: '/auth/change-password',
    method: 'post',
    data
  })
}