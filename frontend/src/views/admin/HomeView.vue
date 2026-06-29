<template>
  <div class="page admin-risk-page">
    <PageHeader title="风险工作台" description="先处理待处置高风险、超时预警和近期波动集中的班级">
      <template #actions>
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
        <el-button type="primary" @click="router.push('/admin/warnings')">进入预警处置</el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="loadError"
      class="load-error"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <div class="triage-grid" v-loading="loading">
      <el-card v-for="item in triageMetrics" :key="item.label" class="triage-card" shadow="never">
        <span class="metric-label">{{ item.label }}</span>
        <strong :class="'tone-' + item.tone">{{ item.value }}</strong>
        <p>{{ item.detail }}</p>
      </el-card>
    </div>

    <div class="command-grid">
      <el-card class="priority-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>待处置优先级</span>
            <small>按风险等级和等待时间排序</small>
          </div>
        </template>
        <el-empty v-if="!priorityQueue.length" description="当前没有待处置预警" />
        <div v-else class="warning-list">
          <article v-for="warning in priorityQueue" :key="warning.id" class="warning-item">
            <div class="warning-main">
              <el-tag :type="riskType(warning.warning_level)" effect="plain">
                {{ riskLabel(warning.warning_level) }}
              </el-tag>
              <strong>{{ warning.real_name || warning.username || '未登记姓名学生' }}</strong>
              <span>{{ warning.class_name || '未分班' }}</span>
            </div>
            <p>{{ warning.reason || '近期风险信号发生变化' }}</p>
            <div class="warning-meta">
              <span>等待 {{ waitingHours(warning.created_at) }} 小时</span>
              <span>{{ formatTime(warning.created_at) }}</span>
            </div>
          </article>
        </div>
      </el-card>

      <el-card class="class-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>班级风险态势</span>
            <small>来自待处置预警聚合</small>
          </div>
        </template>
        <el-empty v-if="!classRiskRows.length" description="暂无待关注班级" />
        <div v-else class="class-list">
          <div v-for="item in classRiskRows" :key="item.className" class="class-row">
            <div>
              <strong>{{ item.className }}</strong>
              <span>{{ item.studentCount }} 名学生有待处置记录</span>
            </div>
            <div class="class-counts">
              <span class="risk-high">高 {{ item.high }}</span>
              <span class="risk-medium">中 {{ item.medium }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="insight-grid">
      <el-card class="trend-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>近 7 天风险信号</span>
            <small>回答风险是否升高</small>
          </div>
        </template>
        <el-empty v-if="!riskTrendRows.length" description="暂无风险趋势数据" />
        <div v-else class="trend-list" aria-label="近 7 天风险信号列表">
          <div v-for="row in riskTrendRows" :key="row.date" class="trend-row">
            <span class="trend-date">{{ row.date }}</span>
            <div class="trend-track">
              <span class="trend-bar high" :style="{ width: trendWidth(row.high) }"></span>
              <span class="trend-bar medium" :style="{ width: trendWidth(row.medium) }"></span>
            </div>
            <strong>{{ row.total }}</strong>
          </div>
        </div>
      </el-card>

      <el-card class="emotion-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>识别情绪分布</span>
            <small>负向情绪占比 {{ negativeEmotionPercent }}%</small>
          </div>
        </template>
        <el-empty v-if="!distributionRows.length" description="暂无情绪分布数据" />
        <div v-else class="emotion-list">
          <div v-for="row in distributionRows" :key="row.emotion" class="emotion-row">
            <span>{{ emotionLabel(row.emotion) }}</span>
            <div class="emotion-track">
              <span :style="{ width: emotionWidth(row.count) }"></span>
            </div>
            <strong>{{ row.count }}</strong>
          </div>
        </div>
      </el-card>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getAdminEmotionDistribution, getAdminOverview, getAdminRiskTrend } from '@/api/stats'
import { listAdminWarnings } from '@/api/warnings'

const WARNING_RESPONSE_HOURS = 24

const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const overview = ref({})
const distribution = ref([])
const warnings = ref([])
const riskTrend = ref([])

const emotionMap = {
  happy: '开心',
  sad: '悲伤',
  angry: '愤怒',
  fear: '恐惧',
  disgust: '厌恶',
  surprise: '惊讶',
  neutral: '平静',
}

const riskMap = {
  low: { label: '低风险', type: 'success', weight: 1 },
  medium: { label: '中风险', type: 'warning', weight: 2 },
  high: { label: '高风险', type: 'danger', weight: 3 },
}

const negativeEmotions = new Set(['sad', 'angry', 'fear', 'disgust'])

