const { chromium } = require('playwright');

async function testFrontendLogin() {
  let browser;
  let context;
  let page;
  
  try {
    console.log('🚀 启动Playwright测试...');
    
    // 启动浏览器
    browser = await chromium.launch({ 
      headless: false, // 设置为false以便观察测试过程
      slowMo: 1000 // 减慢操作速度以便观察
    });
    
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    page = await context.newPage();
    
    // 监听控制台日志
    page.on('console', msg => {
      console.log(`浏览器控制台: ${msg.text()}`);
    });
    
    // 监听网络请求
    page.on('response', response => {
      if (response.url().includes('/auth/')) {
        console.log(`API请求: ${response.request().method()} ${response.url()} - 状态: ${response.status()}`);
      }
    });
    
    console.log('📱 导航到登录页面...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // 等待页面加载
    await page.waitForSelector('input[type="text"], input[placeholder*="用户名"], input[placeholder*="username"]', { timeout: 10000 });
    
    console.log('✍️ 填写登录表单...');
    
    // 查找用户名输入框
    const usernameSelector = 'input[type="text"], input[placeholder*="用户名"], input[placeholder*="username"]';
    await page.fill(usernameSelector, 'validuser');
    
    // 查找密码输入框
    const passwordSelector = 'input[type="password"], input[placeholder*="密码"], input[placeholder*="password"]';
    await page.fill(passwordSelector, 'Password123!');
    
    console.log('🔐 点击登录按钮...');
    
    // 查找并点击登录按钮
    const loginButtonSelector = 'button[type="submit"], button:has-text("登录"), button:has-text("Login"), .login-btn';
    await page.click(loginButtonSelector);
    
    console.log('⏳ 等待登录响应...');
    
    // 等待页面跳转或错误信息
    try {
      // 等待URL变化到dashboard或者等待错误信息出现
      await Promise.race([
        page.waitForURL('**/dashboard**', { timeout: 10000 }),
        page.waitForSelector('.error, .alert-danger, [class*="error"]', { timeout: 10000 })
      ]);
      
      const currentUrl = page.url();
      console.log(`当前URL: ${currentUrl}`);
      
      if (currentUrl.includes('/dashboard')) {
        console.log('✅ 登录成功！页面已跳转到Dashboard');
        
        // 截图保存成功状态
        await page.screenshot({ path: 'test/login_success_screenshot.png', fullPage: true });
        console.log('📸 成功截图已保存到 test/login_success_screenshot.png');
        
        return { success: true, message: '登录测试通过' };
      } else {
        // 检查是否有错误信息
        const errorElement = await page.$('.error, .alert-danger, [class*="error"]');
        if (errorElement) {
          const errorText = await errorElement.textContent();
          console.log(`❌ 登录失败，错误信息: ${errorText}`);
          return { success: false, message: `登录失败: ${errorText}` };
        } else {
          console.log('❌ 登录后页面未跳转到Dashboard');
          return { success: false, message: '登录后页面未正确跳转' };
        }
      }
    } catch (error) {
      console.log('⏰ 等待超时，检查当前页面状态...');
      
      const currentUrl = page.url();
      console.log(`当前URL: ${currentUrl}`);
      
      // 截图保存当前状态
      await page.screenshot({ path: 'test/login_timeout_screenshot.png', fullPage: true });
      console.log('📸 超时截图已保存到 test/login_timeout_screenshot.png');
      
      return { success: false, message: `登录测试超时，当前URL: ${currentUrl}` };
    }
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error.message);
    
    if (page) {
      await page.screenshot({ path: 'test/login_error_screenshot.png', fullPage: true });
      console.log('📸 错误截图已保存到 test/login_error_screenshot.png');
    }
    
    return { success: false, message: `测试错误: ${error.message}` };
  } finally {
    if (browser) {
      console.log('🔚 关闭浏览器...');
      await browser.close();
    }
  }
}

// 运行测试
if (require.main === module) {
  testFrontendLogin()
    .then(result => {
      console.log('\n📊 测试结果:');
      console.log(`状态: ${result.success ? '✅ 通过' : '❌ 失败'}`);
      console.log(`信息: ${result.message}`);
      
      process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 测试运行失败:', error);
      process.exit(1);
    });
}

module.exports = { testFrontendLogin };