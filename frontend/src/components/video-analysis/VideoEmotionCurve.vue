<template>
  <el-card class="chart-card" shadow="never">
    <template #header>
      <div class="chart-title">会话情绪波动曲线</div>
    </template>
    <div v-if="frameResults.length" ref="chartRef" class="chart-box" :style="{ height: chartHeight }"></div>
    <div v-else class="chart-empty" :style="{ height: chartHeight }">
      等待首帧分析数据
    </div>
  </el-card>
</template>

<script setup>
import { computed, nextTick, ref, onMounted, onUnmounted, watch } from 'vue'
import { useEcharts } from '@/composables/useEcharts'
import { emotionLabel, emotionColor } from '@/domain/mentalHealth'

const props = defineProps({
  frameResults: {
    type: Array,
    required: true
  },
  height: {
    type: [Number, String],
    default: 280
  }
})

const chartRef = ref(null)
const { render, resize } = useEcharts(chartRef)
const chartHeight = computed(() => (typeof props.height === 'number' ? `${props.height}px` : props.height))

async function updateChart() {
  if (!props.frameResults.length) return
  await nextTick()
  if (!chartRef.value) return

  // Sort frames by index
  const sortedFrames = [...props.frameResults].sort((a, b) => a.frame_index - b.frame_index)
  
  const xData = sortedFrames.map(f => `${f.frame_index + 1}`)
  const labelInterval = Math.max(0, Math.ceil(sortedFrames.length / 8) - 1)
  
  // Track key emotions: happy, neutral, sad, angry, fear
  const targetEmotions = ['happy', 'neutral', 'sad', 'angry', 'fear']
  
  const series = targetEmotions.map(emotion => {
    return {
      name: emotionLabel(emotion),
      type: 'line',
      smooth: true,
      symbol: 'none',
      emphasis: { focus: 'series' },
      lineStyle: { width: 2 },
      itemStyle: { color: emotionColor(emotion) },
      data: sortedFrames.map(f => {
        if (!f.emotion_scores) return 0
        return Number(((f.emotion_scores[emotion] || 0) * 100).toFixed(1))
      })
    }
  })

  render({
    tooltip: {
      trigger: 'axis',
      confine: true,
      formatter: (params) => {
        let html = `<strong>第 ${params[0].axisValue} 帧</strong><br/>`
        params.forEach(item => {
          html += `${item.marker} ${item.seriesName}: ${item.value}%<br/>`
        })
        return html
      }
    },
    legend: {
      data: targetEmotions.map(emotionLabel),
      top: 0,
      itemWidth: 12,
      itemHeight: 8,
      textStyle: {
        color: '#52525b',
        fontSize: 11
      }
    },
    grid: { left: 48, right: 24, top: 46, bottom: 36 },
    xAxis: {
      type: 'category',
      data: xData,
      boundaryGap: false,
      name: '帧序号',
      nameLocation: 'middle',
      nameGap: 24,
      axisLabel: {
        interval: labelInterval,
        color: '#71717a',
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '得分概率',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        color: '#71717a',
        fontSize: 11
      }
    },
    series
  })

  await nextTick()
  resize()
}

watch(() => [props.frameResults, props.height], updateChart, { deep: true })

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

.chart-empty {
  width: 100%;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--mh-muted);
  font-size: 12px;
  border: 1px dashed var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: #fbfbfc;
}
</style>