const pendingWarnings = computed(() => warnings.value.filter((item) => item.status !== 'handled'))
const highPendingWarnings = computed(() => pendingWarnings.value.filter((item) => item.warning_level === 'high'))
const overdueWarnings = computed(() => pendingWarnings.value.filter((item) => waitingHours(item.created_at) >= WARNING_RESPONSE_HOURS))
const handledTodayCount = computed(() => warnings.value.filter((item) => item.status === 'handled' && isToday(item.handled_at)).length)
const totalEmotionCount = computed(() => distribution.value.reduce((sum, item) => sum + Number(item.count || 0), 0))
const negativeEmotionCount = computed(() =>
  distribution.value
    .filter((item) => negativeEmotions.has(item.emotion))
    .reduce((sum, item) => sum + Number(item.count || 0), 0)
)
const negativeEmotionPercent = computed(() => {
  if (!totalEmotionCount.value) return 0
  return Math.round((negativeEmotionCount.value / totalEmotionCount.value) * 100)
})

const triageMetrics = computed(() => [
  {
    label: '待处置预警',
    value: pendingWarnings.value.length,
    tone: pendingWarnings.value.length ? 'warning' : 'stable',
    detail: `高风险 ${highPendingWarnings.value.length} 条，超 ${WARNING_RESPONSE_HOURS} 小时 ${overdueWarnings.value.length} 条`,
  },
  {
    label: '今日识别记录',
    value: overview.value.today_records ?? 0,
    tone: 'info',
    detail: `在册学生 ${overview.value.student_count ?? 0} 人，记录数不等同覆盖人数`,
  },
  {
    label: '今日已跟进',
    value: handledTodayCount.value,
    tone: handledTodayCount.value ? 'stable' : 'muted',
    detail: '来自预警处理时间，后续需接入干预记录',
  },
  {
    label: '负向情绪占比',
    value: `${negativeEmotionPercent.value}%`,
    tone: negativeEmotionPercent.value >= 30 ? 'warning' : 'info',
    detail: '悲伤、愤怒、恐惧、厌恶识别记录占比',
  },
])

const priorityQueue = computed(() =>
  [...pendingWarnings.value]
    .sort((a, b) => {
      const riskGap = (riskMap[b.warning_level]?.weight || 0) - (riskMap[a.warning_level]?.weight || 0)
      if (riskGap) return riskGap
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    })
    .slice(0, 4)
)

const classRiskRows = computed(() => {
  const rows = new Map()
  pendingWarnings.value.forEach((warning) => {
    const className = warning.class_name || '未分班'
    if (!rows.has(className)) {
      rows.set(className, {
        className,
        high: 0,
        medium: 0,
        students: new Set(),
      })
    }
    const row = rows.get(className)
    if (warning.warning_level === 'high') row.high += 1
    if (warning.warning_level === 'medium') row.medium += 1
    row.students.add(warning.user_id || warning.username || warning.real_name || warning.id)
  })

  return [...rows.values()]
    .map((row) => ({ ...row, studentCount: row.students.size }))
    .sort((a, b) => b.high - a.high || b.medium - a.medium || b.studentCount - a.studentCount)
    .slice(0, 5)
})

const riskTrendRows = computed(() => {
  const buckets = new Map()
  riskTrend.value.forEach((item) => {
    if (!buckets.has(item.date)) {
      buckets.set(item.date, { date: item.date, high: 0, medium: 0, total: 0 })
    }
    const row = buckets.get(item.date)
    const count = Number(item.count || 0)
    if (item.level === 'high') row.high += count
    if (item.level === 'medium') row.medium += count
    row.total += count
  })
  return [...buckets.values()].sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-7)
})

const maxTrendTotal = computed(() => Math.max(1, ...riskTrendRows.value.map((row) => row.total)))
const distributionRows = computed(() => [...distribution.value].sort((a, b) => Number(b.count || 0) - Number(a.count || 0)))
const maxEmotionCount = computed(() => Math.max(1, ...distributionRows.value.map((row) => Number(row.count || 0))))

