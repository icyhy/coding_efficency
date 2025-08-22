<template>
  <div class="app-wrapper" :class="{ 'sidebar-collapsed': collapsed, 'mobile': isMobile }">
    <!-- 侧边栏 -->
    <div 
      class="sidebar-container" 
      :class="{ 'collapsed': collapsed, 'mobile-open': mobileMenuOpen }"
    >
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <i class="el-icon-data-analysis"></i>
        </div>
        <div class="logo-text" v-show="!collapsed">
          代码效率分析
        </div>
      </div>

      <!-- 菜单 -->
      <div class="sidebar-menu">
        <el-menu
          :default-active="activeMenu"
          :collapse="collapsed"
          :unique-opened="true"
          router
          background-color="#fff"
          text-color="#606266"
          active-text-color="#409eff"
        >
          <el-menu-item index="/dashboard">
            <i class="el-icon-odometer menu-icon"></i>
            <span class="menu-title">仪表盘</span>
          </el-menu-item>

          <el-submenu index="/analytics">
            <template #title>
              <i class="el-icon-data-analysis menu-icon"></i>
              <span class="menu-title">数据分析</span>
            </template>
            <el-menu-item index="/analytics/commits">
              <i class="el-icon-document menu-icon"></i>
              <span class="menu-title">提交分析</span>
            </el-menu-item>
            <el-menu-item index="/analytics/merge-requests">
              <i class="el-icon-connection menu-icon"></i>
              <span class="menu-title">合并请求</span>
            </el-menu-item>
            <el-menu-item index="/analytics/efficiency">
              <i class="el-icon-trophy menu-icon"></i>
              <span class="menu-title">效率评分</span>
            </el-menu-item>
            <el-menu-item index="/analytics/time-distribution">
              <i class="el-icon-time menu-icon"></i>
              <span class="menu-title">时间分布</span>
            </el-menu-item>
          </el-submenu>

          <el-menu-item index="/repositories">
            <i class="el-icon-folder menu-icon"></i>
            <span class="menu-title">仓库管理</span>
          </el-menu-item>

          <el-menu-item index="/settings">
            <i class="el-icon-setting menu-icon"></i>
            <span class="menu-title">系统设置</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 折叠按钮 -->
      <div class="sidebar-footer" v-show="!isMobile">
        <button 
          class="collapse-btn" 
          :class="{ 'collapsed': collapsed }"
          @click="toggleSidebar"
        >
          <i class="el-icon-s-fold collapse-icon"></i>
        </button>
      </div>
    </div>

    <!-- 移动端遮罩 -->
    <div 
      class="sidebar-overlay" 
      :class="{ 'show': mobileMenuOpen }"
      @click="closeMobileMenu"
      v-show="isMobile"
    ></div>

    <!-- 主内容区域 -->
    <div class="main-container" :class="{ 'sidebar-collapsed': collapsed }">
      <!-- 顶部导航 -->
      <div class="navbar">
        <div class="navbar-left">
          <!-- 移动端菜单按钮 -->
          <button 
            class="mobile-menu-btn" 
            @click="toggleMobileMenu"
            v-show="isMobile"
          >
            <i class="el-icon-menu"></i>
          </button>

          <!-- 面包屑 -->
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item 
              v-for="item in breadcrumbs" 
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="navbar-right">
          <!-- 用户信息 -->
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar">
                {{ userInitial }}
              </el-avatar>
              <span class="username">{{ username }}</span>
              <i class="el-icon-arrow-down"></i>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <i class="el-icon-user"></i>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <i class="el-icon-setting"></i>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <i class="el-icon-switch-button"></i>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="page-container">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Layout',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    // 响应式数据
    const collapsed = ref(false)
    const mobileMenuOpen = ref(false)
    const isMobile = ref(false)

    // 计算属性
    const activeMenu = computed(() => {
      const { path } = route
      return path
    })

    const username = computed(() => {
      return store.getters['auth/user']?.username || 'User'
    })

    const userAvatar = computed(() => {
      return store.getters['auth/user']?.avatar || ''
    })

    const userInitial = computed(() => {
      return username.value.charAt(0).toUpperCase()
    })

    // 面包屑导航
    const breadcrumbs = computed(() => {
      const matched = route.matched.filter(item => item.meta && item.meta.title)
      const breadcrumbList = []
      
      matched.forEach(item => {
        breadcrumbList.push({
          path: item.path,
          title: item.meta.title
        })
      })
      
      return breadcrumbList
    })

    // 方法
    const toggleSidebar = () => {
      collapsed.value = !collapsed.value
      localStorage.setItem('sidebarCollapsed', collapsed.value)
    }

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
    }

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
    }

    const handleUserCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/profile')
          break
        case 'settings':
          router.push('/settings')
          break
        case 'logout':
          handleLogout()
          break
      }
    }

    const handleLogout = async () => {
      try {
        await store.dispatch('auth/logout')
        ElMessage.success('退出登录成功')
        router.push('/login')
      } catch (error) {
        ElMessage.error('退出登录失败')
      }
    }

    // 检测屏幕尺寸
    const checkMobile = () => {
      isMobile.value = window.innerWidth < 768
      if (isMobile.value) {
        mobileMenuOpen.value = false
      }
    }

    // 生命周期
    onMounted(() => {
      // 恢复侧边栏状态
      const savedCollapsed = localStorage.getItem('sidebarCollapsed')
      if (savedCollapsed !== null) {
        collapsed.value = JSON.parse(savedCollapsed)
      }

      // 检测移动端
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      collapsed,
      mobileMenuOpen,
      isMobile,
      activeMenu,
      username,
      userAvatar,
      userInitial,
      breadcrumbs,
      toggleSidebar,
      toggleMobileMenu,
      closeMobileMenu,
      handleUserCommand
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.app-wrapper {
  position: relative;
  height: 100vh;
  width: 100%;
}

.navbar {
  height: $header-height;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 9;

  .navbar-left {
    display: flex;
    align-items: center;

    .mobile-menu-btn {
      width: 40px;
      height: 40px;
      border: none;
      background: none;
      color: $text-color;
      font-size: 18px;
      cursor: pointer;
      border-radius: 4px;
      margin-right: 15px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba($primary-color, 0.1);
        color: $primary-color;
      }
    }

    .breadcrumb {
      font-size: 14px;
    }
  }

  .navbar-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba($primary-color, 0.1);
      }

      .username {
        margin: 0 8px;
        font-size: 14px;
        color: $text-color;
      }

      .el-icon-arrow-down {
        font-size: 12px;
        color: $text-color-secondary;
      }
    }
  }
}

@include respond-to('mobile') {
  .navbar {
    padding: 0 15px;
  }
}
</style>