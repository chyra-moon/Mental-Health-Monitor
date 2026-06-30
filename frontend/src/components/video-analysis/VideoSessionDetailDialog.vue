<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="会话评估历史详情"
    width="min(1120px, 94vw)"
    destroy-on-close
    class="detail-dialog"
  >
    <div v-if="detailSession" class="dialog-body-stack">
      <section class="detail-section report-section">
        <VideoAssessmentReport :session-summary="detailSession.session" />
      </section>

      <section class="detail-section chart-section">
        <VideoEmotionCurve :frame-results="detailSession.frames" :height="360" />
      </section>

      <section class="detail-section table-section">
        <VideoFrameResultsTable :frame-results="detailSession.frames" :max-height="320" />
      </section>
    </div>
    <div v-else class="loading-state">
      <el-skeleton :rows="8" animated />
    </div>
    
    <template #footer>
      <el-button type="primary" @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import VideoAssessmentReport from './VideoAssessmentReport.vue'
import VideoEmotionCurve from './VideoEmotionCurve.vue'
import VideoFrameResultsTable from './VideoFrameResultsTable.vue'

defineProps({
  modelValue: Boolean,
  detailSession: Object
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
:deep(.detail-dialog .el-dialog__body) {
  padding-top: 12px;
}

.dialog-body-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  min-width: 0;
}

.chart-section :deep(.chart-card),
.table-section :deep(.frame-table-card) {
  margin-top: 0;
}

.loading-state {
  padding: 30px;
}

@media (max-width: 800px) {
  .chart-section :deep(.chart-box) {
    height: 300px !important;
  }
}
</style>
