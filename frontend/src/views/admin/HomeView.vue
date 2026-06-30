<template>
  <div class="page admin-risk-page">
    <PageHeader title="风险工作台" description="综合研判校内高风险预警状态、各班级风险态势及心理会话波动特征">
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

    <!-- Layer 1: Stat cards -->
    <div class="triage-grid" v-loading="loading">
      <el-card v-for="item in triageMetrics" :key="item.label" class="triage-card" shadow="never">
        <span class="metric-label">{{ item.label }}</span>
        <strong :class="'tone-' + item.tone">{{ item.value }}</strong>
        <p>{{ item.detail }}</p>
      </el-card>
    </div>

    <!-- Layer 2: Priority Queue and Class Risk (Fixed height boxes) -->
    <div class="command-grid">
      <!-- Priority queue -->
      <el-card class="priority-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>待处置优先级队列</span>
            <small>优先展示高风险及超时未处理记录</small>
          </div>
        </template>
        <el-empty v-if="!priorityQueue.length" description="当前无待处置预警" />
        <div v-else class="warning-list">
          <article 
            v-for="warning in priorityQueue" 
            :key="warning.id" 
            class="warning-item"
            @click="openTriageDialog(warning)"
          >
            <div class="warning-main">
              <el-tag :type="riskType(warning.warning_level)" size="small" effect="plain">
                {{ riskLabel(warning.warning_level) }}
              </el-tag>
              <strong>{{ warning.real_name || warning.username || '未入档学生' }}</strong>
              <span class="class-text">{{ warning.class_name || '未分配班级' }}</span>
            </div>
            <p class="warning-reason">{{ warning.reason || '近期风险信号波动' }}</p>
            <div class="warning-meta">
              <span>等待时间: {{ waitingHours(warning.created_at) }} 小时</span>
              <span>{{ formatTime(warning.created_at) }}</span>
            </div>
          </article>
        </div>
      </el-card>

      <!-- Class Risk status -->
      <el-card class="class-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>班级风险态势分布</span>
            <small>基于各班待处理风险记录聚合</small>
          </div>
        </template>
        <el-empty v-if="!classRiskRows.length" description="暂无待关注班级" />
        <div v-else class="class-list">
          <div v-for="item in classRiskRows" :key="item.className" class="class-row">
            <div class="class-info">
              <strong>{{ item.className }}</strong>
              <span>{{ item.studentCount }} 名学生待跟进</span>
            </div>
            <div class="class-counts">
              <el-tag type="danger" size="small" effect="dark" v-if="item.high > 0">高危 {{ item.high }}</el-tag>
              <el-tag type="warning" size="small" effect="plain" v-if="item.medium > 0">中度 {{ item.medium }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Layer 3: Trend & Emotion distribution -->
    <div class="insight-grid">
      <el-card class="trend-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-heading">
            <span>近 7 天预警走势</span>
          </div>
        </template>
        <el-empty v-if="!riskTrendRows.length" description="暂无预警趋势数据" />
        <div v-else class="trend-list">
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
            <span>全校识别情绪分布</span>
            <small>负向占比 {{ negativeEmotionPercent }}%</small>
          </div>
        </template>
        <el-empty v-if="!distributionRows.length" description="暂无情绪分布数据" />
        <div v-else class="emotion-list">
          <div v-for="row in distributionRows.slice(0, 5)" :key="row.emotion" class="emotion-row">
            <span>{{ emotionLabel(row.emotion) }}</span>
            <div class="emotion-track">
              <span :style="{ width: emotionWidth(row.count), background: emotionColor(row.emotion) }"></span>
            </div>
            <strong>{{ row.count }}</strong>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 预警处置子窗口 (Dialog) -->
    <el-dialog
      v-model="triageVisible"
      title="预警跟进处置"
      width="580px"
      destroy-on-close
    >
      <div v-if="selectedWarning" class="triage-dialog-content">
        <el-descriptions :column="2" border class="triage-desc">
          <el-descriptions-item label="学生姓名">{{ selectedWarning.real_name || selectedWarning.username }}</el-descriptions-item>
          <el-descriptions-item label="所属班级">{{ selectedWarning.class_name || '未分配' }}</el-descriptions-item>
          <el-descriptions-item label="预警级别">
            <el-tag :type="riskType(selectedWarning.warning_level)">{{ riskLabel(selectedWarning.warning_level) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="已等待时间">{{ waitingHours(selectedWarning.created_at) }} 小时</el-descriptions-item>
          <el-descriptions-item label="触发时间" :span="2">{{ formatTime(selectedWarning.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="triage-section">
          <h5>预警触发依据：</h5>
          <p class="section-text">{{ selectedWarning.reason }}</p>
        </div>

        <div class="triage-section">
          <h5>系统评估干预建议：</h5>
          <p class="section-text suggestion-text">{{ selectedWarning.suggestion }}</p>
        </div>

        <el-alert
          title="跟进须知"
          type="info"
          description="点击下方“确认完成跟进”将更新预警状态。请确保已完成线下辅导、家长电话或心理记录建档。"
          :closable="false"
          show-icon
        />
      </div>
      <template #footer>
        <el-button @click="triageVisible = false">取消</el-button>
        <el-button
          v-if="selectedWarning && selectedWarning.status !== 'handled'"
          type="primary"
          :loading="handling"
          @click="handleTriage"
        >
          确认完成跟进
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getAdminEmotionDistribution, getAdminOverview, getAdminRiskTrend } from '@/api/stats'
import { listAdminWarnings, markWarningHandled } from '@/api/warnings'
import { emotionLabel, emotionColor, riskLabel, riskType, formatTime } from '@/domain/mentalHealth'

const WARNING_RESPONSE_HOURS = 24

const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const overview = ref({})
const distribution = ref([])
const warnings = ref([])
const riskTrend = ref([])

const triageVisible = ref(false)
const selectedWarning = ref(null)
const handling = ref(false)

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
    label: '待处置风险预警',
    value: pendingWarnings.value.length,
    tone: pendingWarnings.value.length ? 'warning' : 'stable',
    detail: `高危预警 ${highPendingWarnings.value.length} 条 · 超时未决 ${overdueWarnings.value.length} 条`,
  },
  {
    label: '今日识别样本数',
    value: overview.value.today_records ?? 0,
    tone: 'info',
    detail: `全校在册学生 ${overview.value.student_count ?? 0} 人`,
  },
  {
    label: '今日处理标记数',
    value: handledTodayCount.value,
    tone: handledTodayCount.value ? 'stable' : 'muted',
    detail: '仅代表预警记录跟进完成',
  },
  {
    label: '全校负向情绪比',
    value: `${negativeEmotionPercent.value}%`,
    tone: negativeEmotionPercent.value >= 30 ? 'warning' : 'info',
    detail: '悲伤/愤怒/恐惧/厌恶样本占比',
  },
])

const priorityQueue = computed(() =>
  [...pendingWarnings.value]
    .sort((a, b) => {
      const riskWeight = { high: 3, medium: 2, low: 1 }
      const riskGap = (riskWeight[b.warning_level] || 0) - (riskWeight[a.warning_level] || 0)
      if (riskGap) return riskGap
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    })
    .slice(0, 3)
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
    row.students.add(warning.user_id)
  })

  return [...rows.values()]
    .map((row) => ({ ...row, studentCount: row.students.size }))
    .sort((a, b) => b.high - a.high || b.medium - a.medium || b.studentCount - a.studentCount)
    .slice(0, 3)
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
  return [...buckets.values()].sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-6)
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
    loadError.value = error?.message || '工作台数据加载失败，请重试。'
  } finally {
    loading.value = false
  }
}

