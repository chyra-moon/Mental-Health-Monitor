<template>
  <el-card class="history-card" shadow="never">
    <template #header>
      <div class="history-header">
        <div class="title-group">
          <span class="card-title">历史会话记录</span>
          <small class="card-desc">双击行或点击详情，可复核历史评估报告</small>
        </div>
        <el-button size="small" :icon="Refresh" circle @click="$emit('refresh')" />
      </div>
    </template>

    <el-table
      v-loading="loading"
      :data="paginatedSessions"
      stripe
      size="small"
      max-height="300"
      @row-dblclick="handleRowDblClick"
    >
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="student_name" label="学生姓名" min-width="100" />
      <el-table-column prop="class_name" label="班级" min-width="120">
        <template #default="{ row }">{{ row.class_name || '未分班' }}</template>
      </el-table-column>
      <el-table-column prop="video_filename" label="留存视频文件" min-width="180" show-overflow-tooltip />
      <el-table-column prop="dominant_emotion" label="主导情绪" width="90" align="center">
        <template #default="{ row }">
          <span v-if="row.status === 'completed'">
            {{ emotionLabel(row.dominant_emotion) }}
          </span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="risk_level" label="评估风险" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="riskType(row.risk_level)" size="small">
            {{ riskLabel(row.risk_level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="会话时间" min-width="160">
        <template #default="{ row }">{{ formatTime(row.started_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click="$emit('detail', row.id)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="sessions.length"
        layout="prev, pager, next, total"
        size="small"
        @update:current-page="$emit('update:currentPage', $event)"
        @update:page-size="$emit('update:pageSize', $event)"
      />
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { emotionLabel, riskLabel, riskType, formatTime } from '@/domain/mentalHealth'

const props = defineProps({
  sessions: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 6
  }
})

const emit = defineEmits([
  'update:currentPage',
  'update:pageSize',
  'refresh',
  'detail'
])

const paginatedSessions = computed(() => {
  const start = (props.currentPage - 1) * props.pageSize
  const end = start + props.pageSize
  return props.sessions.slice(start, end)
})

function handleRowDblClick(row) {
  emit('detail', row.id)
}
</script>

<style scoped>
.history-card {
  width: 100%;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-group {
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

.text-muted {
  color: var(--mh-muted);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
