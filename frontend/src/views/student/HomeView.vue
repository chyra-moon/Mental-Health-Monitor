<template>
  <div class="page student-workspace">
    <PageHeader title="心理工作台">
      <template #actions>
        <el-button :icon="Refresh" @click="loadData" :loading="loading">刷新工作台</el-button>
        <el-button type="primary" :icon="Document" @click="router.push('/student/questionnaire')">进行心理测评</el-button>
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
      <MetricCard
        label="最近识别情绪"
        :value="latestRecord ? emotionLabel(latestRecord.dominant_emotion) : '未记录'"
        :note="latestRecord ? `${formatTime(latestRecord.created_at)} · ${riskLabel(latestRecord.risk_level)}` : '建议每周至少采集一次情绪数据'"
        :tone="latestRecord ? latestRecord.risk_level : 'muted'"
        icon="monitor"
      />

      <MetricCard
        label="待跟进关注提醒"
        :value="latestWarning ? riskLabel(latestWarning.level) : '暂无待处理关注'"
        :note="latestWarningSummary"
        :tone="latestWarning ? latestWarning.level : 'stable'"
        icon="bell"
      />

      <MetricCard
        label="近 7 天累计评测"
        :value="totalTrendCount"
        unit="次"
        :note="`负向情绪频次占比 ${negativePercent}%，覆盖 ${trendDayCount} 天。`"
        :tone="negativePercent >= 30 ? 'warning' : 'info'"
        icon="trend"
      />
    </div>

    <el-card class="next-step-card" shadow="never">
      <div class="next-step-box">
        <div class="advice-main">
          <div class="advice-heading">
            <span class="advice-kicker">当前建议</span>
            <span class="advice-state">近七天状态</span>
          </div>
          <p>{{ nextStepMessage }}</p>
        </div>
        <div class="mood-strip-wrap">
          <span class="strip-title">状态概览</span>
          <div class="mood-strip" aria-label="近七天状态概览">
            <span
              v-for="(bar, index) in moodBars"
              :key="`${bar.date}-${index}`"
              class="mood-bar"
              :style="{ height: bar.height, background: bar.color }"
              :title="bar.title"
            ></span>
          </div>
        </div>
        <div class="next-actions">
          <el-button type="primary" @click="router.push(primaryAction.path)">
            {{ primaryAction.label }}
          </el-button>
          <el-button @click="router.push('/student/trend')">查看趋势图表</el-button>
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
        <el-empty v-if="records.length === 0" description="暂无情绪识别记录" />
        <div v-else class="record-list">
          <article 
            v-for="record in records.slice(0, 4)" 
            :key="record.id" 
            class="record-item"
            @click="viewRecordDetail(record)"
          >
            <div class="item-info">
              <strong>{{ emotionLabel(record.dominant_emotion) }}</strong>
              <span>{{ formatTime(record.created_at) }}</span>
            </div>
            <el-tag :type="riskType(record.risk_level)" size="small" effect="plain">
              {{ riskLabel(record.risk_level) }}
            </el-tag>
          </article>
        </div>
      </el-card>

      <el-card class="quick-panel" shadow="never" v-loading="loading">
        <template #header>
          <div class="section-title">
            <span>关注提醒通知</span>
            <small>以线下沟通结果为准</small>
          </div>
        </template>
        <el-empty v-if="warnings.length === 0" description="暂无关注提醒通知" />
        <div v-else class="warning-list">
          <article 
            v-for="warning in warnings.slice(0, 4)" 
            :key="warning.id" 
            class="warning-item"
            @click="viewWarningDetail(warning)"
          >
            <div class="warning-heading">
              <el-tag :type="riskType(warning.level)" size="small">{{ riskLabel(warning.level) }}</el-tag>
              <span class="warning-status">{{ warningStatusText(warning) }}</span>
            </div>
            <p class="warning-reason">{{ warningSourceText(warning) }}</p>
            <time class="warning-time">{{ formatTime(warning.created_at) }}</time>
          </article>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="recordDialogVisible"
      title="情绪识别记录详情"
      width="540px"
      destroy-on-close
    >
      <div v-if="selectedRecord" class="detail-modal-body">
        <div class="modal-summary">
          <MetricCard label="情绪类别" :value="emotionLabel(selectedRecord.dominant_emotion)" note="识别结果主类别" :tone="selectedRecord.risk_level || 'neutral'" icon="monitor" compact />
          <MetricCard label="置信度" :value="formatPercent(selectedRecord.confidence)" note="模型输出可信度" tone="info" icon="data" compact />
          <MetricCard label="评估风险" :value="riskLabel(selectedRecord.risk_level)" note="系统评估等级" :tone="selectedRecord.risk_level || 'neutral'" icon="warning" compact />
        </div>

        <el-descriptions :column="1" border class="modal-desc">
          <el-descriptions-item label="记录时间">{{ formatTime(selectedRecord.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="来源类别">{{ selectedRecord.source_label }}</el-descriptions-item>
          <template v-if="selectedRecord.source_type === 'video'">
            <el-descriptions-item label="视频文件"><code>{{ selectedRecord.video_filename }}</code></el-descriptions-item>
            <el-descriptions-item label="负向情绪占比">{{ formatPercent(selectedRecord.negative_ratio) }}</el-descriptions-item>
          </template>
        </el-descriptions>

        <div class="modal-advice">
          <h5>评估报告与干预指导建议：</h5>
          <p>{{ selectedRecord.suggestion || '建议保持正常的心态，多留意日常的情绪变化。' }}</p>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="warningDialogVisible"
      title="心理关注提醒详情"
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedWarning" class="detail-modal-body">
        <div class="modal-summary">
          <MetricCard label="预警等级" :value="riskLabel(selectedWarning.level)" note="系统关注等级" :tone="selectedWarning.level || 'neutral'" icon="warning" compact />
          <MetricCard label="跟进状态" :value="warningStatusText(selectedWarning)" note="线下处理进度" :tone="selectedWarning.status === 'handled' ? 'stable' : 'warning'" icon="bell" compact />
        </div>

        <el-descriptions :column="1" border class="modal-desc">
          <el-descriptions-item label="触发时间">{{ formatTime(selectedWarning.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="评估依据">{{ warningSourceText(selectedWarning) }}</el-descriptions-item>
        </el-descriptions>

        <div class="modal-advice">
          <h5>校内调适干预指导建议：</h5>
          <p>{{ warningAdviceText(selectedWarning) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Document } from '@element-plus/icons-vue'
import MetricCard from '@/components/MetricCard.vue'
import PageHeader from '@/components/PageHeader.vue'
import { listMyRecords } from '@/api/records'
import { getStudentTrend } from '@/api/stats'
import { listMyWarnings } from '@/api/warnings'
import { NEGATIVE_EMOTIONS, emotionColor, emotionLabel, formatTime, riskLabel, riskType } from '@/domain/mentalHealth'

const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const records = ref([])
const warnings = ref([])
const trend = ref([])

const recordDialogVisible = ref(false)
const selectedRecord = ref(null)

const warningDialogVisible = ref(false)
const selectedWarning = ref(null)

const positiveEmotions = new Set(['happy', 'surprise'])
const negativeEmotions = NEGATIVE_EMOTIONS

const latestRecord = computed(() => records.value[0] || null)
const latestWarning = computed(() => warnings.value.find((item) => item.status !== 'handled') || warnings.value[0] || null)
const latestWarningSummary = computed(() =>
  latestWarning.value ? warningSourceText(latestWarning.value) : '近期无待处置的负向心理波动提醒。'
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
const moodBars = computed(() => {
  const rows = new Map()
  trend.value.forEach((item) => {
    if (!rows.has(item.date)) {
      rows.set(item.date, { date: item.date, total: 0, dominant: item.emotion, count: 0 })
    }
    const row = rows.get(item.date)
    const count = Number(item.count || 0)
    row.total += count
    if (count >= row.count) {
      row.count = count
      row.dominant = item.emotion
    }
  })

  const values = [...rows.values()].sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-7)
  if (!values.length) {
    return Array.from({ length: 7 }, (_, index) => ({
      date: `empty-${index}`,
      height: `${18 + index * 3}px`,
      color: 'var(--mh-line-strong)',
      title: '暂无数据',
    }))
  }
  const maxTotal = Math.max(1, ...values.map((item) => item.total))
  return values.map((item) => ({
    date: item.date,
    height: `${Math.max(18, Math.round((item.total / maxTotal) * 52))}px`,
    color: emotionColor(item.dominant),
    title: `${item.date} · ${emotionLabel(item.dominant)} · ${item.total} 次`,
  }))
})

const primaryAction = computed(() => {
  if (latestWarning.value?.level === 'high') return { label: '查看全部记录', path: '/student/records' }
  if (!latestRecord.value) return { label: '开始情绪识别', path: '/student/emotion' }
  return { label: '进行心理测评', path: '/student/questionnaire' }
})

const nextStepMessage = computed(() => {
  if (latestWarning.value?.level === 'high') {
    return '当前系统监测到高频/重度波动，建议您优先联系辅导员或心理咨询中心的老师，获取线下专业指导。'
  }
  if (latestWarning.value?.level === 'medium') {
    return '目前存在中度情绪预警，建议您进行一次心理测评自测，有助于更精细地了解状态。'
  }
  if (!latestRecord.value) {
    return '您还没有进行情绪自测。请先进行一次情绪识别，有助于我们提供日常心理关怀。'
  }
  return '目前心境指标正常。建议您保持健康作息，并坚持每周进行情绪自测与心理记录。'
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
    loadError.value = error?.message || '加载工作台数据失败，请重试。'
  } finally {
    loading.value = false
  }
}

function viewRecordDetail(record) {
  selectedRecord.value = record
  recordDialogVisible.value = true
}

function viewWarningDetail(warning) {
  selectedWarning.value = warning
  warningDialogVisible.value = true
}

const warningSourceText = (warning) => warning?.reason || '系统自动评估生成的待关注情绪预警。'
const warningStatusText = (warning) => (warning?.status === 'handled' ? '已完成教师跟进' : '待处理/建议跟进')
const warningAdviceText = (warning) => {
  if (warning?.level === 'high') {
    return '根据预警触发原因，目前您正经历较为显著的情绪负荷。请优先寻找辅导员、班主任或拨打校内 24h 心理支持热线获取一对一帮助。'
  }
  if (warning?.level === 'medium') {
    return '建议您适度减轻学习压力，可以进行适量的户外慢跑或深呼吸练习。如果情绪波动持续超过 3 天，建议预约心理中心的心理辅导。'
  }
  return '保持良好的生活习惯和自测频度。您的整体倾向比较平稳，无需过度担忧。'
}

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}

onMounted(loadData)
</script>

<style scoped>
.student-workspace {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.next-step-card {
  background: var(--mh-surface) !important;
}

.next-step-card :deep(.el-card__body) {
  padding: 16px 18px !important;
}

.next-step-box {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px 142px;
  align-items: center;
  gap: 18px;
  min-height: 92px;
}

.advice-main {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 8px;
  padding-left: 14px;
  border-left: 3px solid var(--mh-accent);
}

.advice-heading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.advice-kicker {
  color: var(--mh-ink);
  font-size: 15px;
  font-weight: 800;
  line-height: 1.2;
}

.advice-state {
  padding: 2px 7px;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  border: 1px solid var(--mh-line);
  border-radius: 5px;
}

.advice-main p {
  margin: 0;
  color: var(--mh-text);
  font-size: 14px;
  line-height: 1.65;
}

.mood-strip-wrap {
  display: flex;
  align-items: stretch;
  justify-content: center;
  min-width: 0;
  flex-direction: column;
  gap: 8px;
  padding: 0 18px;
  border-left: 1px solid var(--mh-line);
  border-right: 1px solid var(--mh-line);
}

.strip-title {
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  text-align: center;
}

.mood-strip {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 7px;
  height: 46px;
}

.mood-bar {
  display: block;
  width: 12px;
  min-height: 18px;
  border-radius: 999px 999px 4px 4px;
}

.next-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.next-actions .el-button {
  width: 100%;
  height: 34px;
  margin-left: 0 !important;
  border-radius: 6px !important;
  font-size: 12.5px;
}

.next-actions .el-button:not(.el-button--primary) {
  background: #ffffff !important;
  border-color: var(--mh-line-strong) !important;
  color: var(--mh-text);
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.quick-panel {
  height: 100%;
  min-height: 274px;
  overflow: hidden;
}

.quick-panel :deep(.el-card__body) {
  height: calc(100% - 49px);
  overflow: hidden;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title span {
  font-weight: 700;
  color: var(--mh-ink);
}

.section-title small {
  color: var(--mh-muted);
  font-size: 11px;
}

.record-list, .warning-list {
  display: grid;
  grid-template-rows: repeat(4, minmax(0, 1fr));
  gap: 8px;
  height: 100%;
  min-height: 0;
}

.record-item, .warning-item {
  min-height: 0;
  padding: 10px 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
  cursor: pointer;
  transition: all 0.18s ease;
}

.record-item:hover, .warning-item:hover {
  border-color: var(--mh-primary);
  background-color: var(--mh-primary-soft);
  transform: translateY(-1px);
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-info strong {
  font-size: 13px;
  color: var(--mh-ink);
}

.item-info span {
  font-size: 11px;
  color: var(--mh-muted);
}

.warning-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.warning-status {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.warning-reason {
  margin: 0 0 6px;
  font-size: 12px;
  color: var(--mh-text);
  line-height: 1.45;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.warning-time {
  font-size: 11px;
  color: var(--mh-muted);
}

.detail-modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.modal-desc {
  margin-top: 4px;
}

.modal-advice {
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 12px 14px;
}

.modal-advice h5 {
  margin: 0 0 6px;
  font-size: 12.5px;
  font-weight: 800;
  color: var(--mh-ink);
}

.modal-advice p {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--mh-text);
}

@media (max-width: 800px) {
  .summary-grid, .workspace-grid {
    grid-template-columns: 1fr;
  }
  .quick-panel {
    height: auto;
  }
  .next-step-box {
    grid-template-columns: 1fr;
    align-items: stretch;
  }
  .mood-strip-wrap {
    padding: 0;
    border: 0;
  }
  .mood-strip,
  .strip-title {
    justify-content: flex-start;
    text-align: left;
  }
  .next-actions {
    flex-direction: row;
  }
}
</style>
