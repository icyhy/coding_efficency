<template>
  <div class="settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">配置系统参数和个人偏好</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧菜单 -->
      <el-col :xs="24" :sm="6" :md="5">
        <el-card class="menu-card">
          <el-menu
            v-model:default-active="activeTab"
            class="settings-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="profile">
              <i class="el-icon-user"></i>
              <span>个人资料</span>
            </el-menu-item>
            <el-menu-item index="account">
              <i class="el-icon-key"></i>
              <span>账户安全</span>
            </el-menu-item>
            <el-menu-item index="notification">
              <i class="el-icon-bell"></i>
              <span>通知设置</span>
            </el-menu-item>
            <el-menu-item index="system">
              <i class="el-icon-setting"></i>
              <span>系统配置</span>
            </el-menu-item>

            <el-menu-item index="backup">
              <i class="el-icon-folder-opened"></i>
              <span>备份恢复</span>
            </el-menu-item>
            <el-menu-item index="about">
              <i class="el-icon-info"></i>
              <span>关于系统</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 右侧内容 -->
      <el-col :xs="24" :sm="18" :md="19">
        <!-- 个人资料 -->
        <el-card v-show="activeTab === 'profile'" class="content-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">个人资料</span>
              <el-button type="primary" @click="saveProfile" :loading="saving">
                保存更改
              </el-button>
            </div>
          </template>
          
          <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="120px">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="头像">
                  <div class="avatar-upload">
                    <el-avatar :src="profileForm.avatar" :size="80">
                      {{ profileForm.username.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <el-button size="small" @click="uploadAvatar" style="margin-left: 16px;">
                      更换头像
                    </el-button>
                  </div>
                </el-form-item>
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="真实姓名" prop="realName">
                  <el-input v-model="profileForm.realName" />
                </el-form-item>
                <el-form-item label="部门" prop="department">
                  <el-input v-model="profileForm.department" />
                </el-form-item>
                <el-form-item label="职位" prop="position">
                  <el-input v-model="profileForm.position" />
                </el-form-item>
                <el-form-item label="个人简介">
                  <el-input
                    v-model="profileForm.bio"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入个人简介"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 账户安全 -->
        <el-card v-show="activeTab === 'account'" class="content-card">
          <template #header>
            <span class="card-title">账户安全</span>
          </template>
          
          <div class="security-section">
            <div class="security-item">
              <div class="item-info">
                <h3>登录密码</h3>
                <p>定期更换密码可以提高账户安全性</p>
              </div>
              <el-button @click="showChangePasswordDialog">修改密码</el-button>
            </div>
            
            <el-divider />
            
            <div class="security-item">
              <div class="item-info">
                <h3>两步验证</h3>
                <p>开启两步验证后，登录时需要输入验证码</p>
              </div>
              <el-switch v-model="securitySettings.twoFactorAuth" @change="toggleTwoFactor" />
            </div>
            
            <el-divider />
            
            <div class="security-item">
              <div class="item-info">
                <h3>登录通知</h3>
                <p>有新设备登录时发送邮件通知</p>
              </div>
              <el-switch v-model="securitySettings.loginNotification" @change="updateSecuritySettings" />
            </div>
            
            <el-divider />
            
            <div class="security-item">
              <div class="item-info">
                <h3>会话管理</h3>
                <p>查看和管理当前登录的设备</p>
              </div>
              <el-button @click="showSessionsDialog">管理会话</el-button>
            </div>
          </div>
        </el-card>

        <!-- 通知设置 -->
        <el-card v-show="activeTab === 'notification'" class="content-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">通知设置</span>
              <el-button type="primary" @click="saveNotificationSettings" :loading="saving">
                保存设置
              </el-button>
            </div>
          </template>
          
          <div class="notification-section">
            <h3>邮件通知</h3>
            <el-checkbox-group v-model="notificationSettings.email">
              <el-checkbox label="commits">代码提交通知</el-checkbox>
              <el-checkbox label="mergeRequests">合并请求通知</el-checkbox>
              <el-checkbox label="issues">问题反馈通知</el-checkbox>
              <el-checkbox label="security">安全警告通知</el-checkbox>
              <el-checkbox label="system">系统维护通知</el-checkbox>
            </el-checkbox-group>
            
            <el-divider />
            
            <h3>浏览器通知</h3>
            <el-checkbox-group v-model="notificationSettings.browser">
              <el-checkbox label="realtime">实时消息推送</el-checkbox>
              <el-checkbox label="mentions">@提及通知</el-checkbox>
              <el-checkbox label="assignments">任务分配通知</el-checkbox>
            </el-checkbox-group>
            
            <el-divider />
            
            <h3>通知时间</h3>
            <el-form label-width="120px">
              <el-form-item label="工作时间">
                <el-time-picker
                  v-model="notificationSettings.workHours.start"
                  placeholder="开始时间"
                  format="HH:mm"
                  value-format="HH:mm"
                />
                <span style="margin: 0 8px;">至</span>
                <el-time-picker
                  v-model="notificationSettings.workHours.end"
                  placeholder="结束时间"
                  format="HH:mm"
                  value-format="HH:mm"
                />
              </el-form-item>
              <el-form-item label="免打扰模式">
                <el-switch v-model="notificationSettings.doNotDisturb" />
                <span style="margin-left: 8px; color: #999;">开启后在非工作时间不接收通知</span>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <!-- 系统配置 -->
        <el-card v-show="activeTab === 'system'" class="content-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">系统配置</span>
              <el-button type="primary" @click="saveSystemSettings" :loading="saving">
                保存配置
              </el-button>
            </div>
          </template>
          
          <el-form :model="systemSettings" label-width="150px">
            <h3>基础设置</h3>
            <el-form-item label="系统名称">
              <el-input v-model="systemSettings.systemName" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input v-model="systemSettings.systemDescription" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="默认语言">
              <el-select v-model="systemSettings.defaultLanguage">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item label="时区">
              <el-select v-model="systemSettings.timezone">
                <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                <el-option label="伦敦时间 (UTC+0)" value="Europe/London" />
              </el-select>
            </el-form-item>
            
            <el-divider />
            
            <h3>数据设置</h3>
            <el-form-item label="数据保留期">
              <el-select v-model="systemSettings.dataRetentionDays">
                <el-option label="30天" :value="30" />
                <el-option label="90天" :value="90" />
                <el-option label="180天" :value="180" />
                <el-option label="365天" :value="365" />
                <el-option label="永久保留" :value="-1" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动同步间隔">
              <el-select v-model="systemSettings.syncInterval">
                <el-option label="每小时" value="hourly" />
                <el-option label="每天" value="daily" />
                <el-option label="每周" value="weekly" />
              </el-select>
            </el-form-item>
            <el-form-item label="启用缓存">
              <el-switch v-model="systemSettings.enableCache" />
            </el-form-item>
            
            <el-divider />
            
            <h3>安全设置</h3>
            <el-form-item label="会话超时时间">
              <el-select v-model="systemSettings.sessionTimeout">
                <el-option label="30分钟" :value="30" />
                <el-option label="1小时" :value="60" />
                <el-option label="2小时" :value="120" />
                <el-option label="8小时" :value="480" />
              </el-select>
            </el-form-item>
            <el-form-item label="强制HTTPS">
              <el-switch v-model="systemSettings.forceHttps" />
            </el-form-item>
            <el-form-item label="启用审计日志">
              <el-switch v-model="systemSettings.enableAuditLog" />
            </el-form-item>
          </el-form>
        </el-card>




        <!-- 备份恢复 -->
        <el-card v-show="activeTab === 'backup'" class="content-card">
          <template #header>
            <span class="card-title">备份恢复</span>
          </template>
          
          <div class="backup-section">
            <div class="backup-actions">
              <el-button type="primary" @click="createBackup" :loading="backing">
                <i class="el-icon-download"></i>
                创建备份
              </el-button>
              <el-button @click="showRestoreDialog">
                <i class="el-icon-upload2"></i>
                恢复备份
              </el-button>
              <el-button @click="loadBackupList">
                <i class="el-icon-refresh"></i>
                刷新列表
              </el-button>
            </div>
            
            <el-divider />
            
            <div class="backup-settings">
              <h3>自动备份设置</h3>
              <el-form label-width="120px">
                <el-form-item label="启用自动备份">
                  <el-switch v-model="backupSettings.autoBackup" />
                </el-form-item>
                <el-form-item label="备份频率" v-if="backupSettings.autoBackup">
                  <el-select v-model="backupSettings.frequency">
                    <el-option label="每天" value="daily" />
                    <el-option label="每周" value="weekly" />
                    <el-option label="每月" value="monthly" />
                  </el-select>
                </el-form-item>
                <el-form-item label="保留数量" v-if="backupSettings.autoBackup">
                  <el-input-number v-model="backupSettings.keepCount" :min="1" :max="30" />
                </el-form-item>
              </el-form>
            </div>
            
            <el-divider />
            
            <div class="backup-list">
              <h3>备份历史</h3>
              <el-table :data="backupList" v-loading="loadingBackups">
                <el-table-column prop="name" label="备份名称" />
                <el-table-column prop="size" label="文件大小" />
                <el-table-column prop="created_at" label="创建时间">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click="downloadBackup(row)">
                      下载
                    </el-button>
                    <el-button type="text" size="small" @click="restoreBackup(row)">
                      恢复
                    </el-button>
                    <el-button type="text" size="small" @click="deleteBackup(row)" class="danger">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>

        <!-- 关于系统 -->
        <el-card v-show="activeTab === 'about'" class="content-card">
          <template #header>
            <span class="card-title">关于系统</span>
          </template>
          
          <div class="about-section">
            <div class="system-info">
              <div class="info-item">
                <span class="label">系统名称:</span>
                <span class="value">代码效率分析平台</span>
              </div>
              <div class="info-item">
                <span class="label">系统版本:</span>
                <span class="value">v1.0.0</span>
              </div>
              <div class="info-item">
                <span class="label">构建时间:</span>
                <span class="value">2024-01-15 10:30:00</span>
              </div>
              <div class="info-item">
                <span class="label">运行环境:</span>
                <span class="value">Python 3.9 + Vue.js 3</span>
              </div>
              <div class="info-item">
                <span class="label">数据库:</span>
                <span class="value">SQLite 3.36</span>
              </div>
            </div>
            
            <el-divider />
            
            <div class="system-status">
              <h3>系统状态</h3>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon success">
                      <i class="el-icon-success"></i>
                    </div>
                    <div class="status-info">
                      <div class="status-title">服务状态</div>
                      <div class="status-value">正常运行</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon warning">
                      <i class="el-icon-warning"></i>
                    </div>
                    <div class="status-info">
                      <div class="status-title">磁盘使用</div>
                      <div class="status-value">78%</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon success">
                      <i class="el-icon-success"></i>
                    </div>
                    <div class="status-info">
                      <div class="status-title">内存使用</div>
                      <div class="status-value">45%</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <el-divider />
            
            <div class="license-info">
              <h3>许可证信息</h3>
              <p>本系统采用 MIT 许可证，允许自由使用、修改和分发。</p>
              <p>© 2024 代码效率分析平台. All rights reserved.</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordVisible" title="修改密码" width="500px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input v-model="passwordForm.currentPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="changePasswordVisible = false">取消</el-button>
          <el-button type="primary" @click="changePassword" :loading="changing">
            确认修改
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'


export default {
  name: 'Settings',
  setup() {
    // 响应式数据
    const activeTab = ref('profile')
    const saving = ref(false)

    const backing = ref(false)
    const changing = ref(false)
    const loadingBackups = ref(false)
    const changePasswordVisible = ref(false)
    
    const profileFormRef = ref(null)
    const passwordFormRef = ref(null)
    
    const backupList = ref([])

    // 个人资料表单
    const profileForm = reactive({
      username: 'admin',
      email: 'admin@example.com',
      phone: '13800138000',
      realName: '管理员',
      department: '技术部',
      position: '系统管理员',
      bio: '负责系统维护和用户管理',
      avatar: ''
    })

    const profileRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }

    // 密码修改表单
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const passwordRules = {
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    // 安全设置
    const securitySettings = reactive({
      twoFactorAuth: false,
      loginNotification: true
    })

    // 通知设置
    const notificationSettings = reactive({
      email: ['commits', 'security', 'system'],
      browser: ['realtime', 'mentions'],
      workHours: {
        start: '09:00',
        end: '18:00'
      },
      doNotDisturb: false
    })

    // 系统设置
    const systemSettings = reactive({
      systemName: '代码效率分析平台',
      systemDescription: '基于Git数据的开发效率分析和可视化平台',
      defaultLanguage: 'zh-CN',
      timezone: 'Asia/Shanghai',
      dataRetentionDays: 365,
      syncInterval: 'daily',
      enableCache: true,
      sessionTimeout: 120,
      forceHttps: false,
      enableAuditLog: true
    })



    // 备份设置
    const backupSettings = reactive({
      autoBackup: false,
      frequency: 'weekly',
      keepCount: 10
    })

    // 方法
    const handleMenuSelect = (key) => {
      activeTab.value = key
    }

    const saveProfile = async () => {
      try {
        await profileFormRef.value.validate()
        saving.value = true
        
        // 模拟保存
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('个人资料保存成功')
      } catch (error) {
        console.error('表单验证失败:', error)
      } finally {
        saving.value = false
      }
    }

    const uploadAvatar = () => {
      ElMessage.info('头像上传功能开发中...')
    }

    const showChangePasswordDialog = () => {
      changePasswordVisible.value = true
    }

    const changePassword = async () => {
      try {
        await passwordFormRef.value.validate()
        changing.value = true
        
        // 模拟修改密码
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('密码修改成功')
        changePasswordVisible.value = false
        
        // 重置表单
        passwordForm.currentPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
        
      } catch (error) {
        console.error('表单验证失败:', error)
      } finally {
        changing.value = false
      }
    }

    const toggleTwoFactor = (value) => {
      if (value) {
        ElMessage.info('两步验证功能开发中...')
      } else {
        ElMessage.success('两步验证已关闭')
      }
    }

    const updateSecuritySettings = () => {
      ElMessage.success('安全设置已更新')
    }

    const showSessionsDialog = () => {
      ElMessage.info('会话管理功能开发中...')
    }

    const saveNotificationSettings = async () => {
      try {
        saving.value = true
        
        // 模拟保存
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('通知设置保存成功')
      } finally {
        saving.value = false
      }
    }

    const saveSystemSettings = async () => {
      try {
        saving.value = true
        
        // 模拟保存
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('系统配置保存成功')
      } finally {
        saving.value = false
      }
    }



    const createBackup = async () => {
      try {
        backing.value = true
        
        // 模拟创建备份
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        ElMessage.success('备份创建成功')
        loadBackupList()
      } catch (error) {
        ElMessage.error('备份创建失败')
      } finally {
        backing.value = false
      }
    }

    const loadBackupList = async () => {
      try {
        loadingBackups.value = true
        
        // 模拟加载备份列表
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        backupList.value = [
          {
            id: 1,
            name: 'backup_2024_01_15_10_30.sql',
            size: '2.5 MB',
            created_at: new Date('2024-01-15T10:30:00')
          },
          {
            id: 2,
            name: 'backup_2024_01_14_10_30.sql',
            size: '2.3 MB',
            created_at: new Date('2024-01-14T10:30:00')
          },
          {
            id: 3,
            name: 'backup_2024_01_13_10_30.sql',
            size: '2.1 MB',
            created_at: new Date('2024-01-13T10:30:00')
          }
        ]
      } finally {
        loadingBackups.value = false
      }
    }

    const showRestoreDialog = () => {
      ElMessage.info('恢复备份功能开发中...')
    }

    const downloadBackup = (backup) => {
      ElMessage.success(`下载备份: ${backup.name}`)
    }

    const restoreBackup = async (backup) => {
      try {
        await ElMessageBox.confirm(
          `确定要恢复备份 "${backup.name}" 吗？此操作将覆盖当前数据。`,
          '确认恢复',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        ElMessage.success(`恢复备份: ${backup.name}`)
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('恢复失败')
        }
      }
    }

    const deleteBackup = async (backup) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除备份 "${backup.name}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        ElMessage.success(`删除备份: ${backup.name}`)
        loadBackupList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    // 生命周期
    onMounted(() => {
      loadBackupList()
    })

    return {
      activeTab,
      saving,

      backing,
      changing,
      loadingBackups,

      changePasswordVisible,
      profileFormRef,
      passwordFormRef,
      backupList,

      profileForm,
      profileRules,
      passwordForm,
      passwordRules,
      securitySettings,
      notificationSettings,
      systemSettings,

      backupSettings,
      handleMenuSelect,
      saveProfile,
      uploadAvatar,
      showChangePasswordDialog,
      changePassword,
      toggleTwoFactor,
      updateSecuritySettings,
      showSessionsDialog,
      saveNotificationSettings,
      saveSystemSettings,

      createBackup,
      loadBackupList,
      showRestoreDialog,
      downloadBackup,
      restoreBackup,
      deleteBackup,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.settings {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  
  .page-title {
    font-size: 28px;
    font-weight: 600;
    color: $text-color;
    margin-bottom: 8px;
  }
  
  .page-subtitle {
    font-size: 14px;
    color: $text-color-secondary;
  }
}

.menu-card {
  .settings-menu {
    border: none;
    
    .el-menu-item {
      border-radius: 8px;
      margin-bottom: 4px;
      
      &:hover {
        background-color: $bg-color-light;
      }
      
      &.is-active {
        background-color: $primary-color;
        color: #fff;
        
        i {
          color: #fff;
        }
      }
      
      i {
        margin-right: 8px;
        color: $text-color-secondary;
      }
    }
  }
}

.content-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title {
      font-size: 18px;
      font-weight: 600;
      color: $text-color;
    }
  }
  
  .avatar-upload {
    display: flex;
    align-items: center;
  }
}

.security-section {
  .security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    
    .item-info {
      flex: 1;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        color: $text-color;
        margin: 0 0 4px 0;
      }
      
      p {
        font-size: 14px;
        color: $text-color-secondary;
        margin: 0;
      }
    }
  }
}

.notification-section {
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
    margin-bottom: 16px;
  }
  
  .el-checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.integration-section {
  .integration-item {
    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        color: $text-color;
        margin: 0;
      }
    }
    
    .item-config {
      background: $bg-color-light;
      padding: 16px;
      border-radius: 8px;
    }
  }
  
  .test-message {
    margin-left: 12px;
    font-size: 12px;
    
    &.success {
      color: $success-color;
    }
    
    &.failed {
      color: $danger-color;
    }
    
    &.pending {
      color: $text-color-secondary;
    }
  }
}

