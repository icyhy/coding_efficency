/**
 * 设置认证Token的JavaScript脚本
 * 在浏览器控制台中运行此脚本来修复认证问题
 */

// 管理员登录凭据
const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'admin123'
};

// API基础URL
const API_BASE_URL = '/api';

/**
 * 登录并设置认证token
 */
async function loginAndSetToken() {
    try {
        console.log('🔐 正在登录...');
        
        // 发送登录请求
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ADMIN_CREDENTIALS)
        });
        
        if (!response.ok) {
            throw new Error(`登录失败: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.success || !data.data) {
            throw new Error(`登录失败: ${data.message || '未知错误'}`);
        }
        
        const { access_token, refresh_token, username, email } = data.data;
        
        // 设置Cookie
        document.cookie = `coding_efficiency_token=${access_token}; path=/; max-age=86400; SameSite=Strict`;
        if (refresh_token) {
            document.cookie = `coding_efficiency_refresh_token=${refresh_token}; path=/; max-age=604800; SameSite=Strict`;
        }
        
        // 设置LocalStorage（模拟前端应用的行为）
        const userInfo = {
            id: data.data.id,
            username: username,
            email: email,
            is_active: data.data.is_active
        };
        localStorage.setItem('user_info', JSON.stringify(userInfo));
        
        console.log('✅ 登录成功！');
        console.log('👤 用户信息:', userInfo);
        console.log('🍪 Token已设置到Cookie中');
        
        return { access_token, refresh_token, userInfo };
        
    } catch (error) {
        console.error('❌ 登录失败:', error.message);
        throw error;
    }
}

/**
 * 测试API调用
 */
async function testAPIs(token) {
    console.log('🧪 开始测试API调用...');
    
    const tests = [
        {
            name: '用户信息API',
            url: `${API_BASE_URL}/auth/profile`,
            method: 'GET'
        },
        {
            name: '仓库列表API',
            url: `${API_BASE_URL}/repositories/`,
            method: 'GET'
        },
        {
            name: '云效搜索API',
            url: `${API_BASE_URL}/repositories/yunxiao/search?keyword=test`,
            method: 'GET'
        }
    ];
    
    for (const test of tests) {
        try {
            const response = await fetch(test.url, {
                method: test.method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log(`✅ ${test.name} - 成功`);
            } else {
                console.log(`❌ ${test.name} - 失败 (${response.status})`);
            }
        } catch (error) {
            console.log(`❌ ${test.name} - 错误: ${error.message}`);
        }
    }
}

/**
 * 检查当前认证状态
 */
function checkAuthStatus() {
    console.log('🔍 检查当前认证状态...');
    
    // 检查Cookie
    const cookies = document.cookie;
    const cookieObj = {};
    if (cookies) {
        cookies.split(';').forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            cookieObj[name] = value;
        });
    }
    
    const hasToken = !!cookieObj['coding_efficiency_token'];
    const hasRefreshToken = !!cookieObj['coding_efficiency_refresh_token'];
    
    console.log('🍪 Cookie状态:');
    console.log(`  - 认证Token: ${hasToken ? '✅ 存在' : '❌ 缺失'}`);
    console.log(`  - 刷新Token: ${hasRefreshToken ? '✅ 存在' : '❌ 缺失'}`);
    
    // 检查LocalStorage
    const userInfo = localStorage.getItem('user_info');
    console.log(`💾 用户信息: ${userInfo ? '✅ 存在' : '❌ 缺失'}`);
    
    if (userInfo) {
        try {
            const parsed = JSON.parse(userInfo);
            console.log('👤 当前用户:', parsed.username);
        } catch (e) {
            console.log('⚠️ 用户信息格式错误');
        }
    }
    
    return { hasToken, hasRefreshToken, userInfo };
}

/**
 * 主修复函数
 */
async function fixAuth() {
    console.log('🔧 开始修复认证问题...');
    console.log('=' .repeat(50));
    
    // 1. 检查当前状态
    const currentStatus = checkAuthStatus();
    
    // 2. 如果没有token，则登录获取
    if (!currentStatus.hasToken) {
        console.log('\n🔑 需要重新登录获取Token...');
        const { access_token } = await loginAndSetToken();
        
        // 3. 测试API调用
        console.log('\n🧪 测试API调用...');
        await testAPIs(access_token);
    } else {
        console.log('\n✅ Token已存在，直接测试API...');
        const cookies = document.cookie;
        const token = cookies.split(';').find(c => c.trim().startsWith('coding_efficiency_token='))?.split('=')[1];
        if (token) {
            await testAPIs(token);
        }
    }
    
    console.log('\n🎉 认证修复完成！');
    console.log('💡 现在可以刷新页面并重试"加入统计"功能');
    console.log('=' .repeat(50));
}

// 导出函数供控制台使用
window.fixAuth = fixAuth;
window.checkAuthStatus = checkAuthStatus;
window.loginAndSetToken = loginAndSetToken;

// 自动执行修复
if (typeof window !== 'undefined') {
    console.log('🚀 认证修复脚本已加载');
    console.log('💡 运行 fixAuth() 来修复认证问题');
    console.log('💡 运行 checkAuthStatus() 来检查当前状态');
}

// 如果在Node.js环境中，导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fixAuth,
        checkAuthStatus,
        loginAndSetToken,
        testAPIs
    };
}