<template>
  <div class="page trend-page">
    <PageHeader title="趋势观察" description="利用可视化图表分析近期情绪波动特征及负向情绪频次变化">
      <template #actions>
        <el-radio-group v-model="days" size="small" aria-label="趋势时间范围" @change="loadData">
          <el-radio-button :value="7">近 7 天</el-radio-button>
          <el-radio-button :value="30">近 30 天</el-radio-button>
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

    <!-- Layer 1: Metrics stats -->
    <section class="stat-grid" v-loading="loading">
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
        <div class="stat-label">待跟进预警</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value">{{ dayCount }}</div>
        <div class="stat-label">活跃天数</div>
      </el-card>
    </section>

    <!-- Layer 2: Main charts and analysis panel -->
    <div class="main-grid">
      <!-- Left side: ECharts trend curve -->
      <div class="left-col">
        <el-card shadow="never" class="chart-card" v-loading="loading">
          <template #header>
            <div class="chart-heading">
              <span class="card-title">情绪波动走势图</span>
            </div>
          </template>
          <div v-show="totalCount" ref="lineChartRef" class="chart-box"></div>
          <el-empty v-show="!totalCount" description="暂无趋势数据" />
        </el-card>
      </div>

      <!-- Right side: ECharts distribution & Text insights -->
      <div class="right-col">
        <el-card shadow="never" class="insight-card" v-loading="loading">
          <template #header>
            <span class="card-title">趋势特征诊断</span>
          </template>
          <div v-if="totalCount" class="insight-content">
            <!-- Mini Pie chart and Rank -->
            <div class="pie-section">
              <div ref="pieChartRef" class="mini-pie-box"></div>
              <div class="ranks-box">
                <div v-for="(item, idx) in emotionRank.slice(0, 3)" :key="item.emotion" class="rank-item">
                  <span class="color-dot" :style="{ background: emotionColor(item.emotion) }"></span>
                  <span class="rank-name">{{ emotionLabel(item.emotion) }}</span>
                  <span class="rank-count">{{ item.count }}次 ({{ getPercent(item.count) }}%)</span>
                </div>
              </div>
            </div>
            
            <el-divider />
            
            <!-- Automated Diagnosis text -->
            <div class="analysis-box">
              <div class="diagnosis-header">
                <el-icon class="diagnosis-icon"><Opportunity /></el-icon>
                <h5>自测心境评估：</h5>
              </div>
              <p class="diagnosis-text">{{ automatedDiagnosisText }}</p>
            </div>
          </div>
          <el-empty v-else description="暂无诊断数据" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { Opportunity } from '@element-plus/icons-vue'
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

const automatedDiagnosisText = computed(() => {
  if (!totalCount.value) return '暂无足够的情绪记录生成分析报告。请多使用情绪识别积累数据。'
  
  let desc = `在近 ${days.value} 天的观测期内，您共进行了 ${totalCount.value} 次情绪评测。`
  
  if (negativePercent.value >= 40) {
    desc += `负向情绪频次占比达 ${negativePercent.value}%，处于较高波动区间。曲线显示您近期可能面临较大的心理压力或睡眠困扰，建议规律作息，并在必要时点击心理测评自测，或主动预约心理中心老师倾诉。`
  } else if (negativePercent.value >= 20) {
    desc += `负向情绪频次占比为 ${negativePercent.value}%，整体状态较为平稳，但在特定时间点存在情绪起伏。建议留意近期让您感到烦躁或压力的事件，进行适当运动调节。`
  } else {
    desc += `负向情绪频次占比仅 ${negativePercent.value}%，主导心境为正面或平静，您的整体心理韧性与适应能力良好，请继续保持健康的生活作息。`
  }
  return desc
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
    
    // 只统计待处理的预警数量
    warnCount.value = warnings.filter(w => w.status !== 'handled').length

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
  } catch (error) {
    loadError.value = error?.message || '趋势数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function getPercent(count) {
  if (!totalCount.value) return 0
  return Math.round((count / totalCount.value) * 100)
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
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: dates,
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      name: '频次',
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
        radius: ['45%', '75%'],
        center: ['50%', '50%'],
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
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
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
  padding: 8px 12px;
}

.stat-value {
  color: var(--mh-ink);
  font-size: 26px;
  font-weight: 850;
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
  font-size: 12px;
  font-weight: 600;
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr);
  gap: 16px;
  flex: 1;
}

.left-col, .right-col {
  height: 100%;
}

.chart-card {
  height: 380px;
}

.insight-card {
  height: 380px;
}

.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.chart-box {
  width: 100%;
  height: 310px;
}

.insight-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.pie-section {
  display: flex;
  align-items: center;
  height: 140px;
  gap: 16px;
}

.mini-pie-box {
  width: 140px;
  height: 140px;
  flex: none;
}

.ranks-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rank-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  flex: none;
}

.rank-name {
  color: var(--mh-text);
  font-weight: 600;
  flex: 1;
}

.rank-count {
  color: var(--mh-muted);
}

.el-divider {
  margin: 12px 0;
}

.analysis-box {
  flex: 1;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  padding: 12px 16px;
  border-radius: var(--mh-radius-md);
  overflow-y: auto;
}

.diagnosis-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.diagnosis-icon {
  font-size: 16px;
  color: var(--mh-primary);
}

.diagnosis-header h5 {
  margin: 0;
  font-size: 12.5px;
  font-weight: 800;
  color: var(--mh-ink);
}

.diagnosis-text {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--mh-text);
  text-align: justify;
}

@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  .chart-card, .insight-card {
    height: auto;
  }
}
</style>
