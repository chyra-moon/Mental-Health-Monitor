<template>
  <el-card class="chart-card" shadow="never">
    <template #header>
      <div class="chart-title">会话情绪波动曲线</div>
    </template>
    <div ref="chartRef" class="chart-box"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useEcharts } from '@/composables/useEcharts'
import { emotionLabel, emotionColor } from '@/domain/mentalHealth'

const props = defineProps({
  frameResults: {
    type: Array,
    required: true
  }
})

const chartRef = ref(null)
const { render, resize } = useEcharts(chartRef)

function updateChart() {
  if (!props.frameResults.length) return

  // Sort frames by index
  const sortedFrames = [...props.frameResults].sort((a, b) => a.frame_index - b.frame_index)
  
  const xData = sortedFrames.map(f => `第 ${f.frame_index + 1} 帧`)
  
  // Track key emotions: happy, neutral, sad, angry, fear
  const targetEmotions = ['happy', 'neutral', 'sad', 'angry', 'fear']
  
  const series = targetEmotions.map(emotion => {
    return {
      name: emotionLabel(emotion),
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2 },
      itemStyle: { color: emotionColor(emotion) },
      data: sortedFrames.map(f => {
        if (!f.emotion_scores) return 0
        return Number((f.emotion_scores[emotion] || 0) * 100).toFixed(1)
      })
    }
  })

  render({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `<strong>${params[0].axisValue}</strong><br/>`
        params.forEach(item => {
          html += `${item.marker} ${item.seriesName}: ${item.value}%<br/>`
        })
        return html
      }
    },
    legend: {
      data: targetEmotions.map(emotionLabel),
      bottom: 0
    },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: xData,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '得分概率',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series
  })
}

watch(() => props.frameResults, updateChart, { deep: true })

onMounted(() => {
  updateChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.chart-card {
  height: 100%;
}
.chart-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.chart-box {
  width: 100%;
  height: 280px;
}
</style>
