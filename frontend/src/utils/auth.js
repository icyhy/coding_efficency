import Cookies from 'js-cookie'

const TokenKey = 'coding_efficiency_token'
const RefreshTokenKey = 'coding_efficiency_refresh_token'

/**
 * 获取Token
 * @returns {string|null} Token值
 */
export function getToken() {
  return Cookies.get(TokenKey)
}

/**
 * 设置Token
 * @param {string} token - Token值
 * @param {Object} options - Cookie选项
 */
export function setToken(token, options = {}) {
  const defaultOptions = {
    expires: 1/48, // 30分钟过期 (1/48 天)
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  }
  return Cookies.set(TokenKey, token, { ...defaultOptions, ...options })
}

/**
 * 移除Token
 */
export function removeToken() {
  Cookies.remove(TokenKey)
  Cookies.remove(RefreshTokenKey)
}

/**
 * 获取刷新Token
 * @returns {string|null} 刷新Token值
 */
export function getRefreshToken() {
  return Cookies.get(RefreshTokenKey)
}

/**
 * 设置刷新Token
 * @param {string} refreshToken - 刷新Token值
 * @param {Object} options - Cookie选项
 */
export function setRefreshToken(refreshToken, options = {}) {
  const defaultOptions = {
    expires: 7, // 7天过期
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  }
  return Cookies.set(RefreshTokenKey, refreshToken, { ...defaultOptions, ...options })
}

/**
 * 检查是否已登录
 * @returns {boolean} 是否已登录
 */
export function isLoggedIn() {
  return !!getToken()
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  removeToken()
  // 清除其他可能的用户数据
  localStorage.removeItem('user_info')
  sessionStorage.clear()
}

/**
 * 获取用户信息（从localStorage）
 * @returns {Object|null} 用户信息
 */
export function getUserInfo() {
  try {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo) : null
  } catch (error) {
    console.error('获取用户信息失败:', error)
    return null
  }
}

/**
 * 设置用户信息（到localStorage）
 * @param {Object} userInfo - 用户信息
 */
export function setUserInfo(userInfo) {
  try {
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  } catch (error) {
    console.error('设置用户信息失败:', error)
  }
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
  localStorage.removeItem('user_info')
}