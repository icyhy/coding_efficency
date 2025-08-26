const { chromium } = require('playwright');

async function testRepositoriesAPI() {
  let browser;
  let context;
  let page;
  
  try {
    console.log('🚀 启动浏览器...');
    browser = await chromium.launch({ headless: false });
    context = await browser.newContext();
    page = await context.newPage();
    
    // 监听网络请求
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`📤 请求: ${request.method()} ${request.url()}`);
        const headers = request.headers();
        if (headers.authorization) {
          console.log(`🔑 认证头: ${headers.authorization.substring(0, 20)}...`);
        } else {
          console.log('⚠️ 没有认证头');
        }
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        console.log(`📥 响应: ${response.status()} ${response.url()}`);
      }
    });
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`❌ 控制台错误: ${msg.text()}`);
      }
    });
    
    // 监听页面错误
    page.on('pageerror', error => {
      console.log(`💥 页面错误: ${error.message}`);
    });
    
    console.log('🔐 直接导航到登录页面...');
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
    
    console.log('📝 填写登录信息...');
    await page.fill('input[placeholder="请输入用户名"]', 'validuser');
    await page.fill('input[placeholder="请输入密码"]', 'Password123!');
    
    console.log('🔑 点击登录按钮...');
    await page.click('.login-btn');
    
    // 等待登录完成
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ 登录成功，已跳转到dashboard！');
    
    // 检查localStorage中的token
    const token = await page.evaluate(() => {
      return localStorage.getItem('token');
    });
    console.log('🎫 Token存在:', !!token);
    if (token) {
      console.log('🎫 Token前缀:', token.substring(0, 20) + '...');
    }
    
    // 手动导航到仓库页面
    console.log('📂 导航到仓库页面...');
    await page.goto('http://localhost:3000/repositories');
    await page.waitForLoadState('networkidle');
    
    // 等待页面加载完成
    await page.waitForTimeout(2000);
    
    // 等待一段时间让API请求完成
    await page.waitForTimeout(3000);
    
    console.log('📸 截图保存...');
    await page.screenshot({ path: 'test/repositories_page_screenshot.png', fullPage: true });
    
    console.log('✅ 测试完成！');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    if (page) {
      await page.screenshot({ path: 'test/repositories_error_screenshot.png', fullPage: true });
    }
  } finally {
    if (browser) {
      console.log('🔚 关闭浏览器...');
      await browser.close();
    }
  }
}

// 运行测试
testRepositoriesAPI().catch(console.error);