<template>
  <div class="page trend-page">
    <PageHeader
      eyebrow="趋势分析"
      title="情绪变化趋势"
      description="按近 7 天或近 30 天查看情绪统计概况，帮助观察近期状态波动。"
    >
      <template #actions>
        <el-radio-group v-model="days" size="small" @change="loadData">
          <el-radio-button :label="7">近 7 天</el-radio-button>
          <el-radio-button :label="30">近 30 天</el-radio-button>
        </el-radio-group>
      </template>
    </PageHeader>

    <div class="stats-grid">
      <MetricCard label="总识别次数" :value="totalCount" unit="次" caption="所选时间范围内的记录总量" accent="teal" />
      <MetricCard label="负面情绪占比" :value="negativePercent" unit="%" caption="悲伤、愤怒、恐惧、厌恶占比" accent="warm" />
      <MetricCard label="预警数量" :value="warnCount" unit="条" caption="当前账号关联预警" :accent="warnCount > 0 ? 'danger' : 'green'" />
      <MetricCard label="覆盖天数" :value="dayCount" unit="天" caption="有检测数据的日期数量" accent="sky" />
    </div>

    <div class="trend-grid">
      <ChartFrame title="情绪趋势" description="不同情绪在日期维度上的次数变化">
        <div v-if="totalCount" ref="lineChartRef" class="chart-box large"></div>
        <el-empty v-else description="暂无趋势数据" />
      </ChartFrame>

      <ChartFrame title="情绪分布" description="按识别次数排序展示情绪构成">
        <div v-if="totalCount" ref="pieChartRef" class="chart-box pie-box"></div>
        <el-empty v-else description="暂无分布数据" />
        <div v-if="emotionRank.length" class="emotion-summary">
          <div v-for="item in emotionRank" :key="item.emotion" class="summary-item">
            <span class="dot" :style="{ background: emotionColor(item.emotion) }"></span>
            <span class="name">{{ emotionLabel(item.emotion) }}</span>
            <span class="count">{{ item.count }} 次</span>
          </div>
        </div>
      </ChartFrame>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import ChartFrame from '@/components/chart/ChartFrame.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { emotionColor, emotionKeys, emotionLabel, negativeEmotions } from '@/utils/presentation'
import http from '@/api/http'

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

async function loadData() {
  const [trendRes, warnRes] = await Promise.all([
    http.get('/stats/student/trend', { params: { days: days.value } }),
    http.get('/warnings/my'),
  ])

  const raw = trendRes.data || []
  const warnings = warnRes.data || []
  warnCount.value = warnings.length

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

  emotionRank.value = Object.entries(emotionGroups)
    .map(([emotion, dates]) => ({
      emotion,
      count: Object.values(dates).reduce((sum, count) => sum + count, 0),
    }))
    .sort((a, b) => b.count - a.count)

  const sortedDates = [...dateSet].sort()
  const series = emotionKeys
    .filter((emotion) => emotionGroups[emotion])
    .map((emotion) => ({
      name: emotionLabel(emotion),
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2 },
      itemStyle: { color: emotionColor(emotion) },
      data: sortedDates.map((date) => emotionGroups[emotion]?.[date] || 0),
    }))

  await nextTick()
  renderLineChart(sortedDates, series)
  renderPieChart()
}

function renderLineChart(dates, series) {
  if (!lineChartRef.value) return
  if (lineChart) lineChart.dispose()
  lineChart = echarts.init(lineChartRef.value)

  lineChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const date = params[0].axisValue
        let html = `<strong>${date}</strong><br/>`
        params.forEach((item) => {
          if (item.value > 0) {
            html += `${item.marker} ${item.seriesName}: ${item.value} 次<br/>`
          }
        })
        return html
      },
    },
    legend: {
      data: series.map((item) => item.name),
      bottom: 0,
      textStyle: { color: '#6e817b' },
    },
    grid: { left: 44, right: 20, top: 24, bottom: 54 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#6e817b' },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      name: '次数',
      axisLabel: { color: '#6e817b' },
    },
    series,
  })
}

function renderPieChart() {
  if (!pieChartRef.value) return
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
    series: [
      {
        type: 'pie',
        radius: ['42%', '70%'],
        center: ['50%', '45%'],
        data,
        label: { show: false },
      },
    ],
  })
}

function resizeCharts() {
  lineChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  if (lineChart) {
    lineChart.dispose()
    lineChart = null
  }
  if (pieChart) {
    pieChart.dispose()
    pieChart = null
  }
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
.trend-page {
  display: grid;
  gap: var(--mh-space-4);
}

.trend-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
  gap: var(--mh-space-4);
}

.chart-box.large {
  height: 380px;
}

.pie-box {
  height: 300px;
}

.emotion-summary {
  display: grid;
  gap: 10px;
  padding-top: var(--mh-space-3);
  border-top: 1px solid var(--mh-line);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--mh-text);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex: none;
}

.name {
  flex: 1;
}

.count {
  color: var(--mh-muted);
}

@media (max-width: 980px) {
  .trend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
