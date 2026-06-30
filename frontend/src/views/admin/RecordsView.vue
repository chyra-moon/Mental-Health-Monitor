<template>
  <div class="page records-page">
    <PageHeader title="识别记录">
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadRecords" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="loadError"
      class="records-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <section class="record-summary" aria-label="识别记录摘要">
      <MetricCard label="记录总数" :value="records.length" unit="条" note="全校识别与视频结果" tone="info" icon="files" />
      <MetricCard label="主导情绪" :value="dominantEmotionLabel" note="按当前记录统计" tone="neutral" icon="pie" />
      <MetricCard label="负向占比" :value="`${negativeRatio}%`" note="负向情绪记录比例" :tone="negativeRatio >= 30 ? 'warning' : 'info'" icon="trend" />
      <MetricCard label="高风险记录" :value="highRiskCount" unit="条" note="建议优先复核" :tone="highRiskCount ? 'danger' : 'stable'" icon="warning" />
    </section>

    <RecordInsightCharts v-if="records.length > 0" :records="records" />
    <RecognitionRecordTable :records="records" :loading="loading" show-student-columns />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import MetricCard from '@/components/MetricCard.vue'
import PageHeader from '@/components/PageHeader.vue'
import RecordInsightCharts from '@/components/records/RecordInsightCharts.vue'
import RecognitionRecordTable from '@/components/records/RecognitionRecordTable.vue'
import { listAdminRecords } from '@/api/records'
import { NEGATIVE_EMOTIONS, emotionLabel } from '@/domain/mentalHealth'

const loading = ref(false)
const loadError = ref('')
const records = ref([])

const highRiskCount = computed(() => records.value.filter((item) => item.risk_level === 'high').length)
const negativeRatio = computed(() => {
  if (!records.value.length) return 0
  const negativeCount = records.value.filter((item) => NEGATIVE_EMOTIONS.has(item.dominant_emotion)).length
  return Math.round((negativeCount / records.value.length) * 100)
})
const dominantEmotionLabel = computed(() => {
  if (!records.value.length) return '-'
  const counts = new Map()
  records.value.forEach((item) => counts.set(item.dominant_emotion, (counts.get(item.dominant_emotion) || 0) + 1))
  const [emotion] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0] || []
  return emotionLabel(emotion)
})

const loadRecords = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listAdminRecords()
    records.value = res.data || []
  } catch (error) {
    loadError.value = error?.message || '识别记录加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(loadRecords)
</script>

<style scoped>
.records-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 100%;
  height: 100%;
  overflow-x: hidden;
}

.records-alert {
  margin-bottom: 0;
}

.record-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 880px) {
  .record-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
