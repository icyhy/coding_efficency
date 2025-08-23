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
          <el-button type="primary" @click="yunxiaoDialogVisible = true">
            <i class="el-icon-search"></i>
            查询仓库
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
        <el-table-column prop="is_tracked" label="统计状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_tracked ? 'success' : 'info'" size="small">
              {{ row.is_tracked ? '已纳入' : '未纳入' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewRepository(row)">
              查看
            </el-button>
            <el-button type="text" size="small" @click="syncRepository(row)" :loading="row.syncing">
              同步
            </el-button>
            <el-button 
              v-if="!row.is_tracked" 
              type="text" 
              size="small" 
              @click="addToTracking(row)"
              :loading="row.tracking"
              style="color: #67C23A;"
            >
              加入统计
            </el-button>
            <el-button 
              v-else 
              type="text" 
              size="small" 
              @click="removeFromTracking(row)"
              :loading="row.tracking"
              style="color: #F56C6C;"
            >
              移出统计
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
                    <el-tag :type="repo.is_tracked ? 'success' : 'info'" size="mini" style="margin-left: 8px;">
                      {{ repo.is_tracked ? '已纳入统计' : '未纳入统计' }}
                    </el-tag>
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
                <el-button 
                  v-if="!repo.is_tracked" 
                  size="small" 
                  type="success" 
                  @click="addToTracking(repo)"
                  :loading="repo.tracking"
                >
                  加入统计
                </el-button>
                <el-button 
                  v-else 
                  size="small" 
                  type="danger" 
                  @click="removeFromTracking(repo)"
                  :loading="repo.tracking"
                >
                  移出统计
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
          <div class="repository-name-input">
            <el-input 
              v-model="form.name" 
              placeholder="请输入仓库名称（支持搜索云效仓库）"
              @input="handleNameInput"
              @blur="hideCandidates"
              @focus="() => form.name && searchCandidateRepositories(form.name)"
            >
              <template #suffix>
                <el-icon v-if="searchingCandidates" class="is-loading">
                  <Loading />
                </el-icon>
              </template>
            </el-input>
            
            <!-- 候选仓库列表 -->
            <div v-if="showCandidates" class="candidate-repositories">
              <div class="candidate-header">
                <span>云效仓库候选列表</span>
                <span class="candidate-count">{{ candidateRepositories.length }} 个结果</span>
              </div>
              <div class="candidate-list">
                <div 
                  v-for="repo in candidateRepositories" 
                  :key="repo.id"
                  class="candidate-item"
                  @click="selectCandidateRepository(repo)"
                >
                  <div class="candidate-info">
                    <div class="candidate-name">{{ repo.name }}</div>
                    <div class="candidate-path">{{ repo.full_name }}</div>
                    <div v-if="repo.description" class="candidate-desc">{{ repo.description }}</div>
                  </div>
                  <div class="candidate-meta">
                    <el-tag :type="repo.visibility === 'public' ? 'success' : 'info'" size="small">
                      {{ repo.visibility === 'public' ? '公开' : '私有' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
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

    <!-- 云效仓库列表对话框 -->
    <el-dialog
      v-model="yunxiaoDialogVisible"
      title="查询云效仓库"
      width="900px"
      @close="resetYunxiaoDialog"
    >
      <div class="yunxiao-repos-container">
        <!-- 搜索和操作栏 -->
        <div class="yunxiao-header">
          <div class="search-section">
            <el-input
              v-model="yunxiaoSearchKeyword"
              placeholder="请输入仓库名称进行查询"
              style="width: 300px; margin-right: 16px;"
              @keyup.enter="searchYunxiaoRepos"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button 
              type="primary" 
              @click="searchYunxiaoRepos"
              :loading="loadingYunxiao"
            >
              搜索
            </el-button>
          </div>
          <div class="action-section">
            <span class="repo-count">共 {{ yunxiaoPagination.total }} 个仓库</span>
            <el-button 
              type="primary" 
              size="small" 
              @click="addSelectedToTracking"
              :disabled="selectedYunxiaoRepos.length === 0"
            >
              加入统计 ({{ selectedYunxiaoRepos.length }})
            </el-button>
          </div>
        </div>
        
        <el-table
          :data="yunxiaoRepositories"
          v-loading="loadingYunxiao"
          @selection-change="handleYunxiaoSelection"
          max-height="400"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="仓库名称" min-width="150">
            <template #default="{ row }">
              <div class="repo-info">
                <div class="repo-name">{{ row.name }}</div>
                <div class="repo-path">{{ row.full_name || row.pathWithNamespace }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="last_activity" label="最后活动" width="120">
            <template #default="{ row }">
              {{ formatDate(row.last_activity || row.lastActivityAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="addSingleToTracking(row)"
              >
                加入统计
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <div class="yunxiao-pagination">
          <el-pagination
            v-model:current-page="yunxiaoPagination.page"
            v-model:page-size="yunxiaoPagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="yunxiaoPagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleYunxiaoSizeChange"
            @current-change="handleYunxiaoPageChange"
          />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="yunxiaoDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Search } from '@element-plus/icons-vue'
import { getRepositories, addRepository, updateRepository, deleteRepository as deleteRepositoryAPI, syncRepository as syncRepositoryAPI, getYunxiaoRepositoriesAPI, addToTrackingAPI, removeFromTrackingAPI, searchYunxiaoRepositories, addYunxiaoRepository } from '@/api/repositories'

export default {
  name: 'Repositories',
  components: {
    Loading,
    Search
  },
  setup() {
    const store = useStore()

    // 响应式数据
    const loading = ref(false)
    const syncing = ref(false)
    const submitting = ref(false)
    const loadingYunxiao = ref(false)
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

    // 候选仓库相关数据
    const candidateRepositories = ref([])
    const searchingCandidates = ref(false)
    const showCandidates = ref(false)

    // 云效仓库对话框相关数据
    const yunxiaoDialogVisible = ref(false)
    const yunxiaoRepositories = ref([])
    const selectedYunxiaoRepos = ref([])
    const yunxiaoSearchKeyword = ref('')
    const yunxiaoPagination = reactive({
      page: 1,
      size: 20,
      total: 0
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
            is_tracked: repo.is_tracked || false, // 是否纳入统计
            last_sync: repo.last_sync_at ? new Date(repo.last_sync_at) : null,
            commits_count: repo.stats?.commits_count || 0,
            branches_count: 0, // API暂不提供分支数
            contributors_count: 0, // API暂不提供贡献者数
            syncing: repo.sync_status === 'syncing',
            tracking: false // 加入/移出统计操作的loading状态
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
      // 重置候选仓库相关状态
      candidateRepositories.value = []
      showCandidates.value = false
    }

    // 搜索候选仓库
    const searchCandidateRepositories = async (query) => {
      if (!query || query.length < 2) {
        candidateRepositories.value = []
        showCandidates.value = false
        return
      }

      try {
        searchingCandidates.value = true
        const response = await searchYunxiaoRepositories({
          search: query,
          page: 1,
          per_page: 10
        })
        
        if (response.data && response.data.success) {
          candidateRepositories.value = response.data.data.repositories || []
          showCandidates.value = candidateRepositories.value.length > 0
        } else {
          candidateRepositories.value = []
          showCandidates.value = false
        }
      } catch (error) {
        console.error('搜索候选仓库失败:', error)
        candidateRepositories.value = []
        showCandidates.value = false
        // 不显示错误消息，避免干扰用户输入体验
      } finally {
        searchingCandidates.value = false
      }
    }

    // 选择候选仓库
    const selectCandidateRepository = (repo) => {
      form.name = repo.name
      form.url = repo.clone_url || repo.url
      form.description = repo.description
      showCandidates.value = false
      candidateRepositories.value = []
    }

    // 处理仓库名称输入
    const handleNameInput = (value) => {
      form.name = value
      // 防抖搜索
      clearTimeout(handleNameInput.timer)
      handleNameInput.timer = setTimeout(() => {
        searchCandidateRepositories(value)
      }, 300)
    }

    // 隐藏候选列表
    const hideCandidates = () => {
      setTimeout(() => {
        showCandidates.value = false
      }, 200) // 延迟隐藏，允许点击候选项
    }

    // 云效仓库对话框相关方法
    const resetYunxiaoDialog = () => {
      yunxiaoRepositories.value = []
      selectedYunxiaoRepos.value = []
      yunxiaoSearchKeyword.value = ''
      yunxiaoPagination.page = 1
      yunxiaoPagination.total = 0
    }

    const handleYunxiaoSelection = (selection) => {
      selectedYunxiaoRepos.value = selection
    }

    const addSingleToTracking = async (repo) => {
      try {
        const targetUrl = repo.clone_url || repo.url
        let targetRepoId = null

        // 优先在本地列表中查找
        const local = repositories.value.find(r => r.url === targetUrl)
        if (local) {
          targetRepoId = local.id
        }

        // 若未找到，调用后端检索
        if (!targetRepoId) {
          try {
            const res = await getRepositories({ search: targetUrl, page: 1, per_page: 1 })
            if (res && res.success && res.data?.items?.length) {
              targetRepoId = res.data.items[0].id
            }
          } catch (error) {
            console.warn('查询仓库失败，可能是认证问题，直接尝试创建:', error.message)
            // 忽略查询错误，继续尝试创建
          }
        }

        // 若仍未找到，则创建后获取ID
        if (!targetRepoId) {
          // 确保必需字段不为空
          const cloneUrl = repo.clone_url || repo.url || ''
          if (!cloneUrl) {
            throw new Error('仓库缺少克隆地址，无法添加')
          }
          
          try {
            const createResp = await addYunxiaoRepository({
              repository_id: repo.id,
              name: repo.name || '未命名仓库',
              clone_url: cloneUrl,
              web_url: repo.url || cloneUrl,
              description: repo.description || ''
            })
            if (createResp && createResp.success) {
              targetRepoId = createResp.data?.id
            }
          } catch (createError) {
            // 如果是409冲突错误，说明仓库已存在，尝试重新查询
            if (createError.response?.status === 409) {
              console.log('仓库已存在，重新查询仓库ID')
              try {
                const retry = await getRepositories({ search: targetUrl, page: 1, per_page: 1 })
                if (retry && retry.success && retry.data?.items?.length) {
                  targetRepoId = retry.data.items[0].id
                }
              } catch (retryError) {
                console.warn('重试查询仓库失败:', retryError.message)
              }
            } else {
              throw createError
            }
          }
        }

        if (!targetRepoId) {
          throw new Error('未找到仓库ID，无法加入统计')
        }

        const trackResp = await addToTrackingAPI(targetRepoId)
        if (trackResp && trackResp.success) {
          ElMessage.success(`仓库 ${repo.name} 已加入统计`)
          loadRepositories()
        } else {
          throw new Error(trackResp?.message || '加入统计失败')
        }
      } catch (error) {
        console.error('加入统计失败:', error)
        ElMessage.error(`仓库 ${repo.name} 加入统计失败: ${error.message || '请重试'}`)
      }
    }

    const addSelectedToTracking = async () => {
      if (selectedYunxiaoRepos.value.length === 0) {
        ElMessage.warning('请先选择要加入统计的仓库')
        return
      }

      try {
        const results = await Promise.all(selectedYunxiaoRepos.value.map(async (repo) => {
          try {
            const targetUrl = repo.clone_url || repo.url
            let repoId = null

            // 本地列表匹配
            const local = repositories.value.find(r => r.url === targetUrl)
            if (local) repoId = local.id

            // 后端检索
            if (!repoId) {
              try {
                const res = await getRepositories({ search: targetUrl, page: 1, per_page: 1 })
                if (res && res.success && res.data?.items?.length) {
                  repoId = res.data.items[0].id
                }
              } catch (error) {
                console.warn('查询仓库失败，可能是认证问题，直接尝试创建:', error.message)
                // 忽略查询错误，继续尝试创建
              }
            }

            // 若仍未找到，则创建后获取ID
            if (!repoId) {
              // 确保必需字段不为空
              const cloneUrl = repo.clone_url || repo.url || ''
              if (!cloneUrl) {
                throw new Error('仓库缺少克隆地址，无法添加')
              }
              
              try {
                const createResp = await addYunxiaoRepository({
                  repository_id: repo.id,
                  name: repo.name || '未命名仓库',
                  clone_url: cloneUrl,
                  web_url: repo.url || cloneUrl,
                  description: repo.description || ''
                })
                if (createResp && createResp.success) {
                  repoId = createResp.data?.id
                }
              } catch (createError) {
                // 如果是409冲突错误，说明仓库已存在，尝试重新查询
                if (createError.response?.status === 409) {
                  console.log('仓库已存在，重新查询仓库ID')
                  try {
                    const retry = await getRepositories({ search: targetUrl, page: 1, per_page: 1 })
                    if (retry && retry.success && retry.data?.items?.length) {
                      repoId = retry.data.items[0].id
                    }
                  } catch (retryError) {
                    console.warn('重试查询仓库失败:', retryError.message)
                  }
                } else {
                  throw createError
                }
              }
            }

            if (!repoId) throw new Error('未找到仓库ID')
            const trackResp = await addToTrackingAPI(repoId)
            if (!(trackResp && trackResp.success)) throw new Error(trackResp?.message || '加入统计失败')
            return true
          } catch (e) {
            return false
          }
        }))

        const successCount = results.filter(Boolean).length
        const failCount = results.length - successCount
        if (successCount > 0) {
          ElMessage.success(`成功加入 ${successCount} 个仓库到统计${failCount > 0 ? `，${failCount} 个失败` : ''}`)
          loadRepositories()
          yunxiaoDialogVisible.value = false
        } else {
          ElMessage.error('所有仓库加入统计失败')
        }
      } catch (error) {
        console.error('批量加入统计失败:', error)
        ElMessage.error('批量加入统计失败，请重试')
      }
    }

    // 云效仓库搜索处理
    const handleYunxiaoSearch = () => {
      // 防抖处理，避免频繁请求
      clearTimeout(handleYunxiaoSearch.timer)
      handleYunxiaoSearch.timer = setTimeout(() => {
        searchYunxiaoRepos()
      }, 500)
    }

    // 搜索云效仓库
    const searchYunxiaoRepos = () => {
      yunxiaoPagination.page = 1 // 重置到第一页
      getYunxiaoRepositories()
    }

    // 云效仓库分页大小变化
    const handleYunxiaoSizeChange = (size) => {
      yunxiaoPagination.size = size
      yunxiaoPagination.page = 1 // 重置到第一页
      getYunxiaoRepositories()
    }

    // 云效仓库页码变化
    const handleYunxiaoPageChange = (page) => {
      yunxiaoPagination.page = page
      getYunxiaoRepositories()
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

    // 搜索云效仓库
    const getYunxiaoRepositories = async () => {
      try {
        // 检查搜索关键词是否为空
        if (!yunxiaoSearchKeyword.value || yunxiaoSearchKeyword.value.trim() === '') {
          ElMessage.warning('请输入仓库名称进行查询')
          return
        }
        
        loadingYunxiao.value = true
        
        const response = await getYunxiaoRepositoriesAPI({
          page: yunxiaoPagination.page,
          per_page: yunxiaoPagination.size,
          search: yunxiaoSearchKeyword.value.trim()
        })
        
        if (response && response.success) {
          const yunxiaoRepos = response.data.items || []  // 使用items字段
          yunxiaoPagination.total = response.data.pagination?.total || 0
          
          if (yunxiaoRepos.length === 0) {
            ElMessage.info('未找到匹配的仓库，请尝试其他关键词')
          } else {
            ElMessage.success(`找到 ${yunxiaoRepos.length} 个匹配的仓库`)
          }
          
          // 更新仓库列表
          yunxiaoRepositories.value = yunxiaoRepos
          console.log('云效仓库搜索结果:', yunxiaoRepos)
        } else {
          throw new Error(response?.message || '搜索云效仓库失败')
        }
        
      } catch (error) {
        console.error('搜索云效仓库失败:', error)
        ElMessage.error(`搜索云效仓库失败: ${error.message || '请重试'}`)
      } finally {
        loadingYunxiao.value = false
      }
    }

    // 加入统计
    const addToTracking = async (repo) => {
      try {
        repo.tracking = true
        const response = await addToTrackingAPI(repo.id)
        if (response && response.success) {
          repo.is_tracked = true
          ElMessage.success(`仓库 ${repo.name} 已加入统计`)
          loadRepositories()
        } else {
          throw new Error(response?.message || '加入统计失败')
        }
      } catch (error) {
        console.error('加入统计失败:', error)
        ElMessage.error(`仓库 ${repo.name} 加入统计失败: ${error.message || '请重试'}`)
      } finally {
        repo.tracking = false
      }
    }

    // 移出统计
    const removeFromTracking = async (repo) => {
      try {
        repo.tracking = true
        const response = await removeFromTrackingAPI(repo.id)
        if (response && response.success) {
          repo.is_tracked = false
          ElMessage.success(`仓库 ${repo.name} 已移出统计`)
          loadRepositories()
        } else {
          throw new Error(response?.message || '移出统计失败')
        }
      } catch (error) {
        console.error('移出统计失败:', error)
        ElMessage.error(`仓库 ${repo.name} 移出统计失败: ${error.message || '请重试'}`)
      } finally {
        repo.tracking = false
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
      loadingYunxiao,
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
      candidateRepositories,
      searchingCandidates,
      showCandidates,
      handleSearch,
      showAddDialog,
      editRepository,
      resetForm,
      submitForm,
      syncRepository,
      getYunxiaoRepositories,
      addToTracking,
      removeFromTracking,
      deleteRepository,
      viewRepository,
      handleRepoAction,
      exportRepositories,
      handleSizeChange,
      handlePageChange,
      getStatusType,
      getStatusText,
      formatDate,
      updateStats,
      searchCandidateRepositories,
      selectCandidateRepository,
      handleNameInput,
      hideCandidates,
      // 云效仓库对话框相关
      yunxiaoDialogVisible,
      yunxiaoRepositories,
      selectedYunxiaoRepos,
      yunxiaoSearchKeyword,
      yunxiaoPagination,
      resetYunxiaoDialog,
      handleYunxiaoSelection,
      addSingleToTracking,
      addSelectedToTracking,
      handleYunxiaoSearch,
      searchYunxiaoRepos,
      handleYunxiaoSizeChange,
      handleYunxiaoPageChange
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

/* 候选仓库相关样式 */
.repository-name-input {
  position: relative;
}

.candidate-repositories {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.candidate-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.candidate-count {
  font-weight: 500;
}

.candidate-list {
  max-height: 250px;
  overflow-y: auto;
}

.candidate-item {
  padding: 12px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: background-color 0.2s;
}

.candidate-item:hover {
  background-color: #f5f7fa;
}

.candidate-item:last-child {
  border-bottom: none;
}

.candidate-info {
  flex: 1;
  min-width: 0;
}

.candidate-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.candidate-path {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
  word-break: break-all;
}

.candidate-desc {
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.candidate-meta {
  margin-left: 12px;
  flex-shrink: 0;
}

/* 云效仓库对话框样式 */
.yunxiao-repos-container {
  .yunxiao-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;
    
    span {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
  }
  
  .repo-info {
    .repo-name {
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
    }
    
    .repo-path {
      font-size: 12px;
      color: #909399;
    }
  }
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