function openTriageDialog(warning) {
  selectedWarning.value = warning
  triageVisible.value = true
}

async function handleTriage() {
  if (!selectedWarning.value) return
  
  try {
    await ElMessageBox.confirm('请确认已与该学生进行线下沟通，或已完成心理记录归档。确认后该预警标记为已处理。', '预警跟进确认', {
      confirmButtonText: '完成跟进',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  handling.value = true
  try {
    await markWarningHandled(selectedWarning.value.id)
    ElMessage.success('跟进记录已更新完成')
    triageVisible.value = false
    selectedWarning.value = null
    await loadData()
  } catch (err) {
    ElMessage.error(err.message || '更新跟进记录失败')
  } finally {
    handling.value = false
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
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
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
  height: 112px;
}

.metric-label {
  display: block;
  color: var(--mh-muted);
  font-size: 11.5px;
  font-weight: 600;
}

.triage-card strong {
  display: block;
  margin-top: 6px;
  color: var(--mh-ink);
  font-size: 24px;
  font-weight: 850;
  line-height: 1.25;
}

.triage-card p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 11.5px;
  line-height: 1.5;
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

.command-grid, .insight-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.90fr);
  gap: 16px;
  flex: 1;
}

.priority-panel, .class-panel, .trend-panel, .emotion-panel {
  height: 280px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.section-heading span {
  font-weight: 700;
  color: var(--mh-ink);
}

.section-heading small {
  color: var(--mh-muted);
  font-size: 11px;
}

.warning-list, .class-list, .trend-list, .emotion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.warning-item {
  padding: 10px 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
  cursor: pointer;
  transition: all 0.18s ease;
}

.warning-item:hover {
  border-color: var(--mh-primary);
  background-color: var(--mh-primary-soft);
  transform: translateY(-1px);
}

.warning-main {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.warning-main strong {
  color: var(--mh-ink);
}

.class-text {
  color: var(--mh-muted);
}

.warning-reason {
  margin: 6px 0;
  font-size: 12.5px;
  color: var(--mh-text);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.warning-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--mh-muted);
}

.class-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--mh-line);
}

.class-row:last-child {
  border-bottom: none;
}

.class-info strong {
  display: block;
  font-size: 13px;
  color: var(--mh-ink);
}

.class-info span {
  display: block;
  font-size: 11.5px;
  color: var(--mh-muted);
  margin-top: 2px;
}

.class-counts {
  display: flex;
  gap: 6px;
}

.trend-row, .emotion-row {
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr) 42px;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.trend-date {
  color: var(--mh-text);
  font-weight: 600;
}

.trend-track, .emotion-track {
  display: flex;
  height: 8px;
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

.trend-row strong, .emotion-row strong {
  color: var(--mh-ink);
  text-align: right;
  font-weight: 700;
}

/* Triage modal details */
.triage-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.triage-desc {
  margin-bottom: 4px;
}
.triage-section h5 {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}
.section-text {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--mh-text);
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  padding: 10px 12px;
  border-radius: var(--mh-radius-md);
}
.suggestion-text {
  font-weight: 600;
  color: var(--mh-primary-strong);
  border-color: var(--mh-primary-soft);
}

@media (max-width: 800px) {
  .triage-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .command-grid, .insight-grid {
    grid-template-columns: 1fr;
  }
  .priority-panel, .class-panel, .trend-panel, .emotion-panel {
    height: auto;
  }
}
</style>
