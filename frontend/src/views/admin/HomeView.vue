<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>管理员首页</h2>
        <p>查看系统整体监测概况</p>
      </div>
      <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
    </div>

    <el-row :gutter="16" class="overview-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ overview.student_count ?? 0 }}</div>
          <div class="stat-label">学生总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ overview.today_records ?? 0 }}</div>
          <div class="stat-label">今日识别次数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card warning">
          <div class="stat-value">{{ overview.pending_warnings ?? 0 }}</div>
          <div class="stat-label">待处理中高风险</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>情绪分布</template>
      <el-empty v-if="!distribution.length" description="暂无情绪分布数据" />
      <el-table v-else v-loading="loading" :data="distribution" stripe>
        <el-table-column prop="emotion" label="情绪" min-width="120">
          <template #default="{ row }">{{ emotionLabel(row.emotion) }}</template>
        </el-table-column>
        <el-table-column prop="count" label="次数" min-width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import http from '@/api/http'

const loading = ref(false)
const overview = ref({})
const distribution = ref([])

const emotionMap = {
  happy: '开心',
  sad: '悲伤',
  angry: '愤怒',
  fear: '恐惧',
  disgust: '厌恶',
  surprise: '惊讶',
  neutral: '平静',
}

const loadData = async () => {
  loading.value = true
  try {
    const [overviewRes, distributionRes] = await Promise.all([
      http.get('/stats/admin/overview'),
      http.get('/stats/admin/emotion-distribution'),
    ])
    overview.value = overviewRes.data || {}
    distribution.value = distributionRes.data || []
  } finally {
    loading.value = false
  }
}

const emotionLabel = (value) => emotionMap[value] || value || '-'

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

.stat-card {
  text-align: center;
}

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.stat-value {
  color: #409eff;
  font-size: 34px;
  font-weight: 700;
}

.stat-label {
  margin-top: 8px;
  color: #606266;
}
</style>
