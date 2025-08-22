<template>
  <div class="users">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-subtitle">管理系统用户和权限</p>
    </div>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名或邮箱"
            prefix-icon="el-icon-search"
            clearable
            @input="handleSearch"
            style="width: 300px;"
          />
          <el-select v-model="roleFilter" placeholder="角色筛选" clearable style="width: 120px; margin-left: 12px;">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
            <el-option label="观察者" value="viewer" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px; margin-left: 12px;">
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="disabled" />
            <el-option label="待激活" value="pending" />
          </el-select>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="showAddDialog">
            <i class="el-icon-plus"></i>
            添加用户
          </el-button>
          <el-button @click="exportUsers">
            <i class="el-icon-download"></i>
            导出
          </el-button>
          <el-button @click="importUsers">
            <i class="el-icon-upload2"></i>
            导入
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in userStats" :key="index">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: stat.color }">
            <i :class="stat.icon"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
            <div class="stat-change" :class="stat.changeType">
              <i :class="stat.changeIcon"></i>
              {{ stat.change }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">用户列表</span>
          <div class="view-toggle">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="table">表格视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 表格视图 -->
      <el-table
        v-if="viewMode === 'table'"
        :data="filteredUsers"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :size="40">
              {{ row.username.charAt(0).toUpperCase() }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewUser(row)">
              查看
            </el-button>
            <el-button type="text" size="small" @click="editUser(row)">
              编辑
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleUserStatus(row)"
              :class="row.status === 'active' ? 'warning' : 'success'"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button type="text" size="small" @click="deleteUser(row)" class="danger">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :lg="8" v-for="user in filteredUsers" :key="user.id">
            <div class="user-card">
              <div class="user-header">
                <div class="user-avatar">
                  <el-avatar :src="user.avatar" :size="60">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="status-indicator" :class="user.status"></div>
                </div>
                <div class="user-info">
                  <h3 class="user-name">{{ user.username }}</h3>
                  <p class="user-email">{{ user.email }}</p>
                  <div class="user-badges">
                    <el-tag :type="getRoleType(user.role)" size="small">
                      {{ getRoleText(user.role) }}
                    </el-tag>
                    <el-tag :type="getStatusType(user.status)" size="small">
                      {{ getStatusText(user.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <div class="user-stats">
                <div class="stat-item">
                  <span class="stat-label">登录次数</span>
                  <span class="stat-value">{{ user.login_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">提交数</span>
                  <span class="stat-value">{{ user.commits_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">活跃天数</span>
                  <span class="stat-value">{{ user.active_days || 0 }}</span>
                </div>
              </div>
              
              <div class="user-meta">
                <div class="meta-item">
                  <i class="el-icon-time"></i>
                  <span>最后登录: {{ user.last_login ? formatDate(user.last_login) : '从未登录' }}</span>
                </div>
                <div class="meta-item">
                  <i class="el-icon-date"></i>
                  <span>创建时间: {{ formatDate(user.created_at) }}</span>
                </div>
              </div>
              
              <div class="user-actions">
                <el-button size="small" @click="viewUser(user)">
                  查看详情
                </el-button>
                <el-button size="small" @click="editUser(user)">
                  编辑用户
                </el-button>
                <el-dropdown @command="(command) => handleUserAction(command, user)">
                  <el-button size="small">
                    更多<i class="el-icon-arrow-down el-icon--right"></i>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="resetPassword">重置密码</el-dropdown-item>
                      <el-dropdown-item command="permissions">权限设置</el-dropdown-item>
                      <el-dropdown-item 
                        :command="user.status === 'active' ? 'disable' : 'enable'"
                      >
                        {{ user.status === 'active' ? '禁用用户' : '启用用户' }}
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除用户</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[12, 24, 48, 96]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加用户' : '编辑用户'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogMode === 'add'">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword" v-if="dialogMode === 'add'">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="disabled">禁用</el-radio>
            <el-radio label="pending">待激活</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ dialogMode === 'add' ? '添加' : '保存' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="800px"
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-header">
          <el-avatar :src="selectedUser.avatar" :size="80">
            {{ selectedUser.username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="detail-info">
            <h2>{{ selectedUser.username }}</h2>
            <p>{{ selectedUser.email }}</p>
            <div class="detail-badges">
              <el-tag :type="getRoleType(selectedUser.role)">
                {{ getRoleText(selectedUser.role) }}
              </el-tag>
              <el-tag :type="getStatusType(selectedUser.status)">
                {{ getStatusText(selectedUser.status) }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-section">
              <h3>基本信息</h3>
              <div class="info-item">
                <span class="label">用户ID:</span>
                <span class="value">{{ selectedUser.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ formatDate(selectedUser.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最后登录:</span>
                <span class="value">{{ selectedUser.last_login ? formatDate(selectedUser.last_login) : '从未登录' }}</span>
              </div>
              <div class="info-item">
                <span class="label">登录次数:</span>
                <span class="value">{{ selectedUser.login_count || 0 }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-section">
              <h3>活动统计</h3>
              <div class="info-item">
                <span class="label">提交数:</span>
                <span class="value">{{ selectedUser.commits_count || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">合并请求:</span>
                <span class="value">{{ selectedUser.merge_requests_count || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">活跃天数:</span>
                <span class="value">{{ selectedUser.active_days || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">代码行数:</span>
                <span class="value">{{ selectedUser.lines_of_code || 0 }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div class="detail-section">
          <h3>权限列表</h3>
          <el-tag v-for="permission in getUserPermissions(selectedUser.role)" :key="permission" style="margin-right: 8px; margin-bottom: 8px;">
            {{ permission }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Users',
  setup() {
    const store = useStore()

    // 响应式数据
    const loading = ref(false)
    const submitting = ref(false)
    const searchKeyword = ref('')
    const roleFilter = ref('')
    const statusFilter = ref('')
    const viewMode = ref('table')
    const dialogVisible = ref(false)
    const detailDialogVisible = ref(false)
    const dialogMode = ref('add')
    const formRef = ref(null)
    const selectedUser = ref(null)

    const users = ref([])
    const userStats = ref([])

    const pagination = reactive({
      page: 1,
      size: 12,
      total: 0
    })

    const form = reactive({
      id: null,
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'developer',
      status: 'active',
      remark: ''
    })

    const formRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== form.password) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    }

    // 计算属性
    const filteredUsers = computed(() => {
      let filtered = users.value

      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(keyword) ||
          user.email.toLowerCase().includes(keyword)
        )
      }

      if (roleFilter.value) {
        filtered = filtered.filter(user => user.role === roleFilter.value)
      }

      if (statusFilter.value) {
        filtered = filtered.filter(user => user.status === statusFilter.value)
      }

      return filtered
    })

    // 方法
    const loadUsers = async () => {
      try {
        loading.value = true
        
        // 模拟加载数据
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        users.value = [
          {
            id: 1,
            username: 'admin',
            email: 'admin@example.com',
            role: 'admin',
            status: 'active',
            avatar: '',
            last_login: new Date('2024-01-15T10:30:00'),
            created_at: new Date('2023-01-01T00:00:00'),
            login_count: 156,
            commits_count: 234,
            merge_requests_count: 45,
            active_days: 89,
            lines_of_code: 12450
          },
          {
            id: 2,
            username: 'developer1',
            email: 'dev1@example.com',
            role: 'developer',
            status: 'active',
            avatar: '',
            last_login: new Date('2024-01-15T09:15:00'),
            created_at: new Date('2023-03-15T00:00:00'),
            login_count: 89,
            commits_count: 567,
            merge_requests_count: 78,
            active_days: 67,
            lines_of_code: 23450
          },
          {
            id: 3,
            username: 'viewer1',
            email: 'viewer1@example.com',
            role: 'viewer',
            status: 'active',
            avatar: '',
            last_login: new Date('2024-01-14T16:45:00'),
            created_at: new Date('2023-06-01T00:00:00'),
            login_count: 34,
            commits_count: 0,
            merge_requests_count: 0,
            active_days: 23,
            lines_of_code: 0
          },
          {
            id: 4,
            username: 'developer2',
            email: 'dev2@example.com',
            role: 'developer',
            status: 'disabled',
            avatar: '',
            last_login: new Date('2024-01-10T14:20:00'),
            created_at: new Date('2023-08-20T00:00:00'),
            login_count: 67,
            commits_count: 123,
            merge_requests_count: 23,
            active_days: 45,
            lines_of_code: 8900
          },
          {
            id: 5,
            username: 'newuser',
            email: 'newuser@example.com',
            role: 'developer',
            status: 'pending',
            avatar: '',
            last_login: null,
            created_at: new Date('2024-01-15T00:00:00'),
            login_count: 0,
            commits_count: 0,
            merge_requests_count: 0,
            active_days: 0,
            lines_of_code: 0
          }
        ]
        
        pagination.total = users.value.length
        
      } catch (error) {
        ElMessage.error('加载用户列表失败')
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      userStats.value = [
        {
          title: '总用户数',
          value: '45',
          change: '+5',
          changeType: 'positive',
          changeIcon: 'el-icon-arrow-up',
          icon: 'el-icon-user',
          color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
          title: '活跃用户',
          value: '38',
          change: '+3',
          changeType: 'positive',
          changeIcon: 'el-icon-arrow-up',
          icon: 'el-icon-success',
          color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
        },
        {
          title: '新增用户',
          value: '5',
          change: '+2',
          changeType: 'positive',
          changeIcon: 'el-icon-arrow-up',
          icon: 'el-icon-plus',
          color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
        },
        {
          title: '禁用用户',
          value: '2',
          change: '-1',
          changeType: 'positive',
          changeIcon: 'el-icon-arrow-down',
          icon: 'el-icon-warning',
          color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
        }
      ]
    }

    const handleSearch = () => {
      // 搜索逻辑已在计算属性中处理
    }

    const showAddDialog = () => {
      dialogMode.value = 'add'
      dialogVisible.value = true
    }

    const editUser = (user) => {
      dialogMode.value = 'edit'
      form.id = user.id
      form.username = user.username
      form.email = user.email
      form.role = user.role
      form.status = user.status
      form.remark = user.remark || ''
      dialogVisible.value = true
    }

    const viewUser = (user) => {
      selectedUser.value = user
      detailDialogVisible.value = true
    }

    const resetForm = () => {
      form.id = null
      form.username = ''
      form.email = ''
      form.password = ''
      form.confirmPassword = ''
      form.role = 'developer'
      form.status = 'active'
      form.remark = ''
      formRef.value?.resetFields()
    }

    const submitForm = async () => {
      try {
        await formRef.value.validate()
        submitting.value = true
        
        // 模拟提交
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        if (dialogMode.value === 'add') {
          ElMessage.success('用户添加成功')
        } else {
          ElMessage.success('用户更新成功')
        }
        
        dialogVisible.value = false
        loadUsers()
        
      } catch (error) {
        console.error('表单验证失败:', error)
      } finally {
        submitting.value = false
      }
    }

    const toggleUserStatus = async (user) => {
      try {
        const action = user.status === 'active' ? '禁用' : '启用'
        await ElMessageBox.confirm(
          `确定要${action}用户 "${user.username}" 吗？`,
          `确认${action}`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 模拟状态切换
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        user.status = user.status === 'active' ? 'disabled' : 'active'
        ElMessage.success(`用户${action}成功`)
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('操作失败')
        }
      }
    }

    const deleteUser = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 模拟删除
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('用户删除成功')
        loadUsers()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }

    const handleUserAction = (command, user) => {
      switch (command) {
        case 'resetPassword':
          ElMessage.info(`重置密码: ${user.username}`)
          break
        case 'permissions':
          ElMessage.info(`权限设置: ${user.username}`)
          break
        case 'enable':
        case 'disable':
          toggleUserStatus(user)
          break
        case 'delete':
          deleteUser(user)
          break
      }
    }

    const exportUsers = () => {
      ElMessage.success('导出功能开发中...')
    }

    const importUsers = () => {
      ElMessage.success('导入功能开发中...')
    }

    const handleSizeChange = (size) => {
      pagination.size = size
      loadUsers()
    }

    const handlePageChange = (page) => {
      pagination.page = page
      loadUsers()
    }

    const getRoleType = (role) => {
      const roleMap = {
        admin: 'danger',
        developer: 'primary',
        viewer: 'info'
      }
      return roleMap[role] || 'info'
    }

    const getRoleText = (role) => {
      const roleMap = {
        admin: '管理员',
        developer: '开发者',
        viewer: '观察者'
      }
      return roleMap[role] || role
    }

    const getStatusType = (status) => {
      const statusMap = {
        active: 'success',
        disabled: 'danger',
        pending: 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        active: '活跃',
        disabled: '禁用',
        pending: '待激活'
      }
      return statusMap[status] || status
    }

    const getUserPermissions = (role) => {
      const permissionMap = {
        admin: ['系统管理', '用户管理', '仓库管理', '数据分析', '系统设置'],
        developer: ['仓库管理', '数据分析', '代码提交', '合并请求'],
        viewer: ['数据查看', '报表查看']
      }
      return permissionMap[role] || []
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    // 生命周期
    onMounted(() => {
      loadUsers()
      loadStats()
    })

    return {
      loading,
      submitting,
      searchKeyword,
      roleFilter,
      statusFilter,
      viewMode,
      dialogVisible,
      detailDialogVisible,
      dialogMode,
      formRef,
      selectedUser,
      users,
      userStats,
      pagination,
      form,
      formRules,
      filteredUsers,
      handleSearch,
      showAddDialog,
      editUser,
      viewUser,
      resetForm,
      submitForm,
      toggleUserStatus,
      deleteUser,
      handleUserAction,
      exportUsers,
      importUsers,
      handleSizeChange,
      handlePageChange,
      getRoleType,
      getRoleText,
      getStatusType,
      getStatusText,
      getUserPermissions,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.users {
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

.action-card {
  margin-bottom: 24px;
  
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .search-section {
      display: flex;
      align-items: center;
    }
    
    .action-buttons {
      display: flex;
      gap: 12px;
    }
  }
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    
    i {
      font-size: 24px;
      color: #fff;
    }
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: $text-color;
      margin-bottom: 4px;
    }
    
    .stat-title {
      font-size: 14px;
      color: $text-color-secondary;
      margin-bottom: 8px;
    }
    
    .stat-change {
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 4px;
      
      &.positive {
        color: $success-color;
      }
      
      &.negative {
        color: $danger-color;
      }
      
      &.neutral {
        color: $text-color-secondary;
      }
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
    }
  }
  
  .warning {
    color: $warning-color;
  }
  
  .success {
    color: $success-color;
  }
  
  .danger {
    color: $danger-color;
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.card-view {
  .user-card {
    background: #fff;
    border: 1px solid $border-color-light;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
    
    .user-header {
      display: flex;
      align-items: flex-start;
      margin-bottom: 16px;
      
      .user-avatar {
        position: relative;
        margin-right: 16px;
        
        .status-indicator {
          position: absolute;
          bottom: 0;
          right: 0;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          border: 2px solid #fff;
          
          &.active {
            background-color: $success-color;
          }
          
          &.disabled {
            background-color: $danger-color;
          }
          
          &.pending {
            background-color: $warning-color;
          }
        }
      }
      
      .user-info {
        flex: 1;
        
        .user-name {
          font-size: 18px;
          font-weight: 600;
          color: $text-color;
          margin: 0 0 4px 0;
        }
        
        .user-email {
          font-size: 14px;
          color: $text-color-secondary;
          margin: 0 0 8px 0;
        }
        
        .user-badges {
          display: flex;
          gap: 8px;
        }
      }
    }
    
    .user-stats {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
      padding: 12px;
      background: $bg-color-light;
      border-radius: 8px;
      
      .stat-item {
        text-align: center;
        
        .stat-label {
          display: block;
          font-size: 12px;
          color: $text-color-secondary;
          margin-bottom: 4px;
        }
        
        .stat-value {
          font-size: 16px;
          font-weight: 600;
          color: $text-color;
        }
      }
    }
    
    .user-meta {
      margin-bottom: 16px;
      
      .meta-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 14px;
        color: $text-color-secondary;
        
        i {
          color: $primary-color;
        }
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
    
    .user-actions {
      display: flex;
      gap: 8px;
      
      .el-button {
        flex: 1;
      }
    }
  }
}

.user-detail {
  .detail-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .detail-info {
      margin-left: 20px;
      
      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        color: $text-color;
      }
      
      p {
        margin: 0 0 12px 0;
        color: $text-color-secondary;
      }
      
      .detail-badges {
        display: flex;
        gap: 8px;
      }
    }
  }
  
  .detail-section {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: 16px;
    }
    
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
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
}

@include respond-to('mobile') {
  .users {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 16px;
    
    .page-title {
      font-size: 24px;
    }
  }
  
  .action-card {
    .action-bar {
      flex-direction: column;
      gap: 16px;
      
      .search-section {
        width: 100%;
        flex-wrap: wrap;
        gap: 8px;
        
        .el-input {
          width: 100% !important;
        }
        
        .el-select {
          width: calc(50% - 4px) !important;
        }
      }
      
      .action-buttons {
        width: 100%;
        justify-content: space-between;
      }
    }
  }
  
  .stats-row {
    margin-bottom: 16px;
  }
  
  .stat-card {
    padding: 16px;
    margin-bottom: 12px;
    
    .stat-content {
      .stat-value {
        font-size: 24px;
      }
    }
  }
  
  .card-view {
    .user-card {
      padding: 16px;
      
      .user-actions {
        flex-direction: column;
      }
    }
  }
  
  .user-detail {
    .detail-header {
      flex-direction: column;
      text-align: center;
      
      .detail-info {
        margin-left: 0;
        margin-top: 16px;
      }
    }
  }
}
</style>