const loadData = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [overviewRes, distributionRes, warningsRes, riskTrendRes] = await Promise.all([
      getAdminOverview(),
      getAdminEmotionDistribution(),
      listAdminWarnings(),
      getAdminRiskTrend(),
    ])
    overview.value = overviewRes.data || {}
    distribution.value = distributionRes.data || []
    warnings.value = warningsRes.data || []
    riskTrend.value = riskTrendRes.data || []
  } catch (error) {
    loadError.value = error?.message || '工作台数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

const isToday = (value) => {
  if (!value) return false
  const date = new Date(value)
  const now = new Date()
  return date.toDateString() === now.toDateString()
}

function waitingHours(value) {
  if (!value) return 0
  const elapsed = Date.now() - new Date(value).getTime()
  return Math.max(0, Math.floor(elapsed / 1000 / 60 / 60))
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
const emotionLabel = (value) => emotionMap[value] || value || '-'
const riskLabel = (value) => riskMap[value]?.label || value || '-'
const riskType = (value) => riskMap[value]?.type || 'info'
const trendWidth = (value) => {
  const count = Number(value || 0)
  return count ? `${Math.max(4, (count / maxTrendTotal.value) * 100)}%` : '0%'
}
const emotionWidth = (value) => {
  const count = Number(value || 0)
  return count ? `${Math.max(4, (count / maxEmotionCount.value) * 100)}%` : '0%'
}

onMounted(loadData)
</script>

<style scoped>
.admin-risk-page {
  display: grid;
  gap: 16px;
}

.load-error {
  margin-bottom: 0;
}

.triage-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.triage-card {
  min-height: 108px;
}

.metric-label {
  display: block;
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 800;
}

.triage-card strong {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 30px;
  line-height: 1.2;
}

.triage-card p {
  margin: 10px 0 0;
  color: var(--mh-muted);
  font-size: 13px;
  line-height: 1.6;
}

.tone-warning {
  color: var(--mh-warning) !important;
}

.tone-stable {
  color: var(--mh-success) !important;
}

.tone-info {
  color: var(--mh-info) !important;
}

.tone-muted {
  color: var(--mh-muted) !important;
}

.command-grid,
.insight-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.section-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.section-heading span {
  color: var(--mh-ink);
  font-weight: 800;
}

.section-heading small {
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 600;
}

.warning-list,
.class-list,
.trend-list,
.emotion-list {
  display: grid;
  gap: 10px;
}

.warning-item {
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
}

.warning-main,
.warning-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.warning-main strong {
  color: var(--mh-ink);
}

.warning-main span:last-child,
.warning-meta {
  color: var(--mh-muted);
  font-size: 13px;
}

.warning-item p {
  margin: 10px 0;
  color: var(--mh-text);
  line-height: 1.6;
}

.warning-meta {
  justify-content: space-between;
}

.class-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--mh-line);
}

.class-row:last-child {
  border-bottom: none;
}

.class-row strong,
.class-row span {
  display: block;
}

.class-row strong {
  color: var(--mh-ink);
}

.class-row span {
  margin-top: 4px;
  color: var(--mh-muted);
  font-size: 13px;
}

.class-counts {
  display: flex;
  gap: 10px;
  white-space: nowrap;
}

.risk-high {
  color: var(--mh-danger) !important;
}

.risk-medium {
  color: var(--mh-warning) !important;
}

.trend-row,
.emotion-row {
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr) 42px;
  align-items: center;
  gap: 10px;
  color: var(--mh-text);
  font-size: 13px;
}

.trend-track,
.emotion-track {
  display: flex;
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--mh-surface-muted);
}

.trend-bar.high {
  background: var(--mh-danger);
}

.trend-bar.medium {
  background: var(--mh-warning);
}

.emotion-track span {
  background: var(--mh-info);
}

.trend-row strong,
.emotion-row strong {
  color: var(--mh-ink);
  text-align: right;
}

@media (max-width: 720px) {
  .triage-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .command-grid,
  .insight-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 721px) and (max-width: 1100px) {
  .priority-panel :deep(.el-card__body),
  .class-panel :deep(.el-card__body) {
    max-height: 420px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .trend-panel :deep(.el-card__body),
  .emotion-panel :deep(.el-card__body) {
    max-height: 260px;
    overflow-x: hidden;
    overflow-y: auto;
  }
}

@media (max-width: 640px) {
  .triage-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .triage-card {
    min-height: 94px;
  }

  .triage-card strong {
    font-size: 22px;
  }

  .triage-card p {
    font-size: 12px;
    line-height: 1.45;
  }

  .priority-panel :deep(.el-card__body),
  .class-panel :deep(.el-card__body),
  .trend-panel :deep(.el-card__body),
  .emotion-panel :deep(.el-card__body) {
    max-height: 220px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .command-grid {
    max-height: 520px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .insight-grid {
    max-height: 420px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .section-heading,
  .class-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .trend-row,
  .emotion-row {
    grid-template-columns: 64px minmax(0, 1fr) 36px;
  }
}
</style>
