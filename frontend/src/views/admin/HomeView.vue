<template>
  <div class="page admin-home">
    <PageHeader
      eyebrow="管理首页"
      title="基于物联网数据分析的心理健康监测系统概览"
      description="集中查看学生规模、今日识别和待处理风险，辅助教师快速判断当前工作重点。"
      tone="admin"
    >
      <template #actions>
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <div class="stats-grid three">
      <MetricCard label="学生总数" :value="overview.student_count ?? 0" unit="人" caption="已注册学生账号数量" accent="sky" />
      <MetricCard label="今日识别次数" :value="overview.today_records ?? 0" unit="次" caption="当天产生的检测记录" accent="teal" />
      <MetricCard label="待处理中高风险" :value="overview.pending_warnings ?? 0" unit="条" caption="需要教师跟进的预警" accent="danger" />
    </div>

    <div class="dashboard-grid">
      <ChartFrame title="情绪分布" description="全平台识别记录按情绪类别汇总">
        <div v-if="distribution.length" ref="distributionChartRef" class="chart-box large"></div>
        <el-empty v-else description="暂无情绪分布数据" />
      </ChartFrame>

      <section class="business-panel">
        <div class="panel-title-row">
          <div>
            <h2>分布明细</h2>
            <p>用于核对图表中的情绪统计次数</p>
          </div>
        </div>
        <el-empty v-if="!distribution.length" description="暂无情绪分布数据" />
        <div v-else class="table-scroll">
          <el-table v-loading="loading" :data="distribution" stripe>
            <el-table-column prop="emotion" label="情绪" min-width="120">
              <template #default="{ row }">
                <StatusBadge :type="emotionType(row.emotion)" :label="emotionLabel(row.emotion)" />
              </template>
            </el-table-column>
            <el-table-column prop="count" label="次数" min-width="120" />
          </el-table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import ChartFrame from '@/components/chart/ChartFrame.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { emotionColor, emotionLabel, emotionType } from '@/utils/presentation'
import http from '@/api/http'

const loading = ref(false)
const overview = ref({})
const distribution = ref([])
const distributionChartRef = ref(null)
let distributionChart = null

const loadData = async () => {
  loading.value = true
  try {
    const [overviewRes, distributionRes] = await Promise.all([
      http.get('/stats/admin/overview'),
      http.get('/stats/admin/emotion-distribution'),
    ])
    overview.value = overviewRes.data || {}
    distribution.value = distributionRes.data || []
    await nextTick()
    renderDistribution()
  } finally {
    loading.value = false
  }
}

function renderDistribution() {
  if (!distributionChartRef.value || !distribution.value.length) return
  if (!distributionChart) distributionChart = echarts.init(distributionChartRef.value)
  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '50%'],
        label: { color: '#3d524d' },
        data: distribution.value.map((item) => ({
          name: emotionLabel(item.emotion),
          value: item.count,
          itemStyle: { color: emotionColor(item.emotion) },
        })),
      },
    ],
  }, true)
}

function resizeChart() {
  distributionChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  distributionChart?.dispose()
})
</script>

<style scoped>
.admin-home {
  display: grid;
  gap: var(--mh-space-4);
}

.chart-box.large {
  height: 360px;
}
</style>
