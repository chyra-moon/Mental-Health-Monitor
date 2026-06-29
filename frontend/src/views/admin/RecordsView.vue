<template>
  <div class="page records-page">
    <PageHeader title="识别记录" description="查看学生情绪识别、视频分析历史和风险信号变化">
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

    <RecordInsightCharts v-if="records.length > 0" :records="records" />
    <RecognitionRecordTable :records="records" :loading="loading" show-student-columns />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import RecordInsightCharts from '@/components/records/RecordInsightCharts.vue'
import RecognitionRecordTable from '@/components/records/RecognitionRecordTable.vue'
import { listAdminRecords } from '@/api/records'

const loading = ref(false)
const loadError = ref('')
const records = ref([])

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
  display: grid;
  gap: 16px;
  max-width: 100%;
  overflow-x: hidden;
}

.records-alert {
  margin-bottom: 0;
}
</style>
