<template>
  <div class="page student-workspace">
    <PageHeader title="心理工作台" description="把情绪识别、心理测评、趋势观察和风险提醒放在同一处查看">
      <template #actions>
        <el-button @click="loadData" :loading="loading">刷新</el-button>
        <el-button type="primary" @click="router.push('/student/questionnaire')">进行心理测评</el-button>
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

    <div class="summary-grid" v-loading="loading">
      <el-card class="summary-card" shadow="never">
        <span>最近识别</span>
        <strong>{{ latestRecord ? emotionLabel(latestRecord.dominant_emotion) : '未记录' }}</strong>
        <p>
          {{
            latestRecord
              ? `${formatTime(latestRecord.created_at)}，${riskLabel(latestRecord.risk_level)}`
              : '可先完成一次情绪识别，作为后续趋势观察参考。'
          }}
        </p>
      </el-card>
      <el-card class="summary-card" shadow="never">
        <span>当前关注提醒</span>
        <strong :class="latestWarning ? 'risk-' + latestWarning.level : 'risk-low'">
          {{ latestWarning ? riskLabel(latestWarning.level) : '暂无待关注提醒' }}
        </strong>
        <p>{{ latestWarningSummary }}</p>
      </el-card>
      <el-card class="summary-card" shadow="never">
        <span>近 7 天趋势</span>
        <strong>{{ totalTrendCount }} 次记录</strong>
        <p>负向情绪占比 {{ negativePercent }}%，覆盖 {{ trendDayCount }} 天。</p>
      </el-card>
    </div>

    <el-card class="next-step-card" shadow="never">
      <template #header>下一步建议</template>
      <div class="next-step">
        <p>{{ nextStepMessage }}</p>
        <div class="next-actions">
          <el-button type="primary" @click="router.push(primaryAction.path)">
            {{ primaryAction.label }}
          </el-button>
          <el-button @click="router.push('/student/trend')">查看趋势观察</el-button>
        </div>
      </div>
    </el-card>

    <div class="workspace-grid">
      <el-card class="quick-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-title">
            <span>最近识别记录</span>
            <el-button link type="primary" @click="router.push('/student/records')">全部记录</el-button>
          </div>
        </template>
        <el-empty v-if="records.length === 0" description="暂无识别记录" />
        <div v-else class="record-list">
          <article v-for="record in records.slice(0, 5)" :key="record.id" class="record-item">
            <div>
              <strong>{{ emotionLabel(record.dominant_emotion) }}</strong>
              <span>{{ formatTime(record.created_at) }}</span>
            </div>
            <el-tag :type="riskType(record.risk_level)" effect="plain">{{ riskLabel(record.risk_level) }}</el-tag>
          </article>
        </div>
      </el-card>

      <el-card class="quick-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-title">
            <span>关注提醒</span>
            <small>系统根据记录生成，最终以线下沟通为准</small>
          </div>
        </template>
        <el-empty v-if="warnings.length === 0" description="暂无新的关注提醒" />
        <div v-else class="warning-list">
          <article v-for="warning in warnings.slice(0, 4)" :key="warning.id" class="warning-item">
            <div class="warning-heading">
              <el-tag :type="riskType(warning.level)" effect="plain">{{ riskLabel(warning.level) }}</el-tag>
              <span>{{ warningStatusText(warning) }}</span>
            </div>
            <p>{{ warningSourceText(warning) }}</p>
            <small>{{ warningAdviceText(warning) }}</small>
            <time>{{ formatTime(warning.created_at) }}</time>
          </article>
        </div>
      </el-card>
    </div>

    <el-card class="trend-panel" shadow="never" v-loading="loading">
      <template #header>
        <div class="section-title">
          <span>近 7 天情绪观察</span>
          <small>用于观察变化，不用于单次判断心理状态</small>
        </div>
      </template>
      <el-empty v-if="trendRows.length === 0" description="暂无趋势数据" />
      <div v-else class="trend-list" aria-label="近 7 天情绪记录列表">
        <div v-for="row in trendRows" :key="row.date" class="trend-row">
          <span>{{ row.date }}</span>
          <div class="trend-track">
            <span class="negative" :style="{ width: trendWidth(row.negative) }"></span>
            <span class="neutral" :style="{ width: trendWidth(row.neutral) }"></span>
            <span class="positive" :style="{ width: trendWidth(row.positive) }"></span>
          </div>
          <strong>{{ row.total }}</strong>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { listMyRecords } from '@/api/records'
import { getStudentTrend } from '@/api/stats'
import { listMyWarnings } from '@/api/warnings'
import { NEGATIVE_EMOTIONS, emotionLabel, formatTime, riskLabel, riskType } from '@/domain/mentalHealth'

const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const records = ref([])
const warnings = ref([])
const trend = ref([])

const positiveEmotions = new Set(['happy', 'surprise'])
const negativeEmotions = NEGATIVE_EMOTIONS

const latestRecord = computed(() => records.value[0] || null)
const latestWarning = computed(() => warnings.value.find((item) => item.status !== 'handled') || warnings.value[0] || null)
const latestWarningSummary = computed(() =>
  latestWarning.value ? warningSourceText(latestWarning.value) : '没有新的关注提醒，建议保持规律记录和自我观察。'
)
const totalTrendCount = computed(() => trend.value.reduce((sum, item) => sum + Number(item.count || 0), 0))
const negativeTrendCount = computed(() =>
  trend.value
    .filter((item) => negativeEmotions.has(item.emotion))
    .reduce((sum, item) => sum + Number(item.count || 0), 0)
)
const negativePercent = computed(() => {
  if (!totalTrendCount.value) return 0
  return Math.round((negativeTrendCount.value / totalTrendCount.value) * 100)
})
const trendDayCount = computed(() => new Set(trend.value.map((item) => item.date)).size)

