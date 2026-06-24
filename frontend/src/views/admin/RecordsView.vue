<template>
  <div class="page records-page">
    <PageHeader
      eyebrow="记录管理"
      title="学生识别记录"
      description="查看学生情绪识别与视频分析历史，辅助管理员进行整体研判。"
      tone="admin"
    >
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadRecords" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <div v-if="records.length > 0" class="chart-grid">
      <ChartFrame title="情绪分布" description="全部记录中的情绪类别构成">
        <div ref="emotionChartRef" class="chart-box" />
      </ChartFrame>
      <ChartFrame title="风险分布" description="低、中、高风险记录数量">
        <div ref="riskChartRef" class="chart-box" />
      </ChartFrame>
      <ChartFrame title="记录趋势" description="按日期汇总记录与风险信号">
        <div ref="trendChartRef" class="chart-box" />
      </ChartFrame>
    </div>

    <section class="table-panel">
      <div class="panel-title-row">
        <div>
          <h2>记录明细</h2>
          <p>包含学生信息、识别来源、主要情绪、置信度和风险等级</p>
        </div>
      </div>

      <el-empty v-if="!loading && records.length === 0" description="暂无识别记录" />
      <div v-else class="table-scroll">
        <el-table v-loading="loading" :data="pagedRecords" stripe style="width: 100%">
          <el-table-column prop="created_at" label="识别时间" min-width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="类型" width="120" align="center">
            <template #default="{ row }">
              <StatusBadge :type="sourceBadgeType(row.source_type)" :label="sourceLabel(row)" />
            </template>
          </el-table-column>
          <el-table-column prop="real_name" label="学生姓名" min-width="120" />
          <el-table-column prop="username" label="用户名" min-width="140" />
          <el-table-column prop="dominant_emotion" label="主要情绪" min-width="120">
            <template #default="{ row }">
              <StatusBadge :type="emotionType(row.dominant_emotion)" :label="emotionLabel(row.dominant_emotion)" />
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" min-width="120">
            <template #default="{ row }">
              {{ row.confidence == null ? '-' : `${(row.confidence * 100).toFixed(1)}%` }}
            </template>
          </el-table-column>
          <el-table-column prop="risk_level" label="风险等级" min-width="120">
            <template #default="{ row }">
              <StatusBadge :type="row.risk_level" :label="riskLabel(row.risk_level)" />
            </template>
          </el-table-column>
          <el-table-column label="补充信息" min-width="240">
            <template #default="{ row }">
              <span v-if="row.source_type === 'video'">
                {{ row.analyzed_frames || 0 }} / {{ row.total_frames || 0 }} 帧，负面 {{ formatPercent(row.negative_ratio) }}
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="records.length > pageSize" class="pagination-bar">
        <span class="page-total">共 {{ records.length }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 10, 15, 20]"
          :total="records.length"
          background
          layout="sizes, prev, pager, next, jumper"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import ChartFrame from '@/components/chart/ChartFrame.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import {
  countBy,
  emotionColor,
  emotionKeys,
  emotionLabel,
  emotionType,
  formatPercent,
  formatTime,
  negativeEmotions,
  riskColor,
  riskKeys,
  riskLabel,
  sourceBadgeType,
  sourceLabel,
} from '@/utils/presentation'
import http from '@/api/http'

const loading = ref(false)
const records = ref([])
const currentPage = ref(1)
const pageSize = ref(6)
const emotionChartRef = ref(null)
const riskChartRef = ref(null)
const trendChartRef = ref(null)
let emotionChart = null
let riskChart = null
let trendChart = null

const emotionCounts = computed(() => countBy(records.value, 'dominant_emotion', emotionKeys))
const riskCounts = computed(() => countBy(records.value, 'risk_level', riskKeys))
const pagedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return records.value.slice(start, start + pageSize.value)
})

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await http.get('/records/admin/all')
    records.value = res.data || []
    currentPage.value = 1
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function buildTrendData() {
  const groups = {}
  records.value.forEach((item) => {
    const date = item.created_at ? item.created_at.slice(0, 10) : ''
    if (!date) return
    if (!groups[date]) groups[date] = { total: 0, risk: 0 }
    groups[date].total += 1
    if (negativeEmotions.includes(item.dominant_emotion) || item.risk_level !== 'low') {
      groups[date].risk += 1
    }
  })
  const dates = Object.keys(groups).sort()
  return {
    dates,
    total: dates.map((date) => groups[date].total),
    risk: dates.map((date) => groups[date].risk),
  }
}

function renderCharts() {
  if (!emotionChartRef.value || records.value.length === 0) return
  if (!emotionChart) emotionChart = echarts.init(emotionChartRef.value)
  if (!riskChart) riskChart = echarts.init(riskChartRef.value)
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)

  emotionChart.setOption({
    color: emotionKeys.map(emotionColor),
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['48%', '72%'],
      label: { color: '#3d524d' },
      data: emotionKeys
        .filter((key) => emotionCounts.value[key] > 0)
        .map((key) => ({
          name: emotionLabel(key),
          value: emotionCounts.value[key],
          itemStyle: { color: emotionColor(key) },
        })),
    }],
  }, true)

  riskChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 36, right: 12, top: 18, bottom: 30 },
    xAxis: { type: 'category', data: riskKeys.map(riskLabel), axisLabel: { color: '#6e817b' } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#6e817b' } },
    series: [{
      type: 'bar',
      data: riskKeys.map((key) => ({
        value: riskCounts.value[key],
        itemStyle: { color: riskColor(key), borderRadius: [4, 4, 0, 0] },
      })),
      barWidth: 30,
    }],
  }, true)

  const trend = buildTrendData()
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['记录数', '风险信号'], top: 0, textStyle: { color: '#6e817b' } },
    grid: { left: 40, right: 12, top: 38, bottom: 30 },
    xAxis: { type: 'category', data: trend.dates, axisLabel: { color: '#6e817b' } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#6e817b' } },
    series: [
      { name: '记录数', type: 'line', smooth: true, data: trend.total, itemStyle: { color: '#337f95' } },
      { name: '风险信号', type: 'line', smooth: true, data: trend.risk, itemStyle: { color: '#b95542' } },
    ],
  }, true)
}

function resizeCharts() {
  emotionChart?.resize()
  riskChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  loadRecords()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  emotionChart?.dispose()
  riskChart?.dispose()
  trendChart?.dispose()
})

watch(records, () => nextTick(renderCharts))
watch(pageSize, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.records-page {
  display: grid;
  gap: var(--mh-space-4);
}
</style>
