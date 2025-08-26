/**
 * 测试前端登录功能
 * 使用Puppeteer自动化测试登录流程
 */

async function testFrontendLogin() {
  let browser;
  
  try {
    const puppeteer = require('puppeteer');
    console.log('🚀 启动浏览器测试...');
    
    browser = await puppeteer.launch({
      headless: false, // 显示浏览器界面
      defaultViewport: null,
      args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // 监听控制台输出
    page.on('console', msg => {
      console.log('🖥️ 浏览器控制台:', msg.text());
    });
    
    // 监听页面错误
    page.on('pageerror', error => {
      console.error('❌ 页面错误:', error.message);
    });
    
    console.log('📱 访问登录页面...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle2' });
    
    // 等待登录表单加载
    await page.waitForSelector('input[placeholder*="用户名"], input[type="text"]', { timeout: 10000 });
    console.log('✅ 登录页面加载完成');
    
    // 填写登录信息
    console.log('📝 填写登录信息...');
    await page.type('input[placeholder*="用户名"], input[type="text"]', 'validuser');
    await page.type('input[placeholder*="密码"], input[type="password"]', 'Password123!');
    
    // 点击登录按钮
    console.log('🔐 点击登录按钮...');
    await page.click('button[type="submit"], .el-button--primary');
    
    // 等待页面跳转或响应
    console.log('⏳ 等待登录响应...');
    await page.waitForTimeout(3000);
    
    // 检查当前URL
    const currentUrl = page.url();
    console.log('🌐 当前页面URL:', currentUrl);
    
    if (currentUrl.includes('/dashboard')) {
      console.log('🎉 登录成功！已跳转到Dashboard页面');
      
      // 检查Dashboard页面是否正确加载
      try {
        await page.waitForSelector('.dashboard, [class*="dashboard"]', { timeout: 5000 });
        console.log('✅ Dashboard页面内容加载完成');
      } catch (e) {
        console.log('⚠️ Dashboard页面内容可能还在加载中');
      }
      
    } else if (currentUrl.includes('/login')) {
      console.log('❌ 登录失败，仍在登录页面');
      
      // 检查是否有错误消息
      try {
        const errorMsg = await page.$eval('.el-message--error, .error-message', el => el.textContent);
        console.log('🚨 错误消息:', errorMsg);
      } catch (e) {
        console.log('🔍 未找到明显的错误消息');
      }
    } else {
      console.log('🤔 页面跳转到了意外的位置:', currentUrl);
    }
    
    // 保持浏览器打开一段时间以便观察
    console.log('⏸️ 保持浏览器打开10秒以便观察...');
    await page.waitForTimeout(10000);
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error.message);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔚 浏览器已关闭');
    }
  }
}

// 检查是否安装了puppeteer
try {
  require('puppeteer');
  testFrontendLogin();
} catch (e) {
  console.log('⚠️ 未安装puppeteer，跳过自动化测试');
  console.log('💡 请手动在浏览器中访问 http://localhost:3000/login 进行测试');
  console.log('🔑 测试账户: validuser / Password123!');
  console.log('');
  console.log('📋 手动测试步骤:');
  console.log('1. 在浏览器中打开 http://localhost:3000/login');
  console.log('2. 输入用户名: validuser');
  console.log('3. 输入密码: Password123!');
  console.log('4. 点击登录按钮');
  console.log('5. 检查是否成功跳转到 http://localhost:3000/dashboard');
  console.log('');
  console.log('✅ 如果跳转成功，说明登录功能已修复');
  console.log('❌ 如果仍停留在登录页面，请检查浏览器控制台错误信息');
}