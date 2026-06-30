<template>
  <el-card class="table-card" shadow="never">
    <template #header>
      <div class="table-card-header">
        <span class="card-title">详细记录列表</span>
        <small class="card-desc">双击行或点击详情，可调出分析子窗口</small>
      </div>
    </template>

    <el-table
      v-loading="loading"
      :data="paginatedRecords"
      stripe
      size="small"
      @row-click="handleRowClick"
      class="records-table"
    >
      <el-table-column prop="id" label="ID" width="120" align="center" show-overflow-tooltip />
      <el-table-column v-if="showStudentColumns" prop="real_name" label="姓名" min-width="100">
        <template #default="{ row }">{{ row.real_name || row.username || '未命名' }}</template>
      </el-table-column>
      <el-table-column prop="source_label" label="来源类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.source_type === 'video' ? 'info' : 'success'" size="small">
            {{ row.source_label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="dominant_emotion" label="主导情绪" width="100" align="center">
        <template #default="{ row }">
          <strong>{{ emotionLabel(row.dominant_emotion) }}</strong>
        </template>
      </el-table-column>
      <el-table-column prop="confidence" label="置信度" width="90" align="center">
        <template #default="{ row }">{{ formatPercent(row.confidence) }}</template>
      </el-table-column>
      <el-table-column prop="risk_level" label="评估风险" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="riskType(row.risk_level)" size="small">
            {{ riskLabel(row.risk_level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="记录时间" min-width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click.stop="showDetail(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="records.length"
        layout="prev, pager, next, total"
        size="small"
      />
    </div>

    <!-- 记录详情子窗口 (Dialog) -->
    <el-dialog
      v-model="dialogVisible"
      title="识别分析详情"
      width="min(980px, 92vw)"
      class="record-detail-dialog"
      destroy-on-close
      append-to-body
    >
      <div v-if="selectedRecord" class="detail-container">
        <div class="detail-overview-grid">
          <section class="record-info-panel">
            <div class="section-head">
              <span>记录信息</span>
              <strong>#{{ selectedRecord.id }}</strong>
            </div>
            <div class="record-info-list">
              <div>
                <span>来源类型</span>
                <strong>{{ selectedRecord.source_label || '-' }}</strong>
              </div>
              <div>
                <span>产生时间</span>
                <strong>{{ formatTime(selectedRecord.created_at) }}</strong>
              </div>
              <div v-if="selectedRecord.source_type === 'video'">
                <span>关联视频</span>
                <strong>{{ selectedRecord.video_filename || '-' }}</strong>
              </div>
              <div v-if="selectedRecord.source_type === 'video'">
                <span>抽帧统计</span>
                <strong>{{ selectedRecord.analyzed_frames || 0 }} / {{ selectedRecord.total_frames || 0 }} 帧</strong>
              </div>
            </div>
          </section>

          <section class="detail-main-panel">
            <div class="detail-summary-card">
              <MetricCard
                label="主导情绪"
                :value="emotionLabel(selectedRecord.dominant_emotion)"
                note="识别模型输出的主情绪"
                :tone="selectedRecord.risk_level || 'neutral'"
                icon="monitor"
                compact
              />
              <MetricCard
                label="置信度"
                :value="formatPercent(selectedRecord.confidence)"
                note="当前识别结果可信度"
                tone="info"
                icon="data"
                compact
              />
              <MetricCard
                label="风险等级"
                :value="riskLabel(selectedRecord.risk_level)"
                note="系统评估风险等级"
                :tone="selectedRecord.risk_level || 'neutral'"
                icon="warning"
                compact
              />
            </div>

            <div class="detail-brief-grid">
              <div class="brief-card">
                <span>综合判断</span>
                <strong>{{ getRiskSummary(selectedRecord) }}</strong>
                <p>{{ getObservationText(selectedRecord) }}</p>
              </div>
              <div class="brief-card">
                <span>关注重点</span>
                <strong>{{ getCareLevelText(selectedRecord) }}</strong>
                <p>{{ getCareActionText(selectedRecord) }}</p>
              </div>
              <div class="brief-card">
                <span>记录价值</span>
                <strong>趋势对照</strong>
                <p>该记录已纳入识别记录、趋势观察和风险统计。</p>
              </div>
            </div>
          </section>
        </div>

        <div class="detail-lower-grid">
          <div class="scores-section">
            <div class="section-title-row">
              <h4 class="section-title">情绪概率明细</h4>
              <span>按概率排序</span>
            </div>
            <el-table
              :data="selectedScoreRows"
              class="detail-score-table"
              size="small"
              :empty-text="'暂无概率明细'"
            >
              <el-table-column prop="label" label="情绪" width="86" />
              <el-table-column label="概率" width="86" align="center">
                <template #default="{ row }">{{ formatPercent(row.score) }}</template>
              </el-table-column>
              <el-table-column label="分布" min-width="180">
                <template #default="{ row }">
                  <el-progress
                    class="score-table-progress"
                    :percentage="row.percentage"
                    :stroke-width="8"
                    :color="emotionColor(row.emotion)"
                    :format="() => `${row.percentage}%`"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="150" />
            </el-table>
          </div>

          <div class="suggestion-section">
            <div class="section-title-row">
              <h4 class="section-title">评估原因与干预建议</h4>
              <span>{{ riskLabel(selectedRecord.risk_level) }}</span>
            </div>
            <div class="suggestion-box">
              <p v-if="selectedRecord.reason" class="reason-text"><strong>触发原因：</strong>{{ selectedRecord.reason }}</p>
              <p class="advice-text"><strong>系统建议：</strong>{{ selectedRecord.suggestion || '建议结合近期记录继续自我观察。' }}</p>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import MetricCard from '@/components/MetricCard.vue'
import { emotionLabel, emotionColor, riskLabel, riskType, formatTime } from '@/domain/mentalHealth'

const props = defineProps({
  records: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  showStudentColumns: Boolean,
  focusRecordId: {
    type: [String, Number],
    default: ''
  }
})

const currentPage = ref(1)
const pageSize = ref(6)
const dialogVisible = ref(false)
const selectedRecord = ref(null)
const lastFocusedRecordId = ref('')

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return props.records.slice(start, end)
})

const selectedScoreRows = computed(() => {
  const scores = selectedRecord.value?.emotion_scores || {}
  return Object.entries(scores)
    .map(([emotion, score]) => {
      const normalizedScore = Number(score) || 0
      return {
        emotion,
        label: emotionLabel(emotion),
        score: normalizedScore,
        percentage: Number((normalizedScore * 100).toFixed(1)),
        description: getScoreDescription(normalizedScore)
      }
    })
    .sort((a, b) => b.score - a.score)
})

watch(() => props.records, () => {
  currentPage.value = 1
})

watch(
  [() => props.records, () => props.focusRecordId],
  () => {
    const targetId = props.focusRecordId
    if (!targetId || lastFocusedRecordId.value === String(targetId)) return
    const targetIndex = props.records.findIndex((record) => String(record.id) === String(targetId))
    const match = props.records[targetIndex]
    if (!match) return
    lastFocusedRecordId.value = String(targetId)
    currentPage.value = Math.floor(targetIndex / pageSize.value) + 1
    showDetail(match)
  },
  { immediate: true }
)

function handleRowClick(row) {
  showDetail(row)
}

function showDetail(row) {
  selectedRecord.value = row
  dialogVisible.value = true
}

function getRiskSummary(data) {
  if (data.risk_level === 'high') return '需要重点关注'
  if (data.risk_level === 'medium') return '存在轻度波动'
  return '状态相对平稳'
}

function getObservationText(data) {
  const emotion = emotionLabel(data.dominant_emotion)
  if (data.risk_level === 'high') {
    return `本次主导情绪为${emotion}，建议尽快完成线下沟通。`
  }
  if (data.risk_level === 'medium') {
    return `本次主导情绪为${emotion}，建议结合测评和近期记录继续观察。`
  }
  return `本次主导情绪为${emotion}，整体处于日常观察范围。`
}

function getCareLevelText(data) {
  if (data.risk_level === 'high') return '优先沟通'
  if (data.risk_level === 'medium') return '连续观察'
  return '常规记录'
}

function getCareActionText(data) {
  if (data.risk_level === 'high') return '建议辅导员或心理中心尽快介入并补充处置记录。'
  if (data.risk_level === 'medium') return '建议关注近一周情绪变化，必要时安排一次简短沟通。'
  return '保持规律记录，用于后续趋势对照。'
}

function getScoreDescription(score) {
  if (score >= 0.45) return '主要情绪信号'
  if (score >= 0.25) return '次级情绪信号'
  if (score >= 0.1) return '弱信号'
  return '低占比'
}

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.table-card {
  width: 100%;
  flex: 1;
  min-height: 0;
}
.table-card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
}
.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.card-desc {
  font-size: 11px;
  color: var(--mh-muted);
  margin-left: auto;
  text-align: right;
  white-space: nowrap;
}
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

/* Detail modal styling */
:deep(.record-detail-dialog .el-dialog__body) {
  padding-top: 12px;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-overview-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.72fr) minmax(0, 1.28fr);
  gap: 16px;
  align-items: stretch;
}

.record-info-panel,
.detail-main-panel,
.scores-section,
.suggestion-section {
  background: var(--mh-surface);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
}

.record-info-panel {
  padding: 14px;
}

.detail-main-panel {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-head,
.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-head span,
.section-title-row span {
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.section-head strong {
  color: var(--mh-ink);
  font-size: 12px;
  font-weight: 750;
}

.record-info-list {
  display: grid;
  gap: 10px;
}

.record-info-list div {
  padding: 10px 0;
  border-top: 1px solid var(--mh-line);
}

.record-info-list div:first-child {
  border-top: 0;
  padding-top: 0;
}

.record-info-list span {
  display: block;
  margin-bottom: 4px;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.record-info-list strong {
  display: block;
  color: var(--mh-ink);
  font-size: 12.5px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.detail-summary-card {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.detail-brief-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.brief-card {
  min-height: 104px;
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: #fbfbfc;
}

.brief-card span {
  display: block;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.brief-card strong {
  display: block;
  margin-top: 6px;
  color: var(--mh-ink);
  font-size: 16px;
}

.brief-card p {
  margin: 8px 0 0;
  color: var(--mh-text);
  font-size: 12px;
  line-height: 1.6;
}

.detail-lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(300px, 0.75fr);
  gap: 16px;
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
  border-left: 3px solid var(--mh-accent);
  padding-left: 8px;
}

.scores-section,
.suggestion-section {
  padding: 16px;
}

.detail-score-table {
  width: 100%;
}

.detail-score-table :deep(.el-table__cell) {
  padding: 7px 0;
}

.score-table-progress :deep(.el-progress__text) {
  min-width: 38px;
  font-size: 11px !important;
}

.suggestion-box {
  background: #fbfbfc;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  padding: 12px 16px;
}

.reason-text,
.advice-text {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--mh-text);
}

.reason-text {
  margin-bottom: 8px;
}

.advice-text strong {
  color: var(--mh-primary-strong);
}

@media (max-width: 900px) {
  .detail-overview-grid,
  .detail-lower-grid,
  .detail-brief-grid {
    grid-template-columns: 1fr;
  }
}
</style>
