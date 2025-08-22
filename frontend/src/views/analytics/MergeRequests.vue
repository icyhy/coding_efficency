<template>
  <div class="merge-requests-analytics">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">合并请求分析</h1>
      <p class="page-subtitle">代码合并请求统计与质量分析</p>
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
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="已合并" value="merged" />
            <el-option label="待审核" value="open" />
            <el-option label="已关闭" value="closed" />
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
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in mrStats" :key="index">
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
      <!-- 合并请求状态分布 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">状态分布</span>
            </div>
          </template>
          <div class="chart-container" ref="statusChartRef" v-loading="loading.status"></div>
        </el-card>
      </el-col>

      <!-- 合并请求趋势 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">合并请求趋势</span>
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
    </el-row>

    <el-row :gutter="20">
      <!-- 审核时间分析 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">审核时间分析</span>
            </div>
          </template>
          <div class="chart-container" ref="reviewTimeChartRef" v-loading="loading.reviewTime"></div>
        </el-card>
      </el-col>

      <!-- 作者贡献分析 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">作者贡献分析</span>
            </div>
          </template>
          <div class="chart-container" ref="authorChartRef" v-loading="loading.author"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 代码质量指标 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">代码质量指标</span>
            </div>
          </template>
          <div class="chart-container" ref="qualityChartRef" v-loading="loading.quality"></div>
        </el-card>
      </el-col>

      <!-- 合并频率 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">合并频率</span>
            </div>
          </template>
          <div class="chart-container" ref="frequencyChartRef" v-loading="loading.frequency"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">合并请求详情</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="exportData">
              <i class="el-icon-download"></i>
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      <el-table
        :data="mrList"
        v-loading="loading.table"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="merged_at" label="合并时间" width="180">
          <template #default="{ row }">
            {{ row.merged_at ? formatDate(row.merged_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="review_time" label="审核时长" width="120" align="right">
          <template #default="{ row }">
            {{ formatDuration(row.review_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="changes" label="代码变更" width="120" align="right">
          <template #default="{ row }">
            <span class="text-success">+{{ row.additions }}</span>
            <span class="text-danger">-{{ row.deletions }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="comments" label="评论数" width="80" align="right" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewMR(row)">
              查看详情
            </el-button>
            <el-button type="text" size="small" @click="viewDiff(row)">
              查看差异
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
  name: 'MergeRequestsAnalytics',
  setup() {
    const store = useStore()

    // 图表引用
    const statusChartRef = ref(null)
    const trendChartRef = ref(null)
    const reviewTimeChartRef = ref(null)
    const authorChartRef = ref(null)
    const qualityChartRef = ref(null)
    const frequencyChartRef = ref(null)

    // 响应式数据
    const loading = reactive({
      status: false,
      trend: false,
      reviewTime: false,
      author: false,
      quality: false,
      frequency: false,
      table: false
    })

    const filters = reactive({
      dateRange: [],
      repository: '',
      status: '',
      author: ''
    })

    const trendType = ref('daily')
    const repositories = ref([])
    const authors = ref([])
    const mrList = ref([])
    const mrStats = ref([])

    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 图表实例
    let statusChart = null
    let trendChart = null
    let reviewTimeChart = null
    let authorChart = null
    let qualityChart = null
    let frequencyChart = null

    // 方法
    const initStatusChart = () => {
      if (!statusChartRef.value) return
      
      statusChart = echarts.init(statusChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '合并请求状态',
          type: 'pie',
          radius: '70%',
          data: [
            { value: 65, name: '已合并', itemStyle: { color: '#67c23a' } },
            { value: 20, name: '待审核', itemStyle: { color: '#e6a23c' } },
            { value: 15, name: '已关闭', itemStyle: { color: '#f56c6c' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}: {c}\n({d}%)'
          }
        }]
      }
      statusChart.setOption(option)
    }

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
        legend: {
          data: ['创建', '合并', '关闭']
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
        series: [
          {
            name: '创建',
            type: 'line',
            smooth: true,
            data: [8, 12, 15, 10, 18, 14, 16],
            itemStyle: { color: '#409eff' }
          },
          {
            name: '合并',
            type: 'line',
            smooth: true,
            data: [6, 10, 12, 8, 15, 12, 14],
            itemStyle: { color: '#67c23a' }
          },
          {
            name: '关闭',
            type: 'line',
            smooth: true,
            data: [2, 2, 3, 2, 3, 2, 2],
            itemStyle: { color: '#f56c6c' }
          }
        ]
      }
      trendChart.setOption(option)
    }

    const initReviewTimeChart = () => {
      if (!reviewTimeChartRef.value) return
      
      reviewTimeChart = echarts.init(reviewTimeChartRef.value)
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
          data: ['<1h', '1-4h', '4-8h', '8-24h', '1-3d', '3-7d', '>7d']
        },
        yAxis: {
          type: 'value',
          name: '合并请求数量'
        },
        series: [{
          name: '审核时间分布',
          type: 'bar',
          data: [5, 15, 25, 35, 20, 8, 2],
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: '#667eea'
              }, {
                offset: 1, color: '#764ba2'
              }]
            }
          }
        }]
      }
      reviewTimeChart.setOption(option)
    }

    const initAuthorChart = () => {
      if (!authorChartRef.value) return
      
      authorChart = echarts.init(authorChartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: ['张三', '李四', '王五', '赵六', '钱七']
        },
        series: [{
          name: '合并请求数',
          type: 'bar',
          data: [25, 20, 18, 15, 12],
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [{
                offset: 0, color: '#4facfe'
              }, {
                offset: 1, color: '#00f2fe'
              }]
            }
          }
        }]
      }
      authorChart.setOption(option)
    }

    const initQualityChart = () => {
      if (!qualityChartRef.value) return
      
      qualityChart = echarts.init(qualityChartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['代码覆盖率', '代码质量评分', '技术债务']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        },
        yAxis: [
          {
            type: 'value',
            name: '百分比 (%)',
            min: 0,
            max: 100
          },
          {
            type: 'value',
            name: '技术债务 (小时)',
            min: 0
          }
        ],
        series: [
          {
            name: '代码覆盖率',
            type: 'line',
            yAxisIndex: 0,
            data: [85, 87, 89, 92],
            itemStyle: { color: '#67c23a' }
          },
          {
            name: '代码质量评分',
            type: 'line',
            yAxisIndex: 0,
            data: [78, 82, 85, 88],
            itemStyle: { color: '#409eff' }
          },
          {
            name: '技术债务',
            type: 'bar',
            yAxisIndex: 1,
            data: [24, 20, 18, 15],
            itemStyle: { color: '#f56c6c' }
          }
        ]
      }
      qualityChart.setOption(option)
    }

    const initFrequencyChart = () => {
      if (!frequencyChartRef.value) return
      
      frequencyChart = echarts.init(frequencyChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '合并频率',
          type: 'gauge',
          radius: '80%',
          data: [{
            value: 75,
            name: '合并率',
            title: {
              offsetCenter: [0, '30%']
            },
            detail: {
              offsetCenter: [0, '50%'],
              formatter: '{value}%'
            }
          }],
          axisLine: {
            lineStyle: {
              width: 20,
              color: [
                [0.3, '#f56c6c'],
                [0.7, '#e6a23c'],
                [1, '#67c23a']
              ]
            }
          },
          pointer: {
            itemStyle: {
              color: 'auto'
            }
          },
          axisTick: {
            distance: -20,
            length: 8,
            lineStyle: {
              color: '#fff',
              width: 2
            }
          },
          splitLine: {
            distance: -20,
            length: 20,
            lineStyle: {
              color: '#fff',
              width: 4
            }
          },
          axisLabel: {
            color: 'auto',
            distance: 40,
            fontSize: 12
          },
          detail: {
            valueAnimation: true,
            formatter: '{value}%',
            color: 'auto',
            fontSize: 20
          }
        }]
      }
      frequencyChart.setOption(option)
    }

    const loadData = async () => {
      try {
        Object.keys(loading).forEach(key => {
          loading[key] = true
        })

        // 模拟加载数据
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟统计数据
        mrStats.value = [
          {
            title: '总合并请求',
            value: '456',
            change: '+15.2%',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-s-order',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          },
          {
            title: '合并成功率',
            value: '85.6%',
            change: '+2.1%',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-success',
            color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
          },
          {
            title: '平均审核时间',
            value: '4.2h',
            change: '-0.8h',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-down',
            icon: 'el-icon-time',
            color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
          },
          {
            title: '代码质量评分',
            value: '8.7',
            change: '+0.3',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-star-on',
            color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
          }
        ]
        
        // 模拟合并请求列表数据
        mrList.value = [
          {
            id: 123,
            title: 'feat: 添加用户权限管理功能',
            author: '张三',
            status: 'merged',
            created_at: new Date('2024-01-15T09:30:00'),
            merged_at: new Date('2024-01-15T14:20:00'),
            review_time: 4.8,
            additions: 245,
            deletions: 56,
            comments: 8
          },
          {
            id: 124,
            title: 'fix: 修复登录页面响应式布局问题',
            author: '李四',
            status: 'open',
            created_at: new Date('2024-01-14T16:45:00'),
            merged_at: null,
            review_time: 0,
            additions: 89,
            deletions: 23,
            comments: 3
          },
          {
            id: 125,
            title: 'refactor: 重构数据库查询逻辑',
            author: '王五',
            status: 'closed',
            created_at: new Date('2024-01-13T11:20:00'),
            merged_at: null,
            review_time: 0,
            additions: 156,
            deletions: 234,
            comments: 12
          }
        ]
        
        pagination.total = 456
        
      } catch (error) {
        ElMessage.error('加载数据失败')
      } finally {
        Object.keys(loading).forEach(key => {
          loading[key] = false
        })
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
      authors.value = ['张三', '李四', '王五', '赵六', '钱七']
    }

    const handleDateChange = () => {
      loadData()
    }

    const resetFilters = () => {
      filters.dateRange = []
      filters.repository = ''
      filters.status = ''
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

    const viewMR = (mr) => {
      ElMessage.info(`查看合并请求: ${mr.id}`)
    }

    const viewDiff = (mr) => {
      ElMessage.info(`查看代码差异: ${mr.id}`)
    }

    const exportData = () => {
      ElMessage.success('导出功能开发中...')
    }

    const getStatusType = (status) => {
      const statusMap = {
        merged: 'success',
        open: 'warning',
        closed: 'danger'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        merged: '已合并',
        open: '待审核',
        closed: '已关闭'
      }
      return statusMap[status] || status
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    const formatDuration = (hours) => {
      if (hours === 0) return '-'
      if (hours < 1) return `${Math.round(hours * 60)}分钟`
      if (hours < 24) return `${hours.toFixed(1)}小时`
      return `${Math.round(hours / 24)}天`
    }

    // 监听器
    watch(trendType, () => {
      initTrendChart()
    })

    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadRepositories(),
        loadAuthors(),
        loadData()
      ])
      
      nextTick(() => {
        initStatusChart()
        initTrendChart()
        initReviewTimeChart()
        initAuthorChart()
        initQualityChart()
        initFrequencyChart()
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
          statusChart?.resize()
          trendChart?.resize()
          reviewTimeChart?.resize()
          authorChart?.resize()
          qualityChart?.resize()
          frequencyChart?.resize()
        })
      })
    })

    return {
      statusChartRef,
      trendChartRef,
      reviewTimeChartRef,
      authorChartRef,
      qualityChartRef,
      frequencyChartRef,
      loading,
      filters,
      trendType,
      repositories,
      authors,
      mrList,
      mrStats,
      pagination,
      loadData,
      handleDateChange,
      resetFilters,
      handleSizeChange,
      handlePageChange,
      viewMR,
      viewDiff,
      exportData,
      getStatusType,
      getStatusText,
      formatDate,
      formatDuration
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.merge-requests-analytics {
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
    
    .header-actions {
      display: flex;
      gap: 8px;
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
  margin-right: 8px;
}

.text-danger {
  color: $danger-color;
}

@include respond-to('mobile') {
  .merge-requests-analytics {
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