<template>
  <el-card class="frame-table-card" shadow="never">
    <template #header>
      <div class="card-title">逐帧表情数据明细</div>
    </template>
    
    <el-table :data="sortedFrames" stripe size="small" max-height="240">
      <el-table-column label="帧号" width="70" align="center">
        <template #default="{ row }">#{{ row.frame_index + 1 }}</template>
      </el-table-column>
      <el-table-column label="视频时间" width="100" align="center">
        <template #default="{ row }">{{ formatTimeMs(row.timestamp_ms) }}</template>
      </el-table-column>
      <el-table-column prop="analysis_status" label="分析状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.analysis_status)" size="small">
            {{ statusLabel(row.analysis_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="主导情绪" min-width="100">
        <template #default="{ row }">
          <span v-if="row.analysis_status === 'ok'">
            {{ emotionLabel(row.dominant_emotion) }}
          </span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="置信度" min-width="90">
        <template #default="{ row }">
          <span v-if="row.analysis_status === 'ok'">
            {{ formatPercent(row.confidence) }}
          </span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="异常日志/详细得分" min-width="260">
        <template #default="{ row }">
          <span v-if="row.analysis_status !== 'ok'" class="error-msg">
            {{ row.error_message || '未检测到人脸' }}
          </span>
          <span v-else class="scores-inline">
            {{ formatScoresInline(row.emotion_scores) }}
          </span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { emotionLabel } from '@/domain/mentalHealth'

const props = defineProps({
  frameResults: {
    type: Array,
    required: true
  }
})

const sortedFrames = computed(() => {
  return [...props.frameResults].sort((a, b) => a.frame_index - b.frame_index)
})

const formatTimeMs = (ms) => {
  if (ms === undefined || ms === null) return '00:00'
  const seconds = Math.floor(ms / 1000)
  const m = String(Math.floor(seconds / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  return `${m}:${s}`
}

const statusTagType = (status) => {
  if (status === 'ok') return 'success'
  if (status === 'no_face') return 'warning'
  return 'danger'
}

const statusLabel = (status) => {
  if (status === 'ok') return '正常'
  if (status === 'no_face') return '未捕获人脸'
  return '分析异常'
}

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}

const formatScoresInline = (scores) => {
  if (!scores) return '-'
  const items = ['happy', 'neutral', 'sad', 'angry']
  return items
    .map(key => `${emotionLabel(key)}:${(Number(scores[key] || 0) * 100).toFixed(0)}%`)
    .join(' | ')
}
</script>

<style scoped>
.frame-table-card {
  margin-top: 12px;
}
.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.text-muted {
  color: var(--mh-muted);
}
.error-msg {
  color: var(--mh-danger);
  font-size: 11px;
}
.scores-inline {
  font-size: 11px;
  color: var(--mh-muted);
}
</style>
