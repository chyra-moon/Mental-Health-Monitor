import { onUnmounted, shallowRef } from 'vue'
import * as echarts from 'echarts'

export function useEcharts(elRef) {
  const chartInstance = shallowRef(null)

  function render(options) {
    if (!elRef.value) return
    if (!chartInstance.value) {
      chartInstance.value = echarts.init(elRef.value)
    }
    chartInstance.value.setOption(options, true)
  }

  function resize() {
    if (chartInstance.value) {
      chartInstance.value.resize()
    }
  }

  onUnmounted(() => {
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
    }
  })

  return {
    render,
    resize,
    instance: chartInstance
  }
}
