// 检查认证状态的Node.js脚本
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 模拟浏览器Cookie解析
function parseCookies(cookieString) {
  const cookies = {};
  if (cookieString) {
    cookieString.split(';').forEach(cookie => {
      const [name, value] = cookie.trim().split('=');
      if (name && value) {
        cookies[name] = decodeURIComponent(value);
      }
    });
  }
  return cookies;
}

async function checkAuthStatus() {
  try {
    console.log('=== 认证状态检查 ===');
    
    // 1. 检查后端健康状态
    console.log('\n1. 检查后端服务状态...');
    try {
      const healthResponse = await axios.get('http://localhost:5001/health', {
        timeout: 5000
      });
      console.log('✅ 后端服务正常:', healthResponse.data);
    } catch (error) {
      console.log('❌ 后端服务异常:', error.message);
      return;
    }
    
    // 2. 尝试无认证访问仓库列表
    console.log('\n2. 测试无认证访问...');
    try {
      const noAuthResponse = await axios.get('http://localhost:5001/api/repositories', {
        timeout: 5000
      });
      console.log('⚠️  无认证访问成功（这可能是问题）:', noAuthResponse.data);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ 无认证访问被正确拒绝 (401)');
      } else {
        console.log('❌ 无认证访问异常:', error.message);
      }
    }
    
    // 3. 尝试登录获取token
    console.log('\n3. 尝试登录获取token...');
    try {
      const loginResponse = await axios.post('http://localhost:5001/api/auth/login', {
        username: 'admin',
        password: 'admin123'
      }, {
        timeout: 5000
      });
      
      if (loginResponse.data && loginResponse.data.success) {
        const token = loginResponse.data.data.access_token;
        console.log('✅ 登录成功，获得token:', token.substring(0, 20) + '...');
        
        // 4. 使用token访问仓库列表
        console.log('\n4. 使用token访问仓库列表...');
        try {
          const authResponse = await axios.get('http://localhost:5001/api/repositories', {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            timeout: 5000
          });
          console.log('✅ 认证访问成功:', authResponse.data);
        } catch (error) {
          console.log('❌ 认证访问失败:', error.response?.data || error.message);
        }
      } else {
        console.log('❌ 登录失败:', loginResponse.data);
      }
    } catch (error) {
      console.log('❌ 登录请求失败:', error.response?.data || error.message);
    }
    
    console.log('\n=== 检查完成 ===');
    
  } catch (error) {
    console.error('检查过程中发生错误:', error.message);
  }
}

checkAuthStatus();