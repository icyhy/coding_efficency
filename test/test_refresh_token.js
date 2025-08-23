// 测试refresh token的存在性和有效性
const fs = require('fs');
const path = require('path');

// 读取前端auth.js文件
const authPath = path.join(__dirname, 'frontend/src/utils/auth.js');
const authContent = fs.readFileSync(authPath, 'utf8');

console.log('=== Auth.js 文件内容检查 ===');
console.log('RefreshTokenKey定义:');
const refreshTokenKeyMatch = authContent.match(/const RefreshTokenKey = ['"]([^'"]+)['"]/); 
if (refreshTokenKeyMatch) {
    console.log('RefreshTokenKey:', refreshTokenKeyMatch[1]);
} else {
    console.log('未找到RefreshTokenKey定义');
}

console.log('\ngetRefreshToken函数:');
const getRefreshTokenMatch = authContent.match(/export function getRefreshToken\(\)[\s\S]*?}/); 
if (getRefreshTokenMatch) {
    console.log(getRefreshTokenMatch[0]);
} else {
    console.log('未找到getRefreshToken函数');
}

console.log('\nsetRefreshToken函数:');
const setRefreshTokenMatch = authContent.match(/export function setRefreshToken\([\s\S]*?\n}/); 
if (setRefreshTokenMatch) {
    console.log(setRefreshTokenMatch[0]);
} else {
    console.log('未找到setRefreshToken函数');
}

// 检查登录API调用
const authApiPath = path.join(__dirname, 'frontend/src/store/modules/auth.js');
const authApiContent = fs.readFileSync(authApiPath, 'utf8');

console.log('\n=== Vuex Auth模块检查 ===');
console.log('登录action中的refresh token处理:');
const loginActionMatch = authApiContent.match(/async login\([\s\S]*?},/); 
if (loginActionMatch) {
    console.log(loginActionMatch[0]);
} else {
    console.log('未找到login action');
}