<template>
  <div class="charts-grid">
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="chart-title">情绪类别占比</div>
      </template>
      <div ref="pieRef" class="chart-box"></div>
    </el-card>

    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="chart-title">风险评估分布</div>
      </template>
      <div ref="barRef" class="chart-box"></div>
    </el-card>

    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="chart-title">近况识别趋势</div>
      </template>
      <div ref="lineRef" class="chart-box"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useEcharts } from '@/composables/useEcharts'
import { emotionLabel, emotionColor, riskLabel, riskColor } from '@/domain/mentalHealth'

const props = defineProps({
  records: {
    type: Array,
    required: true
  }
})

const pieRef = ref(null)
const barRef = ref(null)
const lineRef = ref(null)

const { render: renderPie, resize: resizePie } = useEcharts(pieRef)
const { render: renderBar, resize: resizeBar } = useEcharts(barRef)
const { render: renderLine, resize: resizeLine } = useEcharts(lineRef)

function drawCharts() {
  if (!props.records.length) return

  const emotionCounts = {}
  props.records.forEach(r => {
    if (r.dominant_emotion) {
      emotionCounts[r.dominant_emotion] = (emotionCounts[r.dominant_emotion] || 0) + 1
    }
  })
  
  const pieData = Object.entries(emotionCounts).map(([emotion, count]) => ({
    name: emotionLabel(emotion),
    value: count,
    itemStyle: { color: emotionColor(emotion) }
  }))

  renderPie({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['45%', '75%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            formatter: '{b}'
          }
        },
        data: pieData
      }
    ]
  })

  const riskCounts = { low: 0, medium: 0, high: 0 }
  props.records.forEach(r => {
    if (r.risk_level && riskCounts[r.risk_level] !== undefined) {
      riskCounts[r.risk_level]++
    }
  })

  const barData = Object.entries(riskCounts).map(([level, count]) => ({
    name: riskLabel(level),
    value: count,
    itemStyle: { color: riskColor(level) }
  }))

  renderBar({
    tooltip: { trigger: 'axis', formatter: '{b}: {c} 次' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: barData.map(d => d.name)
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        type: 'bar',
        barWidth: '40%',
        data: barData
      }
    ]
  })

  const dateCounts = {}
  props.records.forEach(r => {
    if (!r.created_at) return
    const date = String(r.created_at).slice(0, 10)
    dateCounts[date] = (dateCounts[date] || 0) + 1
  })
  const dates = Object.keys(dateCounts).sort().slice(-7)
  renderLine({
    tooltip: { trigger: 'axis', formatter: '{b}: {c} 次' },
    grid: { left: 34, right: 16, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2, color: '#7c3aed' },
        itemStyle: { color: '#7c3aed' },
        areaStyle: { color: 'rgba(124, 58, 237, 0.08)' },
        data: dates.map(date => dateCounts[date])
      }
    ]
  })
}

watch(() => props.records, drawCharts, { deep: true })

onMounted(() => {
  drawCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  resizePie()
  resizeBar()
  resizeLine()
}
</script>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.chart-card {
  height: 220px;
  overflow: hidden;
}

.chart-card :deep(.el-card__body) {
  height: calc(100% - 49px);
  overflow: hidden;
  padding: 8px 12px 10px !important;
}

.chart-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.chart-box {
  width: 100%;
  height: 100%;
  min-height: 0;
}

@media (max-width: 980px) {
  .charts-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    height: auto;
  }
}

@media (max-width: 640px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
