<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="会话评估历史详情"
    width="960px"
    destroy-on-close
    class="detail-dialog"
  >
    <div v-if="detailSession" class="dialog-body-grid">
      <!-- Left side: Assessment Report -->
      <div class="report-col">
        <VideoAssessmentReport :session-summary="detailSession.session" />
      </div>
      
      <!-- Right side: Curve & Table -->
      <div class="chart-table-col">
        <VideoEmotionCurve :frame-results="detailSession.frames" />
        <VideoFrameResultsTable :frame-results="detailSession.frames" />
      </div>
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
.dialog-body-grid {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.report-col {
  position: sticky;
  top: 0;
}

.chart-table-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.loading-state {
  padding: 30px;
}

@media (max-width: 800px) {
  .dialog-body-grid {
    grid-template-columns: 1fr;
  }
  .report-col {
    position: static;
  }
  .chart-table-col {
    max-height: none;
    overflow-y: visible;
  }
}
</style>
