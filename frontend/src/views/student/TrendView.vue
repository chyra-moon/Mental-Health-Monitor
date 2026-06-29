<template>
  <div class="page trend-page">
    <PageHeader title="趋势观察" description="查看近期情绪记录、负向情绪占比和风险提醒数量">
      <template #actions>
        <el-radio-group v-model="days" size="small" aria-label="趋势时间范围" @change="loadData">
          <el-radio-button :label="7">近 7 天</el-radio-button>
          <el-radio-button :label="30">近 30 天</el-radio-button>
        </el-radio-group>
      </template>
    </PageHeader>

    <el-alert
      v-if="loadError"
      class="state-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <section class="stat-grid" v-loading="loading" aria-label="趋势统计概览">
      <el-card shadow="never" class="stat-card">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">总识别次数</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value negative">{{ negativePercent }}%</div>
        <div class="stat-label">负向情绪占比</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value" :class="warnCount > 0 ? 'danger' : ''">{{ warnCount }}</div>
        <div class="stat-label">关注提醒数量</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value">{{ dayCount }}</div>
        <div class="stat-label">覆盖天数</div>
      </el-card>
    </section>

    <div class="chart-grid">
      <el-card shadow="never" class="chart-card" v-loading="loading">
        <template #header>
          <div class="chart-heading">
            <span>情绪趋势</span>
            <small>{{ lineSummary }}</small>
          </div>
        </template>
        <div v-if="totalCount" ref="lineChartRef" class="chart-box" role="img" :aria-label="lineSummary"></div>
        <el-empty v-else description="暂无趋势数据" />
      </el-card>

      <el-card shadow="never" class="chart-card" v-loading="loading">
        <template #header>
          <div class="chart-heading">
            <span>情绪分布</span>
            <small>{{ distributionSummary }}</small>
          </div>
        </template>
        <div v-if="totalCount" ref="pieChartRef" class="chart-box pie-box" role="img" :aria-label="distributionSummary"></div>
        <el-empty v-else description="暂无分布数据" />
        <el-divider />
        <div class="emotion-summary" aria-label="情绪分布文本列表">
          <div v-for="item in emotionRank" :key="item.emotion" class="summary-item">
            <span class="color-mark" :style="{ background: emotionColor(item.emotion) }" aria-hidden="true"></span>
            <span class="name">{{ emotionLabel(item.emotion) }}</span>
            <span class="count">{{ item.count }} 次</span>
          </div>
          <span v-if="emotionRank.length === 0" class="text-muted">暂无情绪分布</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { useEcharts } from '@/composables/useEcharts'
import { getStudentTrend } from '@/api/stats'
import { listMyWarnings } from '@/api/warnings'
import { EMOTION_KEYS, EMOTION_META, NEGATIVE_EMOTIONS, emotionColor, emotionLabel } from '@/domain/mentalHealth'

const days = ref(7)
const loading = ref(false)
const loadError = ref('')
const totalCount = ref(0)
const negativePercent = ref(0)
const warnCount = ref(0)
const dayCount = ref(0)
const emotionRank = ref([])

const lineChartRef = ref(null)
const pieChartRef = ref(null)
const lineChart = useEcharts(lineChartRef)
const pieChart = useEcharts(pieChartRef)

const lineSummary = computed(() =>
  totalCount.value
    ? `${days.value} 天内共有 ${totalCount.value} 次记录，负向情绪占比 ${negativePercent.value}%`
    : '暂无趋势数据'
)
const distributionSummary = computed(() => {
  const top = emotionRank.value[0]
  return top ? `最多出现 ${emotionLabel(top.emotion)}，共 ${top.count} 次` : '暂无情绪分布数据'
})

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [trendRes, warnRes] = await Promise.all([
      getStudentTrend(days.value),
      listMyWarnings(),
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
      if (NEGATIVE_EMOTIONS.has(item.emotion)) negativeTotal += item.count
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
    const series = EMOTION_KEYS
      .filter((emotion) => emotionGroups[emotion])
      .map((emotion) => ({
        name: EMOTION_META[emotion].label,
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
  } catch (error) {
    loadError.value = error?.message || '趋势数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function renderLineChart(dates, series) {
  lineChart.render({
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
    },
    grid: { left: 40, right: 20, top: 20, bottom: 50 },
    xAxis: {
      type: 'category',
      data: dates,
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      name: '次数',
    },
    series,
  })
}

function renderPieChart() {
  const data = emotionRank.value
    .filter((item) => item.count > 0)
    .map((item) => ({
      name: emotionLabel(item.emotion),
      value: item.count,
      itemStyle: { color: emotionColor(item.emotion) },
    }))

  pieChart.render({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data,
        label: { show: false },
      },
    ],
  })
}

function resizeCharts() {
  lineChart.resize()
  pieChart.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
.trend-page {
  display: grid;
  gap: 16px;
  max-width: 100%;
  overflow-x: hidden;
}

.state-alert {
  margin-bottom: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  color: var(--mh-ink);
  font-size: 32px;
  font-weight: 800;
}

.stat-value.negative {
  color: var(--mh-warning);
}

.stat-value.danger {
  color: var(--mh-danger);
}

.stat-label {
  margin-top: 4px;
  color: var(--mh-muted);
  font-size: 13px;
}

.chart-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.85fr);
  gap: 16px;
}

.chart-card {
  min-height: 390px;
  min-width: 0;
}

.chart-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.chart-heading span {
  color: var(--mh-ink);
  font-weight: 800;
}

.chart-heading small,
.text-muted {
  color: var(--mh-muted);
  font-size: 12px;
}

.chart-box {
  width: 100%;
  height: 300px;
}

.pie-box {
  height: 260px;
}

.emotion-summary {
  display: grid;
  gap: 10px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--mh-text);
}

.color-mark {
  flex: none;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.name {
  flex: 1;
}

.count {
  color: var(--mh-muted);
}

@media (max-width: 1080px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stat-value {
    font-size: 24px;
  }

  .chart-grid {
    max-height: 660px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .chart-card {
    min-height: auto;
  }

  .chart-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .chart-box {
    height: 220px;
  }

  .pie-box {
    height: 210px;
  }
}
</style>
