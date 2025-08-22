<template>
  <div class="time-distribution-analytics">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">时间分布分析</h1>
      <p class="page-subtitle">开发活动时间模式与效率分析</p>
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
        <el-form-item label="团队成员">
          <el-select v-model="filters.member" placeholder="选择成员" clearable>
            <el-option
              v-for="member in members"
              :key="member"
              :label="member"
              :value="member"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="filters.activityType" placeholder="选择类型" clearable>
            <el-option label="提交" value="commit" />
            <el-option label="合并请求" value="merge_request" />
            <el-option label="代码审查" value="review" />
            <el-option label="问题处理" value="issue" />
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
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in timeStats" :key="index">
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
      <!-- 24小时活动热力图 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">24小时活动热力图</span>
              <el-radio-group v-model="heatmapType" size="small">
                <el-radio-button label="commits">提交</el-radio-button>
                <el-radio-button label="reviews">审查</el-radio-button>
                <el-radio-button label="issues">问题</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="heatmapChartRef" v-loading="loading.heatmap"></div>
        </el-card>
      </el-col>

      <!-- 工作日分布 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">工作日分布</span>
            </div>
          </template>
          <div class="chart-container" ref="weekdayChartRef" v-loading="loading.weekday"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 月度活动趋势 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">月度活动趋势</span>
            </div>
          </template>
          <div class="chart-container" ref="monthlyChartRef" v-loading="loading.monthly"></div>
        </el-card>
      </el-col>

      <!-- 团队成员活跃度对比 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">团队成员活跃度</span>
            </div>
          </template>
          <div class="chart-container" ref="memberActivityChartRef" v-loading="loading.memberActivity"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 工作效率分析 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">工作效率分析</span>
              <el-radio-group v-model="efficiencyMetric" size="small">
                <el-radio-button label="commits_per_hour">每小时提交</el-radio-button>
                <el-radio-button label="lines_per_hour">每小时代码行</el-radio-button>
                <el-radio-button label="reviews_per_day">每日审查</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="efficiencyChartRef" v-loading="loading.efficiency"></div>
        </el-card>
      </el-col>

      <!-- 工作时长分布 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">工作时长分布</span>
            </div>
          </template>
          <div class="chart-container" ref="durationChartRef" v-loading="loading.duration"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">活动详情</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="exportData">
              <i class="el-icon-download"></i>
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      <el-table
        :data="activityList"
        v-loading="loading.table"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date, 'YYYY-MM-DD') }}
          </template>
        </el-table-column>
        <el-table-column prop="member" label="成员" width="120" />
        <el-table-column prop="activity_type" label="活动类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActivityTypeColor(row.activity_type)" size="small">
              {{ getActivityTypeText(row.activity_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="100">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="100">
          <template #default="{ row }">
            {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="持续时间" width="100" align="right">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="commits" label="提交数" width="80" align="right" />
        <el-table-column prop="lines_changed" label="代码行数" width="100" align="right">
          <template #default="{ row }">
            <span class="text-success">+{{ row.lines_added }}</span>
            <span class="text-danger">-{{ row.lines_deleted }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="efficiency_score" label="效率评分" width="100" align="right">
          <template #default="{ row }">
            <el-progress
              :percentage="row.efficiency_score"
              :color="getEfficiencyColor(row.efficiency_score)"
              :show-text="false"
              :stroke-width="8"
            />
            <span class="efficiency-text">{{ row.efficiency_score }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewDetails(row)">
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
  name: 'TimeDistributionAnalytics',
  setup() {
    const store = useStore()

    // 图表引用
    const heatmapChartRef = ref(null)
    const weekdayChartRef = ref(null)
    const monthlyChartRef = ref(null)
    const memberActivityChartRef = ref(null)
    const efficiencyChartRef = ref(null)
    const durationChartRef = ref(null)

    // 响应式数据
    const loading = reactive({
      heatmap: false,
      weekday: false,
      monthly: false,
      memberActivity: false,
      efficiency: false,
      duration: false,
      table: false
    })

    const filters = reactive({
      dateRange: [],
      repository: '',
      member: '',
      activityType: ''
    })

    const heatmapType = ref('commits')
    const efficiencyMetric = ref('commits_per_hour')
    const repositories = ref([])
    const members = ref([])
    const activityList = ref([])
    const timeStats = ref([])

    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 图表实例
    let heatmapChart = null
    let weekdayChart = null
    let monthlyChart = null
    let memberActivityChart = null
    let efficiencyChart = null
    let durationChart = null

    // 方法
    const initHeatmapChart = () => {
      if (!heatmapChartRef.value) return
      
      heatmapChart = echarts.init(heatmapChartRef.value)
      
      // 生成热力图数据
      const hours = Array.from({ length: 24 }, (_, i) => i)
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const data = []
      
      for (let i = 0; i < 7; i++) {
        for (let j = 0; j < 24; j++) {
          const value = Math.floor(Math.random() * 100)
          data.push([j, i, value])
        }
      }
      
      const option = {
        tooltip: {
          position: 'top',
          formatter: function (params) {
            return `${days[params.data[1]]} ${params.data[0]}:00<br/>活动数: ${params.data[2]}`
          }
        },
        grid: {
          height: '50%',
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: hours,
          splitArea: {
            show: true
          },
          axisLabel: {
            formatter: '{value}:00'
          }
        },
        yAxis: {
          type: 'category',
          data: days,
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: 0,
          max: 100,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '15%',
          inRange: {
            color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
          }
        },
        series: [{
          name: '活动热力图',
          type: 'heatmap',
          data: data,
          label: {
            show: false
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      
      heatmapChart.setOption(option)
    }

    const initWeekdayChart = () => {
      if (!weekdayChartRef.value) return
      
      weekdayChart = echarts.init(weekdayChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '工作日分布',
          type: 'pie',
          radius: '70%',
          data: [
            { value: 20, name: '周一', itemStyle: { color: '#5470c6' } },
            { value: 22, name: '周二', itemStyle: { color: '#91cc75' } },
            { value: 25, name: '周三', itemStyle: { color: '#fac858' } },
            { value: 23, name: '周四', itemStyle: { color: '#ee6666' } },
            { value: 18, name: '周五', itemStyle: { color: '#73c0de' } },
            { value: 8, name: '周六', itemStyle: { color: '#3ba272' } },
            { value: 4, name: '周日', itemStyle: { color: '#fc8452' } }
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
            formatter: '{b}\n{d}%'
          }
        }]
      }
      weekdayChart.setOption(option)
    }

    const initMonthlyChart = () => {
      if (!monthlyChartRef.value) return
      
      monthlyChart = echarts.init(monthlyChartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['提交', '合并请求', '代码审查']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '提交',
            type: 'line',
            smooth: true,
            data: [120, 132, 101, 134, 90, 230],
            itemStyle: { color: '#5470c6' }
          },
          {
            name: '合并请求',
            type: 'line',
            smooth: true,
            data: [45, 52, 38, 48, 35, 67],
            itemStyle: { color: '#91cc75' }
          },
          {
            name: '代码审查',
            type: 'line',
            smooth: true,
            data: [78, 85, 72, 89, 65, 98],
            itemStyle: { color: '#fac858' }
          }
        ]
      }
      monthlyChart.setOption(option)
    }

    const initMemberActivityChart = () => {
      if (!memberActivityChartRef.value) return
      
      memberActivityChart = echarts.init(memberActivityChartRef.value)
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
          name: '活跃度评分',
          type: 'bar',
          data: [85, 92, 78, 88, 75],
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [{
                offset: 0, color: '#667eea'
              }, {
                offset: 1, color: '#764ba2'
              }]
            }
          }
        }]
      }
      memberActivityChart.setOption(option)
    }

    const initEfficiencyChart = () => {
      if (!efficiencyChartRef.value) return
      
      efficiencyChart = echarts.init(efficiencyChartRef.value)
      updateEfficiencyChart()
    }

    const updateEfficiencyChart = () => {
      if (!efficiencyChart) return
      
      let seriesData, yAxisName
      
      switch (efficiencyMetric.value) {
        case 'commits_per_hour':
          seriesData = [2.5, 3.2, 2.8, 3.5, 2.9, 3.1, 2.7]
          yAxisName = '每小时提交数'
          break
        case 'lines_per_hour':
          seriesData = [45, 52, 38, 58, 42, 48, 35]
          yAxisName = '每小时代码行数'
          break
        case 'reviews_per_day':
          seriesData = [8, 12, 6, 15, 9, 11, 7]
          yAxisName = '每日审查数'
          break
        default:
          seriesData = [2.5, 3.2, 2.8, 3.5, 2.9, 3.1, 2.7]
          yAxisName = '每小时提交数'
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
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value',
          name: yAxisName
        },
        series: [{
          name: yAxisName,
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
      
      efficiencyChart.setOption(option)
    }

    const initDurationChart = () => {
      if (!durationChartRef.value) return
      
      durationChart = echarts.init(durationChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '工作时长分布',
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: 35, name: '< 4小时', itemStyle: { color: '#f56c6c' } },
            { value: 45, name: '4-8小时', itemStyle: { color: '#67c23a' } },
            { value: 15, name: '8-10小时', itemStyle: { color: '#e6a23c' } },
            { value: 5, name: '> 10小时', itemStyle: { color: '#909399' } }
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
            formatter: '{b}\n{d}%'
          }
        }]
      }
      durationChart.setOption(option)
    }

    const loadData = async () => {
      try {
        Object.keys(loading).forEach(key => {
          loading[key] = true
        })

        // 模拟加载数据
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟统计数据
        timeStats.value = [
          {
            title: '平均工作时长',
            value: '7.2h',
            change: '+0.5h',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-time',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          },
          {
            title: '最活跃时段',
            value: '14:00',
            change: '无变化',
            changeType: 'neutral',
            changeIcon: 'el-icon-minus',
            icon: 'el-icon-sunny',
            color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
          },
          {
            title: '工作效率评分',
            value: '85.6',
            change: '+3.2',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-trophy',
            color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
          },
          {
            title: '团队协作指数',
            value: '92%',
            change: '+5%',
            changeType: 'positive',
            changeIcon: 'el-icon-arrow-up',
            icon: 'el-icon-user',
            color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
          }
        ]
        
        // 模拟活动列表数据
        activityList.value = [
          {
            date: new Date('2024-01-15'),
            member: '张三',
            activity_type: 'commit',
            start_time: '09:00',
            end_time: '17:30',
            duration: 8.5,
            commits: 12,
            lines_added: 245,
            lines_deleted: 56,
            efficiency_score: 85
          },
          {
            date: new Date('2024-01-15'),
            member: '李四',
            activity_type: 'review',
            start_time: '10:00',
            end_time: '18:00',
            duration: 8.0,
            commits: 0,
            lines_added: 0,
            lines_deleted: 0,
            efficiency_score: 92
          },
          {
            date: new Date('2024-01-14'),
            member: '王五',
            activity_type: 'merge_request',
            start_time: '08:30',
            end_time: '16:45',
            duration: 8.25,
            commits: 8,
            lines_added: 156,
            lines_deleted: 34,
            efficiency_score: 78
          }
        ]
        
        pagination.total = 156
        
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

    const loadMembers = async () => {
      members.value = ['张三', '李四', '王五', '赵六', '钱七']
    }

    const handleDateChange = () => {
      loadData()
    }

    const resetFilters = () => {
      filters.dateRange = []
      filters.repository = ''
      filters.member = ''
      filters.activityType = ''
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

    const viewDetails = (activity) => {
      ElMessage.info(`查看活动详情: ${activity.member} - ${activity.date}`)
    }

    const exportData = () => {
      ElMessage.success('导出功能开发中...')
    }

    const getActivityTypeColor = (type) => {
      const colorMap = {
        commit: 'primary',
        merge_request: 'success',
        review: 'warning',
        issue: 'danger'
      }
      return colorMap[type] || 'info'
    }

    const getActivityTypeText = (type) => {
      const textMap = {
        commit: '提交',
        merge_request: '合并请求',
        review: '代码审查',
        issue: '问题处理'
      }
      return textMap[type] || type
    }

    const getEfficiencyColor = (score) => {
      if (score >= 90) return '#67c23a'
      if (score >= 70) return '#e6a23c'
      return '#f56c6c'
    }

    const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    const formatTime = (time) => {
      return time
    }

    const formatDuration = (hours) => {
      if (hours < 1) return `${Math.round(hours * 60)}分钟`
      return `${hours.toFixed(1)}小时`
    }

    // 监听器
    watch(heatmapType, () => {
      initHeatmapChart()
    })

    watch(efficiencyMetric, () => {
      updateEfficiencyChart()
    })

    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadRepositories(),
        loadMembers(),
        loadData()
      ])
      
      nextTick(() => {
        initHeatmapChart()
        initWeekdayChart()
        initMonthlyChart()
        initMemberActivityChart()
        initEfficiencyChart()
        initDurationChart()
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
          heatmapChart?.resize()
          weekdayChart?.resize()
          monthlyChart?.resize()
          memberActivityChart?.resize()
          efficiencyChart?.resize()
          durationChart?.resize()
        })
      })
    })

    return {
      heatmapChartRef,
      weekdayChartRef,
      monthlyChartRef,
      memberActivityChartRef,
      efficiencyChartRef,
      durationChartRef,
      loading,
      filters,
      heatmapType,
      efficiencyMetric,
      repositories,
      members,
      activityList,
      timeStats,
      pagination,
      loadData,
      handleDateChange,
      resetFilters,
      handleSizeChange,
      handlePageChange,
      viewDetails,
      exportData,
      getActivityTypeColor,
      getActivityTypeText,
      getEfficiencyColor,
      formatDate,
      formatTime,
      formatDuration
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.time-distribution-analytics {
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
  
  .efficiency-text {
    margin-left: 8px;
    font-size: 12px;
    color: $text-color-secondary;
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
  .time-distribution-analytics {
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