<template>
  <div class="repositories">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">仓库管理</h1>
      <p class="page-subtitle">管理和监控代码仓库</p>
    </div>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索仓库名称或描述"
            prefix-icon="el-icon-search"
            clearable
            @input="handleSearch"
            style="width: 300px;"
          />
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px; margin-left: 12px;">
            <el-option label="活跃" value="active" />
            <el-option label="同步中" value="syncing" />
            <el-option label="错误" value="error" />
            <el-option label="暂停" value="paused" />
          </el-select>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="showAddDialog">
            <i class="el-icon-plus"></i>
            添加仓库
          </el-button>
          <el-button @click="syncAllRepositories" :loading="syncing">
            <i class="el-icon-refresh"></i>
            同步所有
          </el-button>
          <el-button @click="exportRepositories">
            <i class="el-icon-download"></i>
            导出
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 仓库统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in repoStats" :key="index">
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

    <!-- 仓库列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">仓库列表</span>
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
        :data="filteredRepositories"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="仓库名称" min-width="200">
          <template #default="{ row }">
            <div class="repo-name">
              <i class="el-icon-folder-opened"></i>
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_private" type="warning" size="mini">私有</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="url" label="仓库地址" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link :href="row.url" target="_blank" type="primary">
              {{ row.url }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_sync" label="最后同步" width="180">
          <template #default="{ row }">
            {{ row.last_sync ? formatDate(row.last_sync) : '从未同步' }}
          </template>
        </el-table-column>
        <el-table-column prop="commits_count" label="提交数" width="100" align="right" />
        <el-table-column prop="branches_count" label="分支数" width="100" align="right" />
        <el-table-column prop="contributors_count" label="贡献者" width="100" align="right" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewRepository(row)">
              查看
            </el-button>
            <el-button type="text" size="small" @click="syncRepository(row)" :loading="row.syncing">
              同步
            </el-button>
            <el-button type="text" size="small" @click="editRepository(row)">
              编辑
            </el-button>
            <el-button type="text" size="small" @click="deleteRepository(row)" class="danger">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :lg="8" v-for="repo in filteredRepositories" :key="repo.id">
            <div class="repo-card">
              <div class="repo-header">
                <div class="repo-info">
                  <h3 class="repo-title">
                    <i class="el-icon-folder-opened"></i>
                    {{ repo.name }}
                    <el-tag v-if="repo.is_private" type="warning" size="mini">私有</el-tag>
                  </h3>
                  <p class="repo-description">{{ repo.description || '暂无描述' }}</p>
                </div>
                <el-tag :type="getStatusType(repo.status)" size="small">
                  {{ getStatusText(repo.status) }}
                </el-tag>
              </div>
              
              <div class="repo-stats">
                <div class="stat-item">
                  <span class="stat-label">提交数</span>
                  <span class="stat-value">{{ repo.commits_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">分支数</span>
                  <span class="stat-value">{{ repo.branches_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">贡献者</span>
                  <span class="stat-value">{{ repo.contributors_count }}</span>
                </div>
              </div>
              
              <div class="repo-meta">
                <div class="meta-item">
                  <i class="el-icon-time"></i>
                  <span>最后同步: {{ repo.last_sync ? formatDate(repo.last_sync) : '从未同步' }}</span>
                </div>
                <div class="meta-item">
                  <i class="el-icon-link"></i>
                  <el-link :href="repo.url" target="_blank" type="primary" :underline="false">
                    查看仓库
                  </el-link>
                </div>
              </div>
              
              <div class="repo-actions">
                <el-button size="small" @click="viewRepository(repo)">
                  查看详情
                </el-button>
                <el-button size="small" @click="syncRepository(repo)" :loading="repo.syncing">
                  同步数据
                </el-button>
                <el-dropdown @command="(command) => handleRepoAction(command, repo)">
                  <el-button size="small">
                    更多<i class="el-icon-arrow-down el-icon--right"></i>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">编辑仓库</el-dropdown-item>
                      <el-dropdown-item command="settings">仓库设置</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除仓库</el-dropdown-item>
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

    <!-- 添加/编辑仓库对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加仓库' : '编辑仓库'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库地址" prop="url">
          <el-input v-model="form.url" placeholder="请输入Git仓库地址" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入仓库描述（可选）"
          />
        </el-form-item>
        <el-form-item label="访问令牌" prop="access_token">
          <el-input
            v-model="form.access_token"
            type="password"
            placeholder="请输入访问令牌（私有仓库必填）"
            show-password
          />
        </el-form-item>
        <el-form-item label="同步设置">
          <el-checkbox v-model="form.auto_sync">启用自动同步</el-checkbox>
          <div v-if="form.auto_sync" style="margin-top: 8px;">
            <el-select v-model="form.sync_interval" placeholder="同步频率">
              <el-option label="每小时" value="hourly" />
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
            </el-select>
          </div>
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRepositories, addRepository, updateRepository, deleteRepository as deleteRepositoryAPI, syncRepository as syncRepositoryAPI } from '@/api/repositories'

export default {
  name: 'Repositories',
  setup() {
    const store = useStore()

    // 响应式数据
    const loading = ref(false)
    const syncing = ref(false)
    const submitting = ref(false)
    const searchKeyword = ref('')
    const statusFilter = ref('')
    const viewMode = ref('table')
    const dialogVisible = ref(false)
    const dialogMode = ref('add')
    const formRef = ref(null)

    const repositories = ref([])
    const repoStats = ref([])

    const pagination = reactive({
      page: 1,
      size: 12,
      total: 0
    })

    const form = reactive({
      id: null,
      name: '',
      url: '',
      description: '',
      access_token: '',
      auto_sync: false,
      sync_interval: 'daily'
    })

    const formRules = {
      name: [
        { required: true, message: '请输入仓库名称', trigger: 'blur' }
      ],
      url: [
        { required: true, message: '请输入仓库地址', trigger: 'blur' },
        { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
      ]
    }

    // 计算属性
    const filteredRepositories = computed(() => {
      let filtered = repositories.value

      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(repo => 
          repo.name.toLowerCase().includes(keyword) ||
          (repo.description && repo.description.toLowerCase().includes(keyword))
        )
      }

      if (statusFilter.value) {
        filtered = filtered.filter(repo => repo.status === statusFilter.value)
      }

      return filtered
    })

    // 方法
    const loadRepositories = async () => {
      try {
        loading.value = true
        
        // 调用真实API获取仓库列表
        const params = {
          page: pagination.page,
          per_page: pagination.size,
          search: searchKeyword.value,
          is_active: statusFilter.value === 'active' ? true : undefined
        }
        
        const response = await getRepositories(params)
        
        if (response.data && response.data.success) {
          repositories.value = response.data.data.items.map(repo => ({
            id: repo.id,
            name: repo.name,
            description: repo.description || '',
            url: repo.url,
            status: repo.is_active ? 'active' : 'paused',
            is_private: repo.platform === 'yunxiao', // 阿里云效仓库默认为私有
            last_sync: repo.last_sync_at ? new Date(repo.last_sync_at) : null,
            commits_count: repo.stats?.commits_count || 0,
            branches_count: 0, // API暂不提供分支数
            contributors_count: 0, // API暂不提供贡献者数
            syncing: repo.sync_status === 'syncing'
          }))
          
          pagination.total = response.data.data.total
          
          // 更新统计数据
          updateStats()
        } else {
          repositories.value = []
          pagination.total = 0
          updateStats()
        }
        
      } catch (error) {
        console.error('加载仓库列表失败:', error)
        ElMessage.error('加载仓库列表失败，请检查网络连接')
        repositories.value = []
        pagination.total = 0
      } finally {
        loading.value = false
      }
    }

    // 计算统计数据
    const updateStats = () => {
      const stats = {
        total: repositories.value.length,
        active: 0,
        syncing: 0,
        error: 0,
        paused: 0
      }
      
      repositories.value.forEach(repo => {
        if (repo.status === 'active') stats.active++
        else if (repo.status === 'syncing') stats.syncing++
        else if (repo.status === 'error') stats.error++
        else if (repo.status === 'paused') stats.paused++
      })
      
      repoStats.value = [
        {
          title: '总仓库数',
          value: stats.total.toString(),
          change: '+0',
          changeType: 'neutral',
          changeIcon: 'el-icon-minus',
          icon: 'el-icon-folder',
          color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
          title: '活跃仓库',
          value: stats.active.toString(),
          change: '+0',
          changeType: 'neutral',
          changeIcon: 'el-icon-minus',
          icon: 'el-icon-success',
          color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
        },
        {
          title: '同步中',
          value: stats.syncing.toString(),
          change: '无变化',
          changeType: 'neutral',
          changeIcon: 'el-icon-minus',
          icon: 'el-icon-loading',
          color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        },
        {
          title: '错误状态',
          value: stats.error.toString(),
          change: '+0',
          changeType: 'neutral',
          changeIcon: 'el-icon-minus',
          icon: 'el-icon-warning',
          color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
        }
      ]
    }

    const loadStats = async () => {
      // 统计数据已通过updateStats函数更新
      // 这里保持空函数以兼容现有调用
    }

    const handleSearch = () => {
      // 搜索逻辑已在计算属性中处理
    }

    const showAddDialog = () => {
      dialogMode.value = 'add'
      dialogVisible.value = true
    }

    const editRepository = (repo) => {
      dialogMode.value = 'edit'
      form.id = repo.id
      form.name = repo.name
      form.url = repo.url
      form.description = repo.description
      form.access_token = ''
      form.auto_sync = repo.auto_sync || false
      form.sync_interval = repo.sync_interval || 'daily'
      dialogVisible.value = true
    }

    const resetForm = () => {
      form.id = null
      form.name = ''
      form.url = ''
      form.description = ''
      form.access_token = ''
      form.auto_sync = false
      form.sync_interval = 'daily'
      formRef.value?.resetFields()
    }

    const submitForm = async () => {
      try {
        await formRef.value.validate()
        submitting.value = true
        
        const formData = {
          name: form.name,
          url: form.url,
          description: form.description,
          api_key: form.access_token, // 后端API使用api_key字段
          platform: 'yunxiao', // 固定为阿里云效平台
          project_id: form.project_id || '' // 项目ID，可选
        }
        
        let response
        if (dialogMode.value === 'add') {
          response = await addRepository(formData)
          if (response.data && response.data.success) {
            ElMessage.success('仓库添加成功')
          } else {
            throw new Error(response.data?.message || '添加仓库失败')
          }
        } else {
          const updateData = {
            name: form.name,
            api_key: form.access_token,
            is_active: form.is_active !== false
          }
          response = await updateRepository(form.id, updateData)
          if (response.data && response.data.success) {
            ElMessage.success('仓库更新成功')
          } else {
            throw new Error(response.data?.message || '更新仓库失败')
          }
        }
        
        dialogVisible.value = false
        resetForm()
        loadRepositories()
        
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(error.message || '操作失败，请重试')
      } finally {
        submitting.value = false
      }
    }

    const syncRepository = async (repo) => {
      try {
        repo.syncing = true
        
        const response = await syncRepositoryAPI(repo.id)
        
        if (response.data && response.data.success) {
          repo.status = 'active'
          repo.last_sync = new Date()
          ElMessage.success(`仓库 ${repo.name} 同步成功`)
          
          // 重新加载仓库列表以获取最新状态
          loadRepositories()
        } else {
          throw new Error(response.data?.message || '同步失败')
        }
        
      } catch (error) {
        console.error('同步仓库失败:', error)
        ElMessage.error(`仓库 ${repo.name} 同步失败: ${error.message || '请重试'}`)
      } finally {
        repo.syncing = false
      }
    }

    const syncAllRepositories = async () => {
      try {
        syncing.value = true
        
        // 模拟批量同步
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        ElMessage.success('所有仓库同步完成')
        loadRepositories()
        
      } catch (error) {
        ElMessage.error('批量同步失败')
      } finally {
        syncing.value = false
      }
    }

    const deleteRepository = async (repo) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除仓库 "${repo.name}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await deleteRepositoryAPI(repo.id)
        
        if (response.data && response.data.success) {
          ElMessage.success(`仓库 ${repo.name} 删除成功`)
          loadRepositories()
        } else {
          throw new Error(response.data?.message || '删除失败')
        }
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除仓库失败:', error)
          ElMessage.error(`删除仓库 ${repo.name} 失败: ${error.message || '请重试'}`)
        }
      }
    }

    const viewRepository = (repo) => {
      ElMessage.info(`查看仓库详情: ${repo.name}`)
      // 这里可以跳转到仓库详情页面
    }

    const handleRepoAction = (command, repo) => {
      switch (command) {
        case 'edit':
          editRepository(repo)
          break
        case 'settings':
          ElMessage.info(`仓库设置: ${repo.name}`)
          break
        case 'delete':
          deleteRepository(repo)
          break
      }
    }

    const exportRepositories = () => {
      ElMessage.success('导出功能开发中...')
    }

    const handleSizeChange = (size) => {
      pagination.size = size
      loadRepositories()
    }

    const handlePageChange = (page) => {
      pagination.page = page
      loadRepositories()
    }

    const getStatusType = (status) => {
      const statusMap = {
        active: 'success',
        syncing: 'warning',
        error: 'danger',
        paused: 'info'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        active: '活跃',
        syncing: '同步中',
        error: '错误',
        paused: '暂停'
      }
      return statusMap[status] || status
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    // 生命周期
    onMounted(() => {
      loadRepositories()
    })

    return {
      loading,
      syncing,
      submitting,
      searchKeyword,
      statusFilter,
      viewMode,
      dialogVisible,
      dialogMode,
      formRef,
      repositories,
      repoStats,
      pagination,
      form,
      formRules,
      filteredRepositories,
      handleSearch,
      showAddDialog,
      editRepository,
      resetForm,
      submitForm,
      syncRepository,
      syncAllRepositories,
      deleteRepository,
      viewRepository,
      handleRepoAction,
      exportRepositories,
      handleSizeChange,
      handlePageChange,
      getStatusType,
      getStatusText,
      formatDate,
      updateStats
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.repositories {
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
  
  .repo-name {
    display: flex;
    align-items: center;
    gap: 8px;
    
    i {
      color: $primary-color;
    }
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
  .repo-card {
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
    
    .repo-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
      
      .repo-info {
        flex: 1;
        
        .repo-title {
          font-size: 18px;
          font-weight: 600;
          color: $text-color;
          margin: 0 0 8px 0;
          display: flex;
          align-items: center;
          gap: 8px;
          
          i {
            color: $primary-color;
          }
        }
        
        .repo-description {
          font-size: 14px;
          color: $text-color-secondary;
          margin: 0;
          line-height: 1.4;
        }
      }
    }
    
    .repo-stats {
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
    
    .repo-meta {
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
    
    .repo-actions {
      display: flex;
      gap: 8px;
      
      .el-button {
        flex: 1;
      }
    }
  }
}

@include respond-to('mobile') {
  .repositories {
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
        
        .el-input {
          width: 100% !important;
        }
        
        .el-select {
          width: 100px !important;
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
    .repo-card {
      padding: 16px;
      
      .repo-actions {
        flex-direction: column;
      }
    }
  }
}
</style>