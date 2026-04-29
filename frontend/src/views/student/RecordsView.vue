<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>历史记录</h2>
        <p>查看最近 50 次情绪识别结果</p>
      </div>
      <el-button :icon="RefreshRight" type="primary" @click="loadRecords" :loading="loading">刷新</el-button>
    </div>

    <el-card shadow="never">
      <el-empty v-if="!loading && records.length === 0" description="暂无识别记录" />
      <el-table v-else v-loading="loading" :data="records" stripe>
        <el-table-column prop="created_at" label="识别时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="dominant_emotion" label="主要情绪" min-width="120">
          <template #default="{ row }">
            <el-tag :type="emotionType(row.dominant_emotion)">
              {{ emotionLabel(row.dominant_emotion) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" min-width="120">
          <template #default="{ row }">
            {{ row.confidence == null ? '-' : `${(row.confidence * 100).toFixed(1)}%` }}
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" min-width="120">
          <template #default="{ row }">
            <el-tag :type="riskType(row.risk_level)">
              {{ riskLabel(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import http from '@/api/http'

const loading = ref(false)
const records = ref([])

const emotionMap = {
  happy: { label: '开心', type: 'success' },
  sad: { label: '悲伤', type: 'primary' },
  angry: { label: '愤怒', type: 'danger' },
  fear: { label: '恐惧', type: 'warning' },
  disgust: { label: '厌恶', type: 'warning' },
  surprise: { label: '惊讶', type: 'info' },
  neutral: { label: '平静', type: 'success' },
}

const riskMap = {
  low: { label: '低风险', type: 'success' },
  medium: { label: '中风险', type: 'warning' },
  high: { label: '高风险', type: 'danger' },
}

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await http.get('/records/my')
    records.value = res.data || []
  } finally {
    loading.value = false
  }
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
const emotionLabel = (value) => emotionMap[value]?.label || value || '-'
const emotionType = (value) => emotionMap[value]?.type || 'info'
const riskLabel = (value) => riskMap[value]?.label || value || '-'
const riskType = (value) => riskMap[value]?.type || 'info'

onMounted(loadRecords)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 6px;
}

.page-header p {
  margin: 0;
  color: #909399;
}
</style>
