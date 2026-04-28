<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>风险预警</h2>
        <p>查看中高风险学生预警并标记处理状态</p>
      </div>
      <el-button type="primary" @click="loadWarnings">刷新</el-button>
    </div>

    <el-card>
      <el-table v-loading="loading" :data="warnings" stripe>
        <el-table-column prop="created_at" label="预警时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="real_name" label="学生姓名" min-width="120" />
        <el-table-column prop="username" label="用户名" min-width="130" />
        <el-table-column prop="class_name" label="班级" min-width="120">
          <template #default="{ row }">{{ row.class_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="warning_level" label="风险等级" min-width="110">
          <template #default="{ row }">
            <el-tag :type="riskType(row.warning_level)">
              {{ riskLabel(row.warning_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="触发原因" min-width="260" show-overflow-tooltip />
        <el-table-column prop="suggestion" label="系统建议" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">{{ row.suggestion || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'handled' ? 'success' : 'warning'">
              {{ row.status === 'handled' ? '已处理' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'handled'"
              type="primary"
              size="small"
              :loading="handlingId === row.id"
              @click="handleWarning(row)"
            >
              标记处理
            </el-button>
            <span v-else class="handled-time">{{ formatTime(row.handled_at) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import http from '@/api/http'

const loading = ref(false)
const handlingId = ref(null)
const warnings = ref([])

const riskMap = {
  low: { label: '低风险', type: 'success' },
  medium: { label: '中风险', type: 'warning' },
  high: { label: '高风险', type: 'danger' },
}

const loadWarnings = async () => {
  loading.value = true
  try {
    const res = await http.get('/warnings/admin/list')
    warnings.value = res.data || []
  } finally {
    loading.value = false
  }
}

const handleWarning = async (row) => {
  try {
    await ElMessageBox.confirm('确认将该预警标记为已处理吗？', '处理预警', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  handlingId.value = row.id
  try {
    await http.put(`/warnings/admin/${row.id}/status`)
    await loadWarnings()
  } finally {
    handlingId.value = null
  }
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
const riskLabel = (value) => riskMap[value]?.label || value || '-'
const riskType = (value) => riskMap[value]?.type || 'info'

onMounted(loadWarnings)
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
.handled-time {
  color: #909399;
  font-size: 12px;
}
</style>