.backup-section {
  .backup-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
  }
  
  .backup-settings {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: 16px;
    }
  }
  
  .backup-list {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: 16px;
    }
    
    .danger {
      color: $danger-color;
    }
  }
}

.about-section {
  .system-info {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid $border-color-lighter;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        font-weight: 500;
        color: $text-color-secondary;
      }
      
      .value {
        color: $text-color;
      }
    }
  }
  
  .system-status {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: 16px;
    }
    
    .status-item {
      display: flex;
      align-items: center;
      padding: 16px;
      background: $bg-color-light;
      border-radius: 8px;
      
      .status-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        
        &.success {
          background-color: $success-color;
          color: #fff;
        }
        
        &.warning {
          background-color: $warning-color;
          color: #fff;
        }
        
        &.danger {
          background-color: $danger-color;
          color: #fff;
        }
      }
      
      .status-info {
        .status-title {
          font-size: 14px;
          color: $text-color-secondary;
          margin-bottom: 4px;
        }
        
        .status-value {
          font-size: 16px;
          font-weight: 600;
          color: $text-color;
        }
      }
    }
  }
  
  .license-info {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: 16px;
    }
    
    p {
      font-size: 14px;
      color: $text-color-secondary;
      line-height: 1.6;
      margin-bottom: 8px;
    }
  }
}

@include respond-to('mobile') {
  .settings {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 16px;
    
    .page-title {
      font-size: 24px;
    }
  }
  
  .backup-section {
    .backup-actions {
      flex-direction: column;
    }
  }
  
  .security-section {
    .security-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }
}
</style>