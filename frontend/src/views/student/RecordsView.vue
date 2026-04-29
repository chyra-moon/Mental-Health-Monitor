<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>历史记录</h2>
        <p>查看最近 50 次识别与视频分析结果</p>
      </div>
      <el-button :icon="RefreshRight" type="primary" @click="loadRecords" :loading="loading">刷新</el-button>
    </div>

    <div v-if="records.length > 0" class="chart-grid">
      <div class="chart-panel">
        <div class="chart-title">情绪分布</div>
        <div ref="emotionChartRef" class="chart-box" />
      </div>
      <div class="chart-panel">
        <div class="chart-title">风险分布</div>
        <div ref="riskChartRef" class="chart-box" />
      </div>
      <div class="chart-panel">
        <div class="chart-title">趋势</div>
        <div ref="trendChartRef" class="chart-box" />
      </div>
    </div>

    <el-card class="records-card" shadow="never">
      <el-empty v-if="!loading && records.length === 0" description="暂无识别记录" />
      <el-table v-else v-loading="loading" :data="pagedRecords" stripe style="width: 100%">
        <el-table-column prop="created_at" label="识别时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="sourceType(row.source_type)" size="small">{{ sourceLabel(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dominant_emotion" label="主要情绪" min-width="120">
          <template #default="{ row }">
            <el-tag :type="emotionType(row.dominant_emotion)">
              {{ emotionLabel(row.dominant_emotion) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" min-width="120">
          <template #default="{ row }">
            {{ row.confidence == null ? '-' : `${(row.confidence * 100).toFixed(1)}%` }}
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" min-width="120">
          <template #default="{ row }">
            <el-tag :type="riskType(row.risk_level)">
              {{ riskLabel(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="补充信息" min-width="220">
          <template #default="{ row }">
            <span v-if="row.source_type === 'video'">
              {{ row.analyzed_frames || 0 }} / {{ row.total_frames || 0 }} 帧，负面 {{ formatPercent(row.negative_ratio) }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
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
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
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

const emotionMap = {
  happy: { label: '开心', type: 'success', color: '#67c23a' },
  sad: { label: '悲伤', type: 'primary', color: '#409eff' },
  angry: { label: '愤怒', type: 'danger', color: '#f56c6c' },
  fear: { label: '恐惧', type: 'warning', color: '#e6a23c' },
  disgust: { label: '厌恶', type: 'warning', color: '#909399' },
  surprise: { label: '惊讶', type: 'info', color: '#b37feb' },
  neutral: { label: '平静', type: 'success', color: '#67c8b9' },
}

const riskMap = {
  low: { label: '低风险', type: 'success', color: '#67c23a' },
  medium: { label: '中风险', type: 'warning', color: '#e6a23c' },
  high: { label: '高风险', type: 'danger', color: '#f56c6c' },
}

const emotionKeys = Object.keys(emotionMap)
const riskKeys = ['low', 'medium', 'high']
const negativeEmotions = ['sad', 'angry', 'fear', 'disgust']

const emotionCounts = computed(() => countBy(records.value, 'dominant_emotion', emotionKeys))
const riskCounts = computed(() => countBy(records.value, 'risk_level', riskKeys))
const pagedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return records.value.slice(start, start + pageSize.value)
})

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await http.get('/records/my')
    records.value = res.data || []
    currentPage.value = 1
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function countBy(items, field, keys) {
  const counts = Object.fromEntries(keys.map((key) => [key, 0]))
  items.forEach((item) => {
    if (counts[item[field]] !== undefined) counts[item[field]] += 1
  })
  return counts
}

function buildTrendData() {
  const groups = {}
  records.value.forEach((item) => {
    const date = item.created_at ? item.created_at.slice(0, 10) : ''
    if (!date) return
    if (!groups[date]) groups[date] = { total: 0, negative: 0 }
    groups[date].total += 1
    if (negativeEmotions.includes(item.dominant_emotion) || item.risk_level !== 'low') {
      groups[date].negative += 1
    }
  })
  const dates = Object.keys(groups).sort()
  return {
    dates,
    total: dates.map((date) => groups[date].total),
    negative: dates.map((date) => groups[date].negative),
  }
}

function renderCharts() {
  if (!emotionChartRef.value || records.value.length === 0) return
  if (!emotionChart) emotionChart = echarts.init(emotionChartRef.value)
  if (!riskChart) riskChart = echarts.init(riskChartRef.value)
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)

  emotionChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['45%', '72%'],
      data: emotionKeys
        .filter((key) => emotionCounts.value[key] > 0)
        .map((key) => ({
          name: emotionLabel(key),
          value: emotionCounts.value[key],
          itemStyle: { color: emotionMap[key].color },
        })),
    }],
  }, true)

  riskChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 32, right: 12, top: 20, bottom: 28 },
    xAxis: { type: 'category', data: riskKeys.map(riskLabel) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      type: 'bar',
      data: riskKeys.map((key) => ({
        value: riskCounts.value[key],
        itemStyle: { color: riskMap[key].color },
      })),
      barWidth: 28,
    }],
  }, true)

  const trend = buildTrendData()
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['记录数', '风险信号'], top: 0 },
    grid: { left: 36, right: 12, top: 36, bottom: 28 },
    xAxis: { type: 'category', data: trend.dates },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      { name: '记录数', type: 'line', smooth: true, data: trend.total, itemStyle: { color: '#409eff' } },
      { name: '风险信号', type: 'line', smooth: true, data: trend.negative, itemStyle: { color: '#f56c6c' } },
    ],
  }, true)
}

function resizeCharts() {
  emotionChart?.resize()
  riskChart?.resize()
  trendChart?.resize()
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
const formatPercent = (value) => (value == null ? '-' : `${(value * 100).toFixed(1)}%`)
const emotionLabel = (value) => emotionMap[value]?.label || value || '-'
const emotionType = (value) => emotionMap[value]?.type || 'info'
const riskLabel = (value) => riskMap[value]?.label || value || '-'
const riskType = (value) => riskMap[value]?.type || 'info'
const sourceLabel = (row) => row.source_label || (row.source_type === 'video' ? '视频分析' : '图片识别')
const sourceType = (value) => (value === 'video' ? 'warning' : 'primary')

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
.page {
  max-width: 100%;
  overflow-x: hidden;
}

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

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.chart-panel {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fff;
  padding: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.chart-box {
  height: 220px;
}

.records-card {
  overflow: hidden;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 16px;
  flex-wrap: wrap;
}

.page-total {
  color: #7d8fb3;
  font-size: 13px;
}

.text-muted {
  color: #909399;
}

@media (max-width: 960px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }

  .pagination-bar {
    justify-content: flex-end;
  }
}
</style>
