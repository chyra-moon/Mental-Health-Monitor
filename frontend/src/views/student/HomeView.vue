<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>学生首页</h2>
        <p>欢迎使用心理健康监测系统</p>
      </div>
      <el-button type="primary" @click="router.push('/student/emotion')">开始识别</el-button>
    </div>

    <el-row :gutter="16" class="overview-row">
      <el-col :span="12">
        <el-card class="quick-card">
          <template #header>最近识别</template>
          <el-empty v-if="records.length === 0" description="暂无识别记录" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="record in records.slice(0, 5)"
              :key="record.id"
              :timestamp="formatTime(record.created_at)"
            >
              {{ emotionLabel(record.dominant_emotion) }}，
              风险等级：{{ riskLabel(record.risk_level) }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="quick-card">
          <template #header>我的预警</template>
          <el-empty v-if="warnings.length === 0" description="暂无风险预警" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="warning in warnings.slice(0, 5)"
              :key="warning.id"
              :timestamp="formatTime(warning.created_at)"
              :type="warning.level === 'high' ? 'danger' : 'warning'"
            >
              {{ riskLabel(warning.level) }}：{{ warning.reason || '系统检测到风险变化' }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'

const router = useRouter()
const records = ref([])
const warnings = ref([])

const emotionMap = {
  happy: '开心',
  sad: '悲伤',
  angry: '愤怒',
  fear: '恐惧',
  disgust: '厌恶',
  surprise: '惊讶',
  neutral: '平静',
}

const riskMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
}

const loadData = async () => {
  const [recordsRes, warningsRes] = await Promise.all([
    http.get('/records/my'),
    http.get('/warnings/my'),
  ])
  records.value = recordsRes.data || []
  warnings.value = warningsRes.data || []
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
const emotionLabel = (value) => emotionMap[value] || value || '-'
const riskLabel = (value) => riskMap[value] || value || '-'

onMounted(loadData)
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
.overview-row {
  margin-bottom: 16px;
}
.quick-card {
  min-height: 320px;
}
</style>
