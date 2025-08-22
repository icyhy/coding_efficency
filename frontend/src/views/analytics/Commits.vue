<template>
  <div class="commits-analytics">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">提交分析</h1>
      <p class="page-subtitle">代码提交统计与趋势分析</p>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="filters.repository" placeholder="选择仓库" clearable>
            <el-option
              v-for="repo in repositories"
              :key="repo.id"
              :label="repo.name"
              :value="repo.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="作者">
          <el-select v-model="filters.author" placeholder="选择作者" clearable>
            <el-option
              v-for="author in authors"
              :key="author"
              :label="author"
              :value="author"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <i class="el-icon-search"></i>
            查询
          </el-button>
          <el-button @click="resetFilters">
            <i class="el-icon-refresh"></i>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in commitStats" :key="index">
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

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 提交趋势图 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">提交趋势</span>
              <el-radio-group v-model="trendType" size="small">
                <el-radio-button label="daily">按天</el-radio-button>
                <el-radio-button label="weekly">按周</el-radio-button>
                <el-radio-button label="monthly">按月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef" v-loading="loading.trend"></div>
        </el-card>
      </el-col>

      <!-- 作者贡献分布 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">作者贡献分布</span>
            </div>
          </template>
          <div class="chart-container" ref="authorChartRef" v-loading="loading.author"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 提交时间分布 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">提交时间分布</span>
              <el-radio-group v-model="timeDistributionType" size="small">
                <el-radio-button label="hour">小时</el-radio-button>
                <el-radio-button label="weekday">星期</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="timeChartRef" v-loading="loading.time"></div>
        </el-card>
      </el-col>

      <!-- 文件类型分布 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">文件类型分布</span>
            </div>
          </template>
          <div class="chart-container" ref="fileTypeChartRef" v-loading="loading.fileType"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">提交详情</span>
          <el-button type="primary" size="small" @click="exportData">
            <i class="el-icon-download"></i>
            导出数据
          </el-button>
        </div>
      </template>
      <el-table
        :data="commitList"
        v-loading="loading.table"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="hash" label="提交哈希" width="120">
          <template #default="{ row }">
            <el-link type="primary" :underline="false">
              {{ row.hash.substring(0, 8) }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="提交信息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="date" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="additions" label="新增行数" width="100" align="right">
          <template #default="{ row }">
            <span class="text-success">+{{ row.additions }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="deletions" label="删除行数" width="100" align="right">
          <template #default="{ row }">
            <span class="text-danger">-{{ row.deletions }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="files" label="文件数" width="80" align="right" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewCommit(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useStore } from 'vuex'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

export default {
  name: 'CommitsAnalytics',
  setup() {
    const store = useStore()

    // 图表引用
    const trendChartRef = ref(null)
    const authorChartRef = ref(null)
    const timeChartRef = ref(null)
    const fileTypeChartRef = ref(null)

    // 响应式数据
    const loading = reactive({
      trend: false,
      author: false,
      time: false,
      fileType: false,
      table: false
    })

    const filters = reactive({
      dateRange: [],
      repository: '',
      author: ''
    })

    const trendType = ref('daily')
    const timeDistributionType = ref('hour')
    const repositories = ref([])
    const authors = ref([])
    const commitList = ref([])
    const commitStats = ref([])

    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 图表实例
    let trendChart = null
    let authorChart = null
    let timeChart = null
    let fileTypeChart = null

    // 方法
    const initTrendChart = () => {
      if (!trendChartRef.value) return
      
      trendChart = echarts.init(trendChartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', '2024-01-07']
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: '提交数',
          type: 'line',
          smooth: true,
          data: [12, 19, 15, 25, 22, 18, 20],
          itemStyle: {
            color: '#667eea'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(102, 126, 234, 0.3)'
              }, {
                offset: 1, color: 'rgba(102, 126, 234, 0.1)'
              }]
            }
          }
        }]
      }
      trendChart.setOption(option)
    }

    const initAuthorChart = () => {
      if (!authorChartRef.value) return
      
      authorChart = echarts.init(authorChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          bottom: '0%',
          left: 'center'
        },
        series: [{
          name: '提交数',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          data: [
            { value: 35, name: '张三', itemStyle: { color: '#5470c6' } },
            { value: 25, name: '李四', itemStyle: { color: '#91cc75' } },
            { value: 18, name: '王五', itemStyle: { color: '#fac858' } },
            { value: 15, name: '赵六', itemStyle: { color: '#ee6666' } },
            { value: 7, name: '其他', itemStyle: { color: '#73c0de' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      authorChart.setOption(option)
    }

    const initTimeChart = () => {
      if (!timeChartRef.value) return
      
      timeChart = echarts.init(timeChartRef.value)
      updateTimeChart()
    }

    const updateTimeChart = () => {
      if (!timeChart) return
      
      let xAxisData, seriesData
      
      if (timeDistributionType.value === 'hour') {
        xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
        seriesData = [2, 1, 0, 0, 0, 1, 3, 8, 12, 15, 18, 22, 25, 28, 24, 20, 18, 15, 12, 8, 6, 4, 3, 2]
      } else {
        xAxisData = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        seriesData = [85, 92, 88, 95, 90, 45, 35]
      }
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: xAxisData
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: '提交数',
          type: 'bar',
          data: seriesData,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: '#4facfe'
              }, {
                offset: 1, color: '#00f2fe'
              }]
            }
          }
        }]
      }
      timeChart.setOption(option)
    }

    const initFileTypeChart = () => {
      if (!fileTypeChartRef.value) return
      
      fileTypeChart = echarts.init(fileTypeChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '文件类型',
          type: 'pie',
          radius: '70%',
          data: [
            { value: 40, name: '.js', itemStyle: { color: '#f7df1e' } },
            { value: 25, name: '.vue', itemStyle: { color: '#4fc08d' } },
            { value: 15, name: '.css', itemStyle: { color: '#1572b6' } },
            { value: 10, name: '.html', itemStyle: { color: '#e34f26' } },
            { value: 10, name: '其他', itemStyle: { color: '#909399' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      fileTypeChart.setOption(option)
    }

    const loadData = async () => {
      try {
        loading.trend = true
        loading.author = true
        loading.time = true
        loading.fileType = true
        loading.table = true

        // 模拟加载数据
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟统计数据
        commitStats.value = [
          {
            title: '总提交数',
            value: '1,234',
            change: '+12.5%',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-document',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          },
          {
            title: '活跃作者',
            value: '15',
            change: '+2',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-user',
            color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
          },
          {
            title: '平均每日提交',
            value: '8.5',
            change: '+1.2',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-time',
            color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
          },
          {
            title: '代码行数变化',
            value: '+15.2K',
            change: '+8.5%',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-data-line',
            color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
          }
        ]
        
        // 模拟提交列表数据
        commitList.value = [
          {
            hash: 'a1b2c3d4e5f6g7h8',
            message: 'feat: 添加用户认证功能',
            author: '张三',
            date: new Date('2024-01-15T10:30:00'),
            additions: 125,
            deletions: 23,
            files: 8
          },
          {
            hash: 'b2c3d4e5f6g7h8i9',
            message: 'fix: 修复登录页面样式问题',
            author: '李四',
            date: new Date('2024-01-14T16:45:00'),
            additions: 45,
            deletions: 12,
            files: 3
          }
        ]
        
        pagination.total = 156
        
      } catch (error) {
        ElMessage.error('加载数据失败')
      } finally {
        loading.trend = false
        loading.author = false
        loading.time = false
        loading.fileType = false
        loading.table = false
      }
    }

    const loadRepositories = async () => {
      repositories.value = [
        { id: 1, name: 'frontend-project' },
        { id: 2, name: 'backend-api' },
        { id: 3, name: 'mobile-app' }
      ]
    }

    const loadAuthors = async () => {
      authors.value = ['张三', '李四', '王五', '赵六']
    }

    const handleDateChange = () => {
      loadData()
    }

    const resetFilters = () => {
      filters.dateRange = []
      filters.repository = ''
      filters.author = ''
      loadData()
    }

    const handleSizeChange = (size) => {
      pagination.size = size
      loadData()
    }

    const handlePageChange = (page) => {
      pagination.page = page
      loadData()
    }

    const viewCommit = (commit) => {
      ElMessage.info(`查看提交: ${commit.hash}`)
    }

    const exportData = () => {
      ElMessage.success('导出功能开发中...')
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    // 监听器
    watch(trendType, () => {
      initTrendChart()
    })

    watch(timeDistributionType, () => {
      updateTimeChart()
    })

    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadRepositories(),
        loadAuthors(),
        loadData()
      ])
      
      nextTick(() => {
        initTrendChart()
        initAuthorChart()
        initTimeChart()
        initFileTypeChart()
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
          trendChart?.resize()
          authorChart?.resize()
          timeChart?.resize()
          fileTypeChart?.resize()
        })
      })
    })

    return {
      trendChartRef,
      authorChartRef,
      timeChartRef,
      fileTypeChartRef,
      loading,
      filters,
      trendType,
      timeDistributionType,
      repositories,
      authors,
      commitList,
      commitStats,
      pagination,
      loadData,
      handleDateChange,
      resetFilters,
      handleSizeChange,
      handlePageChange,
      viewCommit,
      exportData,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.commits-analytics {
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

.filter-card {
  margin-bottom: 24px;
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

.chart-card {
  margin-bottom: 24px;
  
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
  
  .chart-container {
    height: 300px;
    width: 100%;
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
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.text-success {
  color: $success-color;
}

.text-danger {
  color: $danger-color;
}

@include respond-to('mobile') {
  .commits-analytics {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 16px;
    
    .page-title {
      font-size: 24px;
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
  
  .chart-container {
    height: 250px !important;
  }
}
</style>