<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>情绪趋势分析</h2>
        <p>查看情绪变化趋势和统计概况</p>
      </div>
      <el-radio-group v-model="days" size="small" @change="loadData">
        <el-radio-button :value="7">近 7 天</el-radio-button>
        <el-radio-button :value="30">近 30 天</el-radio-button>
      </el-radio-group>
    </div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-label">总识别次数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value negative">{{ negativePercent }}%</div>
          <div class="stat-label">负面情绪占比</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value" :class="warnCount > 0 ? 'danger' : ''">{{ warnCount }}</div>
          <div class="stat-label">产生预警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ dayCount }}</div>
          <div class="stat-label">识别天数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>情绪趋势</template>
          <div ref="lineChartRef" style="height: 360px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>情绪分布</template>
          <div ref="pieChartRef" style="height: 300px"></div>
          <el-divider />
          <div class="emotion-summary">
            <div class="summary-item" v-for="item in emotionRank" :key="item.emotion">
              <span class="dot" :style="{ background: emotionColor(item.emotion) }"></span>
              <span class="name">{{ emotionLabel(item.emotion) }}</span>
              <span class="count">{{ item.count }} 次</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import http from '@/api/http'
import * as echarts from 'echarts'

const days = ref(7)
const totalCount = ref(0)
const negativePercent = ref(0)
const warnCount = ref(0)
const dayCount = ref(0)
const emotionRank = ref([])

const lineChartRef = ref(null)
const pieChartRef = ref(null)
let lineChart = null
let pieChart = null

const emotionConfig = {
  happy: { label: '开心', color: '#67C23A' },
  sad: { label: '悲伤', color: '#409EFF' },
  angry: { label: '愤怒', color: '#F56C6C' },
  fear: { label: '恐惧', color: '#E6A23C' },
  disgust: { label: '厌恶', color: '#A0522D' },
  surprise: { label: '惊讶', color: '#FF69B4' },
  neutral: { label: '平静', color: '#909399' },
}

const negativeEmotions = ['sad', 'angry', 'fear', 'disgust']

const emotionLabel = (value) => emotionConfig[value]?.label || value
const emotionColor = (value) => emotionConfig[value]?.color || '#999'

const loadData = async () => {
  const [trendRes, warnRes] = await Promise.all([
    http.get('/stats/student/trend', { params: { days: days.value } }),
    http.get('/warnings/my'),
  ])

  const raw = trendRes.data || []
  const warnData = warnRes.data || []
  warnCount.value = warnData.length

  // Process trend data
  const dateSet = new Set()
  const emotionGroups = {}
  let total = 0
  let negativeTotal = 0

  raw.forEach((item) => {
    dateSet.add(item.date)
    if (!emotionGroups[item.emotion]) emotionGroups[item.emotion] = {}
    emotionGroups[item.emotion][item.date] = item.count
    total += item.count
    if (negativeEmotions.includes(item.emotion)) negativeTotal += item.count
  })

  totalCount.value = total
  dayCount.value = dateSet.size
  negativePercent.value = total > 0 ? Math.round((negativeTotal / total) * 100) : 0

  // Emotion ranking
  emotionRank.value = Object.entries(emotionGroups)
    .map(([emotion, dates]) => ({
      emotion,
      count: Object.values(dates).reduce((a, b) => a + b, 0),
    }))
    .sort((a, b) => b.count - a.count)

  const sortedDates = [...dateSet].sort()

  // Build series for each emotion
  const allEmotions = Object.keys(emotionConfig)
  const series = allEmotions
    .filter((em) => emotionGroups[em])
    .map((em) => ({
      name: emotionConfig[em].label,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2 },
      itemStyle: { color: emotionConfig[em].color },
      data: sortedDates.map((d) => emotionGroups[em]?.[d] || 0),
    }))

  nextTick(() => {
    renderLineChart(sortedDates, series)
    renderPieChart()
  })
}

const renderLineChart = (dates, series) => {
  if (lineChart) lineChart.dispose()
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const date = params[0].axisValue
        let html = `<strong>${date}</strong><br/>`
        params.forEach((p) => {
          if (p.value > 0) {
            html += `${p.marker} ${p.seriesName}: ${p.value} 次<br/>`
          }
        })
        return html
      },
    },
    legend: {
      data: series.map((s) => s.name),
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
    },
    grid: { left: 40, right: 20, top: 20, bottom: 50 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      name: '次数',
    },
    series,
  })
}

const renderPieChart = () => {
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(pieChartRef.value)
  const data = emotionRank.value
    .filter((item) => item.count > 0)
    .map((item) => ({
      name: emotionLabel(item.emotion),
      value: item.count,
      itemStyle: { color: emotionColor(item.emotion) },
    }))
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    series: {
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14 },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.2)' },
      },
    },
  })
}

onMounted(loadData)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0 0 6px;
}
.page-header p {
  margin: 0;
  color: #909399;
}
.stat-row {
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}
.stat-value.negative {
  color: #E6A23C;
}
.stat-value.danger {
  color: #F56C6C;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.emotion-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.summary-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  flex-shrink: 0;
}
.name {
  flex: 1;
  color: #606266;
}
.count {
  color: #909399;
}
</style>