const trendRows = computed(() => {
  const rows = new Map()
  trend.value.forEach((item) => {
    if (!rows.has(item.date)) {
      rows.set(item.date, { date: item.date, positive: 0, negative: 0, neutral: 0, total: 0 })
    }
    const row = rows.get(item.date)
    const count = Number(item.count || 0)
    if (negativeEmotions.has(item.emotion)) row.negative += count
    else if (positiveEmotions.has(item.emotion)) row.positive += count
    else row.neutral += count
    row.total += count
  })
  return [...rows.values()].sort((a, b) => new Date(a.date) - new Date(b.date))
})
const maxTrendTotal = computed(() => Math.max(1, ...trendRows.value.map((row) => row.total)))

const primaryAction = computed(() => {
  if (latestWarning.value?.level === 'high') return { label: '查看最近记录', path: '/student/records' }
  if (!latestRecord.value) return { label: '开始情绪识别', path: '/student/emotion' }
  return { label: '进行心理测评', path: '/student/questionnaire' }
})

const nextStepMessage = computed(() => {
  if (latestWarning.value?.level === 'high') {
    return '当前存在重点关注提醒，建议优先联系辅导员或校心理中心，由线下支持人员一起判断下一步。'
  }
  if (latestWarning.value?.level === 'medium') {
    return '当前有需要关注的风险信号，建议完成一次心理测评，并结合近期记录决定是否联系校内支持人员。'
  }
  if (!latestRecord.value) {
    return '还没有识别记录。可以先完成一次情绪识别，再进行测评，后续趋势会更有参考价值。'
  }
  return '建议保持规律记录；当近几天负向情绪占比升高时，可完成测评并主动寻求校内支持。'
})

const loadData = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [recordsRes, warningsRes, trendRes] = await Promise.all([
      listMyRecords(),
      listMyWarnings(),
      getStudentTrend(7),
    ])
    records.value = recordsRes.data || []
    warnings.value = warningsRes.data || []
    trend.value = trendRes.data || []
  } catch (error) {
    loadError.value = error?.message || '学生工作台数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

const warningSourceText = (warning) => warning?.reason || '系统记录到近期风险信号变化，建议结合自己的实际状态观察。'
const warningStatusText = (warning) => (warning?.status === 'handled' ? '学校已标记跟进' : '建议待跟进')
const warningAdviceText = (warning) => {
  if (warning?.level === 'high') {
    return '如近期持续不适或影响学习生活，请优先联系辅导员或校心理中心。'
  }
  if (warning?.level === 'medium') {
    return '可以先完成一次心理测评，并留意近几天情绪和睡眠变化。'
  }
  return '保持规律记录即可；如状态变化明显，可主动寻求校内支持。'
}
const trendWidth = (value) => {
  const count = Number(value || 0)
  return count ? `${Math.max(4, (count / maxTrendTotal.value) * 100)}%` : '0%'
}

onMounted(loadData)
</script>

<style scoped>
.student-workspace {
  display: grid;
  gap: 16px;
}

.state-alert {
  margin-bottom: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  min-height: 108px;
}

.summary-card span {
  display: block;
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 800;
}

.summary-card strong {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 24px;
  line-height: 1.25;
}

.summary-card p {
  margin: 10px 0 0;
  color: var(--mh-muted);
  font-size: 13px;
  line-height: 1.6;
}

.risk-low {
  color: var(--mh-success) !important;
}

.risk-medium {
  color: var(--mh-warning) !important;
}

.risk-high {
  color: var(--mh-danger) !important;
}

.next-step {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.next-step p {
  max-width: 760px;
  margin: 0;
  color: var(--mh-text);
  line-height: 1.7;
}

.next-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

.section-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.section-title span {
  color: var(--mh-ink);
  font-weight: 800;
}

.section-title small {
  color: var(--mh-muted);
  font-size: 12px;
}

.record-list,
.warning-list,
.trend-list {
  display: grid;
  gap: 10px;
}

.record-item,
.warning-item {
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
}

.record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.record-item strong,
.record-item span {
  display: block;
}

.record-item strong {
  color: var(--mh-ink);
}

.record-item span {
  margin-top: 4px;
  color: var(--mh-muted);
  font-size: 13px;
}

.warning-heading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-heading span {
  color: var(--mh-muted);
  font-size: 13px;
}

.warning-item p {
  margin: 10px 0 8px;
  color: var(--mh-text);
  line-height: 1.6;
}

.warning-item small {
  display: block;
  margin-bottom: 8px;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.5;
}

.warning-item time {
  color: var(--mh-muted);
  font-size: 12px;
}

.trend-row {
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) 40px;
  align-items: center;
  gap: 10px;
  color: var(--mh-text);
  font-size: 13px;
}

.trend-track {
  display: flex;
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--mh-surface-muted);
}

.trend-track .negative {
  background: var(--mh-warning);
}

.trend-track .neutral {
  background: var(--mh-info);
}

.trend-track .positive {
  background: var(--mh-success);
}

.trend-row strong {
  color: var(--mh-ink);
  text-align: right;
}

@media (max-width: 720px) {
  .summary-grid,
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .next-step {
    align-items: flex-start;
    flex-direction: column;
  }

  .next-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-card {
    min-height: 96px;
  }

  .summary-card strong {
    font-size: 20px;
  }

  .summary-card p {
    font-size: 12px;
    line-height: 1.45;
  }

  .workspace-grid {
    max-height: 520px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .quick-panel :deep(.el-card__body),
  .trend-panel :deep(.el-card__body) {
    max-height: 220px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .record-item,
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .trend-row {
    grid-template-columns: 72px minmax(0, 1fr) 32px;
  }
}
</style>
