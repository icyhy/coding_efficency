<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧背景 -->
      <div class="login-bg">
        <div class="bg-content">
          <h1 class="bg-title">代码效率分析平台</h1>
          <p class="bg-subtitle">基于阿里云效的智能代码分析与效率评估系统</p>
          <div class="bg-features">
            <div class="feature-item">
              <i class="el-icon-data-analysis"></i>
              <span>智能数据分析</span>
            </div>
            <div class="feature-item">
              <i class="el-icon-trophy"></i>
              <span>效率评分</span>
            </div>
            <div class="feature-item">
              <i class="el-icon-time"></i>
              <span>时间分布统计</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form">
        <div class="form-container">
          <div class="form-header">
            <h2 class="form-title">欢迎登录</h2>
            <p class="form-subtitle">请输入您的账号信息</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form-content"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                prefix-icon="el-icon-user"
                :disabled="loading"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="el-icon-lock"
                :disabled="loading"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="loginForm.rememberMe">
                  记住我
                </el-checkbox>
                <el-link type="primary" :underline="false">
                  忘记密码？
                </el-link>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <p class="register-link">
              还没有账号？
              <el-link type="primary" :underline="false" @click="goToRegister">
                立即注册
              </el-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()

    // 表单引用
    const loginFormRef = ref(null)

    // 响应式数据
    const loading = ref(false)
    const loginForm = reactive({
      username: '',
      password: '',
      rememberMe: false
    })

    // 表单验证规则
    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
      ]
    }

    // 方法
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      try {
        const valid = await loginFormRef.value.validate()
        if (!valid) return

        loading.value = true
        
        // 调用登录接口
        await store.dispatch('auth/login', {
          username: loginForm.username,
          password: loginForm.password,
          rememberMe: loginForm.rememberMe
        })

        ElMessage.success('登录成功')
        
        // 等待更长时间确保Token完全设置到axios拦截器和Cookie中
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 验证Token是否正确设置
        const currentToken = getToken()
        if (!currentToken) {
          throw new Error('Token设置失败，请重试')
        }
        
        // 跳转到目标页面或首页
        const redirect = route.query.redirect || '/dashboard'
        router.push(redirect)
        
      } catch (error) {
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }

    const goToRegister = () => {
      router.push('/register')
    }

    // 生命周期
    onMounted(() => {
      // 如果已经登录，直接跳转
      if (getToken()) {
        router.push('/dashboard')
        return
      }

      // 开发环境下预填充表单
      if (process.env.NODE_ENV === 'development') {
        loginForm.username = 'admin'
        loginForm.password = 'admin123'
      }
    })

    return {
      loginFormRef,
      loading,
      loginForm,
      loginRules,
      handleLogin,
      goToRegister
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-wrapper {
  width: 100%;
  max-width: 1000px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  min-height: 600px;
}

.login-bg {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
    opacity: 0.3;
  }
  
  .bg-content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: #fff;
    
    .bg-title {
      font-size: 36px;
      font-weight: 700;
      margin-bottom: 16px;
      line-height: 1.2;
    }
    
    .bg-subtitle {
      font-size: 18px;
      opacity: 0.9;
      margin-bottom: 40px;
      line-height: 1.5;
    }
    
    .bg-features {
      display: flex;
      flex-direction: column;
      gap: 20px;
      
      .feature-item {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        font-size: 16px;
        opacity: 0.9;
        
        i {
          font-size: 20px;
        }
      }
    }
  }
}

.login-form {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  
  .form-container {
    width: 100%;
    max-width: 400px;
    
    .form-header {
      text-align: center;
      margin-bottom: 40px;
      
      .form-title {
        font-size: 28px;
        font-weight: 600;
        color: $text-color;
        margin-bottom: 8px;
      }
      
      .form-subtitle {
        font-size: 14px;
        color: $text-color-secondary;
      }
    }
    
    .login-form-content {
      .el-form-item {
        margin-bottom: 24px;
        
        :deep(.el-input__inner) {
          height: 48px;
          border-radius: 8px;
          border: 1px solid $border-color;
          
          &:focus {
            border-color: $primary-color;
            box-shadow: 0 0 0 2px rgba($primary-color, 0.1);
          }
        }
      }
      
      .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .el-checkbox {
          :deep(.el-checkbox__label) {
            font-size: 14px;
            color: $text-color-regular;
          }
        }
        
        .el-link {
          font-size: 14px;
        }
      }
      
      .login-btn {
        width: 100%;
        height: 48px;
        font-size: 16px;
        font-weight: 500;
        border-radius: 8px;
        background: $gradient-primary;
        border: none;
        
        &:hover {
          opacity: 0.9;
        }
      }
    }
    
    .form-footer {
      text-align: center;
      margin-top: 24px;
      
      .register-link {
        font-size: 14px;
        color: $text-color-regular;
        
        .el-link {
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }
}

// 响应式设计
@include respond-to('tablet') {
  .login-wrapper {
    flex-direction: column;
    max-width: 500px;
  }
  
  .login-bg {
    padding: 40px 30px;
    
    .bg-content {
      .bg-title {
        font-size: 28px;
      }
      
      .bg-subtitle {
        font-size: 16px;
      }
      
      .bg-features {
        flex-direction: row;
        justify-content: center;
        flex-wrap: wrap;
        
        .feature-item {
          flex-direction: column;
          gap: 8px;
          font-size: 14px;
        }
      }
    }
  }
  
  .login-form {
    padding: 40px 30px;
  }
}

@include respond-to('mobile') {
  .login-container {
    padding: 10px;
  }
  
  .login-wrapper {
    min-height: auto;
  }
  
  .login-bg {
    padding: 30px 20px;
    
    .bg-content {
      .bg-title {
        font-size: 24px;
      }
      
      .bg-subtitle {
        font-size: 14px;
        margin-bottom: 30px;
      }
    }
  }
  
  .login-form {
    padding: 30px 20px;
    
    .form-container {
      .form-header {
        margin-bottom: 30px;
        
        .form-title {
          font-size: 24px;
        }
      }
    }
  }
}
</style>