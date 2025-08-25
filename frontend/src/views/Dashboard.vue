<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
      <p class="page-subtitle">代码效率分析概览</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in stats" :key="index">
        <div class="stat-card" :style="{ background: stat.gradient }">
          <div class="stat-icon">
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
    <el-row :gutter="20" class="charts-row">
      <!-- 提交趋势图 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">提交趋势</span>
              <el-select v-model="commitPeriod" size="small" style="width: 120px">
                <el-option label="最近7天" value="7d"></el-option>
                <el-option label="最近30天" value="30d"></el-option>
                <el-option label="最近90天" value="90d"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="commitChartRef" v-loading="loading.commits"></div>
        </el-card>
      </el-col>

      <!-- 合并请求状态 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">合并请求状态</span>
            </div>
          </template>
          <div class="chart-container" ref="mergeRequestChartRef" v-loading="loading.mergeRequests"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- 代码质量评分 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">代码质量评分</span>
            </div>
          </template>
          <div class="chart-container" ref="qualityChartRef" v-loading="loading.quality"></div>
        </el-card>
      </el-col>

      <!-- 活跃度分布 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">开发活跃度</span>
              <el-radio-group v-model="activityType" size="small">
                <el-radio-button label="hour">小时</el-radio-button>
                <el-radio-button label="weekday">星期</el-radio-button>
                <el-radio-button label="month">月份</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="activityChartRef" v-loading="loading.activity"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近活动</span>
              <el-button type="text" size="small" @click="refreshActivities">
                <i class="el-icon-refresh"></i>
                刷新
              </el-button>
            </div>
          </template>
          <div class="activity-list" v-loading="loading.activities">
            <div 
              class="activity-item" 
              v-for="activity in recentActivities" 
              :key="activity.id"
            >
              <div class="activity-avatar">
                <el-avatar :size="32" :src="activity.avatar">
                  {{ activity.author.charAt(0) }}
                </el-avatar>
              </div>
              <div class="activity-content">
                <div class="activity-title">
                  <strong>{{ activity.author }}</strong>
                  {{ activity.action }}
                  <el-link type="primary" :underline="false">
                    {{ activity.target }}
                  </el-link>
                </div>
                <div class="activity-time">
                  {{ formatTime(activity.timestamp) }}
                </div>
              </div>
              <div class="activity-type">
                <el-tag :type="getActivityTagType(activity.type)" size="small">
                  {{ activity.type }}
                </el-tag>
              </div>
            </div>
            <div class="empty-state" v-if="!recentActivities.length && !loading.activities">
              <i class="el-icon-document-copy"></i>
              <p>暂无活动记录</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 快速操作 -->
      <el-col :xs="24" :lg="8">
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="goToPage('/repositories')">
              <div class="action-icon">
                <i class="el-icon-folder"></i>
              </div>
              <div class="action-content">
                <div class="action-title">仓库管理</div>
                <div class="action-desc">添加和管理代码仓库</div>
              </div>
            </div>
            <div class="action-item" @click="goToPage('/analytics/commits')">
              <div class="action-icon">
                <i class="el-icon-data-analysis"></i>
              </div>
              <div class="action-content">
                <div class="action-title">提交分析</div>
                <div class="action-desc">查看详细的提交统计</div>
              </div>
            </div>
            <div class="action-item" @click="goToPage('/analytics/efficiency')">
              <div class="action-icon">
                <i class="el-icon-trophy"></i>
              </div>
              <div class="action-content">
                <div class="action-title">效率评分</div>
                <div class="action-desc">查看代码效率评估</div>
              </div>
            </div>
            <div class="action-item" @click="goToPage('/settings')">
              <div class="action-icon">
                <i class="el-icon-setting"></i>
              </div>
              <div class="action-content">
                <div class="action-title">系统设置</div>
                <div class="action-desc">配置系统参数</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getDashboardData } from '@/api/analytics'

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const store = useStore()

    // 图表引用
    const commitChartRef = ref(null)
    const mergeRequestChartRef = ref(null)
    const qualityChartRef = ref(null)
    const activityChartRef = ref(null)

    // 响应式数据
    const loading = reactive({
      commits: false,
      mergeRequests: false,
      quality: false,
      activity: false,
      activities: false
    })

    const commitPeriod = ref('30d')
    const activityType = ref('hour')
    const recentActivities = ref([])

    // 统计数据
    const stats = ref([
      {
        title: '总提交数',
        value: '1,234',
        change: '+12.5%',
        changeType: 'positive',
        changeIcon: 'el-icon-arrow-up',
        icon: 'el-icon-document',
        gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      },
      {
        title: '合并请求',
        value: '89',
        change: '+8.2%',
        changeType: 'positive',
        changeIcon: 'el-icon-arrow-up',
        icon: 'el-icon-connection',
        gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
      },
      {
        title: '代码质量',
        value: '92',
        change: '+2.1%',
        changeType: 'positive',
        changeIcon: 'el-icon-arrow-up',
        icon: 'el-icon-trophy',
        gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
      },
      {
        title: '活跃仓库',
        value: '15',
        change: '0%',
        changeType: 'neutral',
        changeIcon: 'el-icon-minus',
        icon: 'el-icon-folder',
        gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
      }
    ])

    // 图表实例
    let commitChart = null
    let mergeRequestChart = null
    let qualityChart = null
    let activityChart = null

    // 图表数据
    const chartData = reactive({
      commits: {
        dates: [],
        values: []
      },
      mergeRequests: {
        opened: 0,
        merged: 0,
        closed: 0
      },
      quality: {
        categories: [],
        scores: []
      },
      activity: {
        hours: [],
        commits: []
      }
    })

    // 方法
    const initCommitChart = async () => {
      if (!commitChartRef.value) return
      
      let dates = []
      let values = []
      
      try {
        // 获取提交趋势数据
        const params = {
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0],
          group_by: 'day'
        }
        
        const response = await getDashboardData(params)
        
        if (response && response.data && response.data.commit_trend) {
          const trend = response.data.commit_trend
          dates = trend.map(item => item.date)
          values = trend.map(item => item.count)
          console.log('成功获取提交趋势数据:', dates, values)
        } else {
          console.warn('提交趋势数据格式不正确，使用默认数据')
          throw new Error('数据格式不正确')
        }
      } catch (error) {
        console.error('获取提交趋势数据失败:', error)
        // 使用默认数据
        const today = new Date()
        for (let i = 6; i >= 0; i--) {
          const date = new Date(today.getTime() - i * 24 * 60 * 60 * 1000)
          dates.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
          values.push(Math.floor(Math.random() * 30) + 5)
        }
        console.log('使用默认提交趋势数据:', dates, values)
      }
      
      try {
        chartData.commits.dates = dates
        chartData.commits.values = values
        
        commitChart = echarts.init(commitChartRef.value)
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross'
            },
            formatter: function(params) {
              return `${params[0].name}<br/>${params[0].seriesName}: ${params[0].value} 次提交`
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
            data: dates,
            axisLabel: {
              color: '#666'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: '#666'
            }
          },
          series: [{
            name: '提交数',
            type: 'line',
            smooth: true,
            data: values,
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
        
        if (commitChart) {
          commitChart.setOption(option)
        }
      } catch (error) {
        console.error('初始化提交图表失败:', error)
        // 使用默认数据
        const defaultDates = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        const defaultValues = [12, 19, 15, 25, 22, 18, 20]
        
        commitChart = echarts.init(commitChartRef.value)
        const defaultOption = {
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
            data: defaultDates
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            name: '提交数',
            type: 'line',
            smooth: true,
            data: defaultValues,
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
        
        if (commitChart) {
          commitChart.setOption(defaultOption)
        }
      }
    }

    const initMergeRequestChart = async () => {
      if (!mergeRequestChartRef.value) {
        console.warn('合并请求图表DOM元素不存在')
        return
      }
      
      // 确保DOM元素已正确挂载
      await nextTick()
      
      // 检查DOM元素是否仍然存在
      if (!mergeRequestChartRef.value) {
        console.error('合并请求图表DOM元素在nextTick后仍不存在')
        return
      }
      
      let option
      let mergeRequestData = [
        { value: 35, name: '已合并', itemStyle: { color: '#67c23a' } },
        { value: 15, name: '待审核', itemStyle: { color: '#e6a23c' } },
        { value: 8, name: '已拒绝', itemStyle: { color: '#f56c6c' } },
        { value: 12, name: '草稿', itemStyle: { color: '#909399' } }
      ]
      
      try {
        // 获取合并请求数据
        const params = {
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0]
        }
        
        const response = await getDashboardData(params)
        
        if (response && response.data && response.data.merge_request_stats) {
          const stats = response.data.merge_request_stats
          mergeRequestData = [
            { value: stats.merged || 0, name: '已合并', itemStyle: { color: '#67c23a' } },
            { value: stats.opened || 0, name: '待审核', itemStyle: { color: '#e6a23c' } },
            { value: stats.closed || 0, name: '已拒绝', itemStyle: { color: '#f56c6c' } },
            { value: stats.draft || 0, name: '草稿', itemStyle: { color: '#909399' } }
          ]
          
          chartData.mergeRequests.opened = stats.opened || 0
          chartData.mergeRequests.merged = stats.merged || 0
          chartData.mergeRequests.closed = stats.closed || 0
          console.log('成功获取合并请求数据:', chartData.mergeRequests)
        } else {
          console.warn('合并请求数据格式不正确，使用默认数据')
        }
        
      } catch (error) {
        console.error('获取合并请求数据失败:', error)
        // 继续使用默认数据
      }
      
      // 统一初始化图表
      try {
        // 如果图表已存在，先销毁
        if (mergeRequestChart) {
          mergeRequestChart.dispose()
        }
        
        mergeRequestChart = echarts.init(mergeRequestChartRef.value)
        
        option = {
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              return `${params.name}: ${params.value} (${params.percent}%)`
            }
          },
          legend: {
            bottom: '0%',
            left: 'center',
            textStyle: {
              color: '#666'
            }
          },
          series: [{
            name: '合并请求',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '45%'],
            data: mergeRequestData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              formatter: '{b}: {c}'
            }
          }]
        }
        
        mergeRequestChart.setOption(option)
        console.log('合并请求图表初始化成功')
        
      } catch (chartError) {
        console.error('初始化合并请求图表失败:', chartError)
      }
    }

    const initQualityChart = () => {
      if (!qualityChartRef.value) return
      
      qualityChart = echarts.init(qualityChartRef.value)
      const option = {
        series: [{
          type: 'gauge',
          center: ['50%', '60%'],
          startAngle: 200,
          endAngle: -40,
          min: 0,
          max: 100,
          splitNumber: 5,
          itemStyle: {
            color: '#58D9F9',
            shadowColor: 'rgba(0,138,255,0.45)',
            shadowBlur: 10,
            shadowOffsetX: 2,
            shadowOffsetY: 2
          },
          progress: {
            show: true,
            roundCap: true,
            width: 18
          },
          pointer: {
            icon: 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z',
            length: '75%',
            width: 16,
            offsetCenter: [0, '5%']
          },
          axisLine: {
            roundCap: true,
            lineStyle: {
              width: 18
            }
          },
          axisTick: {
            splitNumber: 2,
            lineStyle: {
              width: 2,
              color: '#999'
            }
          },
          splitLine: {
            length: 12,
            lineStyle: {
              width: 3,
              color: '#999'
            }
          },
          axisLabel: {
            distance: 30,
            color: '#999',
            fontSize: 20
          },
          title: {
            show: false
          },
          detail: {
            backgroundColor: '#fff',
            borderColor: '#999',
            borderWidth: 2,
            width: '60%',
            lineHeight: 40,
            height: 40,
            borderRadius: 8,
            offsetCenter: [0, '35%'],
            valueAnimation: true,
            formatter: function (value) {
              return '{value|' + value.toFixed(0) + '}{unit|分}'
            },
            rich: {
              value: {
                fontSize: 50,
                fontWeight: 'bolder',
                color: '#777'
              },
              unit: {
                fontSize: 20,
                color: '#999',
                padding: [0, 0, -20, 10]
              }
            }
          },
          data: [{
            value: 92
          }]
        }]
      }
      qualityChart.setOption(option)
    }

    const initActivityChart = () => {
      if (!activityChartRef.value) return
      
      activityChart = echarts.init(activityChartRef.value)
      updateActivityChart()
    }

    const updateActivityChart = () => {
      if (!activityChart) return
      
      let xAxisData, seriesData
      
      switch (activityType.value) {
        case 'hour':
          xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
          seriesData = [2, 1, 0, 0, 0, 1, 3, 8, 12, 15, 18, 22, 25, 28, 24, 20, 18, 15, 12, 8, 6, 4, 3, 2]
          break
        case 'weekday':
          xAxisData = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
          seriesData = [85, 92, 88, 95, 90, 45, 35]
          break
        case 'month':
          xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
          seriesData = [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330]
          break
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
          name: '活跃度',
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
      activityChart.setOption(option)
    }

    const loadDashboardData = async () => {
      try {
        loading.commits = true
        loading.mergeRequests = true
        loading.quality = true
        loading.activity = true
        loading.activities = true

        // 获取仪表盘数据
        const params = {
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0]
        }
        
        const response = await getDashboardData(params)
        
        if (response && response.data) {
          const data = response.data
          
          // 更新统计数据
          stats.value = [
            {
              title: '总提交数',
              value: data.total_commits || '0',
              change: data.commits_change || '0%',
              changeType: data.commits_change?.startsWith('+') ? 'positive' : data.commits_change?.startsWith('-') ? 'negative' : 'neutral',
              changeIcon: data.commits_change?.startsWith('+') ? 'el-icon-arrow-up' : data.commits_change?.startsWith('-') ? 'el-icon-arrow-down' : 'el-icon-minus',
              icon: 'el-icon-document',
              gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            },
            {
              title: '合并请求',
              value: data.total_merge_requests || '0',
              change: data.merge_requests_change || '0%',
              changeType: data.merge_requests_change?.startsWith('+') ? 'positive' : data.merge_requests_change?.startsWith('-') ? 'negative' : 'neutral',
              changeIcon: data.merge_requests_change?.startsWith('+') ? 'el-icon-arrow-up' : data.merge_requests_change?.startsWith('-') ? 'el-icon-arrow-down' : 'el-icon-minus',
              icon: 'el-icon-connection',
              gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
            },
            {
              title: '代码质量',
              value: data.code_quality_score || '0',
              change: data.quality_change || '0%',
              changeType: data.quality_change?.startsWith('+') ? 'positive' : data.quality_change?.startsWith('-') ? 'negative' : 'neutral',
              changeIcon: data.quality_change?.startsWith('+') ? 'el-icon-arrow-up' : data.quality_change?.startsWith('-') ? 'el-icon-arrow-down' : 'el-icon-minus',
              icon: 'el-icon-trophy',
              gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
            },
            {
              title: '活跃仓库',
              value: data.active_repositories || '0',
              change: data.repositories_change || '0%',
              changeType: data.repositories_change?.startsWith('+') ? 'positive' : data.repositories_change?.startsWith('-') ? 'negative' : 'neutral',
              changeIcon: data.repositories_change?.startsWith('+') ? 'el-icon-arrow-up' : data.repositories_change?.startsWith('-') ? 'el-icon-arrow-down' : 'el-icon-minus',
              icon: 'el-icon-folder',
              gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
            }
          ]
          
          // 更新最近活动数据
          recentActivities.value = data.recent_activities || []
        }
        
      } catch (error) {
        console.error('加载仪表盘数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
        
        // 使用默认数据
        recentActivities.value = [
          {
            id: 1,
            author: '系统',
            action: '暂无数据',
            target: '请检查后端服务',
            type: 'info',
            timestamp: new Date(),
            avatar: ''
          }
        ]
      } finally {
        loading.commits = false
        loading.mergeRequests = false
        loading.quality = false
        loading.activity = false
        loading.activities = false
      }
    }

    const refreshActivities = () => {
      loadDashboardData()
    }

    const goToPage = (path) => {
      router.push(path)
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time
      
      if (diff < 1000 * 60) {
        return '刚刚'
      } else if (diff < 1000 * 60 * 60) {
        return `${Math.floor(diff / (1000 * 60))}分钟前`
      } else if (diff < 1000 * 60 * 60 * 24) {
        return `${Math.floor(diff / (1000 * 60 * 60))}小时前`
      } else {
        return time.toLocaleDateString()
      }
    }

    const getActivityTagType = (type) => {
      const typeMap = {
        commit: 'primary',
        merge_request: 'warning',
        merge: 'success',
        issue: 'info'
      }
      return typeMap[type] || 'info'
    }

    // 监听器
    watch(activityType, () => {
      updateActivityChart()
    })

    watch(commitPeriod, async () => {
      // 重新加载提交数据
      await initCommitChart()
    })

    // 生命周期
    onMounted(async () => {
      // 等待一小段时间确保Token完全设置
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 先加载基础数据
      await loadDashboardData()
      
      // 等待DOM更新后再初始化图表
      await nextTick()
      
      // 串行初始化图表，避免并发API调用导致Token冲突
      try {
        await initCommitChart()
        await initMergeRequestChart()
        initQualityChart()
        initActivityChart()
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
          commitChart?.resize()
          mergeRequestChart?.resize()
          qualityChart?.resize()
          activityChart?.resize()
        })
      } catch (error) {
        console.error('图表初始化失败:', error)
        ElMessage.warning('部分图表加载失败，请刷新页面重试')
      }
    })

    return {
      commitChartRef,
      mergeRequestChartRef,
      qualityChartRef,
      activityChartRef,
      loading,
      commitPeriod,
      activityType,
      recentActivities,
      stats,
      refreshActivities,
      goToPage,
      formatTime,
      getActivityTagType
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
.dashboard {
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

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  border-radius: 12px;
  color: #fff;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    transform: translate(30px, -30px);
  }
  
  .stat-icon {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 32px;
    opacity: 0.3;
  }
  
  .stat-content {
    position: relative;
    z-index: 1;
    
    .stat-value {
      font-size: 36px;
      font-weight: bold;
      margin-bottom: 8px;
    }
    
    .stat-title {
      font-size: 14px;
      opacity: 0.9;
      margin-bottom: 8px;
    }
    
    .stat-change {
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 4px;
      
      &.positive {
        color: rgba(255, 255, 255, 0.9);
      }
      
      &.negative {
        color: rgba(255, 255, 255, 0.7);
      }
      
      &.neutral {
        color: rgba(255, 255, 255, 0.8);
      }
    }
  }
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
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

.activity-card {
  .activity-list {
    max-height: 400px;
    overflow-y: auto;
    
    .activity-item {
      display: flex;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid $border-color-lighter;
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-avatar {
        margin-right: 12px;
      }
      
      .activity-content {
        flex: 1;
        
        .activity-title {
          font-size: 14px;
          color: $text-color;
          margin-bottom: 4px;
        }
        
        .activity-time {
          font-size: 12px;
          color: $text-color-secondary;
        }
      }
      
      .activity-type {
        margin-left: 12px;
      }
    }
    
    .empty-state {
      text-align: center;
      padding: 40px 0;
      color: $text-color-secondary;
      
      i {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
      }
      
      p {
        font-size: 14px;
      }
    }
  }
}

.quick-actions-card {
  .quick-actions {
    .action-item {
      display: flex;
      align-items: center;
      padding: 16px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      &:hover {
        background: rgba($primary-color, 0.05);
        transform: translateX(4px);
      }
      
      .action-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba($primary-color, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        
        i {
          font-size: 18px;
          color: $primary-color;
        }
      }
      
      .action-content {
        .action-title {
          font-size: 14px;
          font-weight: 500;
          color: $text-color;
          margin-bottom: 4px;
        }
        
        .action-desc {
          font-size: 12px;
          color: $text-color-secondary;
        }
      }
    }
  }
}

@include respond-to('mobile') {
  .dashboard {
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
        font-size: 28px;
      }
    }
  }
  
  .charts-row {
    margin-bottom: 16px;
  }
  
  .chart-container {
    height: 250px !important;
  }
}
</style>