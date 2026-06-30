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
      max-height="350"
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
      width="640px"
      destroy-on-close
      append-to-body
    >
      <div v-if="selectedRecord" class="detail-container">
        <div class="detail-summary-card">
          <div class="sum-row">
            <span class="sum-label">主导情绪</span>
            <strong class="sum-val">{{ emotionLabel(selectedRecord.dominant_emotion) }}</strong>
          </div>
          <div class="sum-row">
            <span class="sum-label">置信度</span>
            <strong class="sum-val">{{ formatPercent(selectedRecord.confidence) }}</strong>
          </div>
          <div class="sum-row">
            <span class="sum-label">风险等级</span>
            <el-tag :type="riskType(selectedRecord.risk_level)" size="large" effect="dark">
              {{ riskLabel(selectedRecord.risk_level) }}
            </el-tag>
          </div>
        </div>

        <el-descriptions title="基本信息" :column="2" border class="detail-desc">
          <el-descriptions-item label="记录 ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selectedRecord.source_label }}</el-descriptions-item>
          <el-descriptions-item label="产生时间" :span="2">{{ formatTime(selectedRecord.created_at) }}</el-descriptions-item>
          
          <template v-if="selectedRecord.source_type === 'video'">
            <el-descriptions-item label="关联视频" :span="2">
              <code>{{ selectedRecord.video_filename || '-' }}</code>
            </el-descriptions-item>
            <el-descriptions-item label="抽帧帧数">
              {{ selectedRecord.analyzed_frames }} / {{ selectedRecord.total_frames }} 帧
            </el-descriptions-item>
            <el-descriptions-item label="负向占比">
              {{ formatPercent(selectedRecord.negative_ratio) }}
            </el-descriptions-item>
          </template>
        </el-descriptions>

        <!-- 情绪细分得分 -->
        <div class="scores-section" v-if="selectedRecord.emotion_scores">
          <h4 class="section-title">详细情绪得分</h4>
          <div v-for="(score, emotion) in selectedRecord.emotion_scores" :key="emotion" class="score-progress-row">
            <span class="emotion-name">{{ emotionLabel(emotion) }}</span>
            <el-progress
              :percentage="Number((score * 100).toFixed(1))"
              :stroke-width="12"
              :color="emotionColor(emotion)"
              :format="() => `${(score * 100).toFixed(1)}%`"
            />
          </div>
        </div>

        <div class="suggestion-section">
          <h4 class="section-title">评估原因与干预建议</h4>
          <div class="suggestion-box">
            <p v-if="selectedRecord.reason" class="reason-text"><strong>触发原因：</strong>{{ selectedRecord.reason }}</p>
            <p class="advice-text"><strong>系统建议：</strong>{{ selectedRecord.suggestion || '建议结合近期记录继续自我观察。' }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { emotionLabel, emotionColor, riskLabel, riskType, formatTime } from '@/domain/mentalHealth'

const props = defineProps({
  records: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  showStudentColumns: Boolean
})

const currentPage = ref(1)
const pageSize = ref(8)
const dialogVisible = ref(false)
const selectedRecord = ref(null)

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return props.records.slice(start, end)
})

watch(() => props.records, () => {
  currentPage.value = 1
})

function handleRowClick(row) {
  showDetail(row)
}

function showDetail(row) {
  selectedRecord.value = row
  dialogVisible.value = true
}

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.table-card {
  width: 100%;
}
.table-card-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.card-desc {
  font-size: 11px;
  color: var(--mh-muted);
}
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

/* Detail modal styling */
.detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-summary-card {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 16px;
  text-align: center;
}

.sum-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.sum-label {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.sum-val {
  font-size: 20px;
  font-weight: 850;
  color: var(--mh-ink);
}

.detail-desc {
  margin-top: 4px;
}

.section-title {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
  border-left: 3px solid var(--mh-primary);
  padding-left: 8px;
}

.score-progress-row {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.emotion-name {
  font-size: 12px;
  color: var(--mh-text);
  font-weight: 600;
}

.suggestion-box {
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
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
</style>
