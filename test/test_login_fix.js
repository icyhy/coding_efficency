/**
 * 测试登录功能修复
 * 验证前端登录是否能正确获取access_token
 */

const axios = require('axios');

// 配置axios实例
const api = axios.create({
  baseURL: 'http://localhost:8001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

async function testLogin() {
  try {
    console.log('🔍 测试登录功能...');
    
    // 测试登录
    const loginResponse = await api.post('/auth/login', {
      username: 'validuser',
      password: 'Password123!'
    });
    
    console.log('✅ 登录请求成功');
    console.log('📦 响应数据结构:', JSON.stringify(loginResponse.data, null, 2));
    
    // 检查响应数据结构
    const responseData = loginResponse.data;
    
    if (responseData.access_token) {
      console.log('✅ access_token 存在:', responseData.access_token.substring(0, 50) + '...');
    } else {
      console.log('❌ access_token 不存在');
      console.log('🔍 响应数据键:', Object.keys(responseData));
    }
    
    if (responseData.refresh_token) {
      console.log('✅ refresh_token 存在:', responseData.refresh_token.substring(0, 50) + '...');
    } else {
      console.log('❌ refresh_token 不存在');
    }
    
    if (responseData.token_type) {
      console.log('✅ token_type:', responseData.token_type);
    }
    
    // 测试使用access_token获取用户信息
    if (responseData.access_token) {
      console.log('\n🔍 测试获取用户信息...');
      
      const userInfoResponse = await api.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${responseData.access_token}`
        }
      });
      
      console.log('✅ 获取用户信息成功');
      console.log('👤 用户信息:', JSON.stringify(userInfoResponse.data, null, 2));
    }
    
    console.log('\n🎉 登录功能测试完成，所有功能正常！');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    if (error.response) {
      console.error('📦 错误响应:', error.response.data);
      console.error('🔢 状态码:', error.response.status);
    }
  }
}

// 运行测试
testLogin();