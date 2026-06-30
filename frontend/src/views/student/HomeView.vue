<template>
  <div class="page student-workspace">
    <PageHeader title="心理工作台" description="综合查看近期情绪识别状态、心理自测记录与校内干预跟进提醒">
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

    <!-- Layer 1: Stat cards -->
    <div class="summary-grid" v-loading="loading">
      <el-card class="summary-card border-info" shadow="never">
        <div class="card-inner">
          <div class="card-left">
            <span class="card-label">最近识别情绪</span>
            <strong class="card-value">{{ latestRecord ? emotionLabel(latestRecord.dominant_emotion) : '未记录' }}</strong>
            <p class="card-desc">
              {{
                latestRecord
                  ? `${formatTime(latestRecord.created_at)} · ${riskLabel(latestRecord.risk_level)}`
                  : '建议每周至少采集一次情绪数据'
              }}
            </p>
          </div>
          <div class="card-right">
            <el-icon class="card-icon tone-info"><Tickets /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="summary-card" :class="latestWarning ? 'border-' + latestWarning.level : 'border-stable'" shadow="never">
        <div class="card-inner">
          <div class="card-left">
            <span class="card-label">待跟进关注提醒</span>
            <strong class="card-value" :class="latestWarning ? 'risk-' + latestWarning.level : 'risk-low'">
              {{ latestWarning ? riskLabel(latestWarning.level) : '暂无待处理关注' }}
            </strong>
            <p class="card-desc">{{ latestWarningSummary }}</p>
          </div>
          <div class="card-right">
            <el-icon class="card-icon" :class="latestWarning ? 'risk-' + latestWarning.level : 'risk-low'"><Bell /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="summary-card border-primary" shadow="never">
        <div class="card-inner">
          <div class="card-left">
            <span class="card-label">近 7 天累计评测</span>
            <strong class="card-value">{{ totalTrendCount }} 次</strong>
            <p class="card-desc">负向占比 {{ negativePercent }}%，覆盖 {{ trendDayCount }} 天。</p>
          </div>
          <div class="card-right">
            <el-icon class="card-icon tone-primary"><TrendCharts /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Layer 2: Core Next Step Guidance -->
    <el-card class="next-step-card" shadow="never">
      <div class="next-step-box">
        <div class="advice-content">
          <el-icon class="advice-icon"><Opportunity /></el-icon>
          <div class="advice-text">
            <h5>下一步自测与调适建议：</h5>
            <p>{{ nextStepMessage }}</p>
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

    <!-- Layer 3: Two Column detail preview (Fixed height) -->
    <div class="workspace-grid">
      <!-- Recent Records -->
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

      <!-- Warnings -->
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
            v-for="warning in warnings.slice(0, 3)" 
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

    <!-- 记录详情子窗口 (Dialog) -->
    <el-dialog
      v-model="recordDialogVisible"
      title="情绪识别记录详情"
      width="540px"
      destroy-on-close
    >
      <div v-if="selectedRecord" class="detail-modal-body">
        <div class="modal-summary">
          <div class="sum-cell">
            <span>情绪类别</span>
            <strong>{{ emotionLabel(selectedRecord.dominant_emotion) }}</strong>
          </div>
          <div class="sum-cell">
            <span>置信度</span>
            <strong>{{ formatPercent(selectedRecord.confidence) }}</strong>
          </div>
          <div class="sum-cell">
            <span>评估风险</span>
            <el-tag :type="riskType(selectedRecord.risk_level)">
              {{ riskLabel(selectedRecord.risk_level) }}
            </el-tag>
          </div>
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

    <!-- 预警详情子窗口 (Dialog) -->
    <el-dialog
      v-model="warningDialogVisible"
      title="心理关注提醒详情"
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedWarning" class="detail-modal-body">
        <div class="modal-summary">
          <div class="sum-cell">
            <span>预警等级</span>
            <el-tag :type="riskType(selectedWarning.level)" size="large" effect="dark">
              {{ riskLabel(selectedWarning.level) }}
            </el-tag>
          </div>
          <div class="sum-cell">
            <span>跟进状态</span>
            <strong>{{ warningStatusText(selectedWarning) }}</strong>
          </div>
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
import { Refresh, Document, Opportunity, Tickets, Bell, TrendCharts } from '@element-plus/icons-vue'
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
  gap: 16px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.summary-card {
  height: 114px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.summary-card :deep(.el-card__body) {
  padding: 12px 16px !important;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

/* Accent left borders based on status */
.summary-card.border-primary {
  border-left: 4px solid var(--mh-primary) !important;
}

.summary-card.border-info {
  border-left: 4px solid var(--mh-info) !important;
}

.summary-card.border-stable {
  border-left: 4px solid var(--mh-success) !important;
}

.summary-card.border-medium {
  border-left: 4px solid var(--mh-warning) !important;
}

.summary-card.border-high {
  border-left: 4px solid var(--mh-danger) !important;
}

.card-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.card-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  min-width: 0;
}

.card-label {
  display: block;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 700;
}

.card-value {
  display: block;
  margin-top: 4px;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.1;
}

.card-desc {
  margin: 4px 0 0;
  color: var(--mh-muted);
  font-size: 11px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-right {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 12px;
  flex-shrink: 0;
}

.card-icon {
  font-size: 28px;
  opacity: 0.16;
}

.tone-primary {
  color: var(--mh-primary) !important;
}

.tone-info {
  color: var(--mh-info) !important;
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

.next-step-card {
  background: var(--mh-surface) !important;
}

.next-step-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.advice-content {
  display: flex;
  align-items: start;
  gap: 12px;
}

.advice-icon {
  font-size: 22px;
  color: var(--mh-primary);
  margin-top: 2px;
  flex: none;
}

.advice-text h5 {
  margin: 0 0 4px;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--mh-ink);
}

.advice-text p {
  margin: 0;
  font-size: 12.5px;
  color: var(--mh-text);
  line-height: 1.6;
}

.next-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  flex: 1;
}

.quick-panel {
  height: 280px;
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
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-item, .warning-item {
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
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.warning-time {
  font-size: 11px;
  color: var(--mh-muted);
}

/* Detail Modals */
.detail-modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 12px;
  text-align: center;
}

.modal-summary .sum-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.modal-summary .sum-cell span {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.modal-summary .sum-cell strong {
  font-size: 16px;
  color: var(--mh-ink);
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
    flex-direction: column;
    align-items: stretch;
  }
  .next-actions {
    justify-content: flex-end;
  }
}
</style>
