<template>
  <div class="page warning-page">
    <PageHeader
      eyebrow="预警管理"
      title="风险预警处理"
      description="查看中高风险学生预警，并对待处理事项进行确认。"
      tone="admin"
    >
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadWarnings" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <div class="stats-grid three">
      <MetricCard label="预警总数" :value="warnings.length" unit="条" caption="当前列表中的全部预警" accent="sky" />
      <MetricCard label="待处理" :value="pendingCount" unit="条" caption="需要管理员确认处理" accent="warm" />
      <MetricCard label="高风险" :value="highCount" unit="条" caption="高风险等级预警数量" accent="danger" />
    </div>

    <section class="table-panel">
      <div class="panel-title-row">
        <div>
          <h2>预警明细</h2>
          <p>包含触发原因、系统建议和处理状态</p>
        </div>
      </div>

      <el-empty v-if="!loading && warnings.length === 0" description="暂无风险预警" />
      <div v-else class="table-scroll">
        <el-table v-loading="loading" :data="warnings" stripe>
          <el-table-column prop="created_at" label="预警时间" min-width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="real_name" label="学生姓名" min-width="120" />
          <el-table-column prop="username" label="用户名" min-width="130" />
          <el-table-column prop="class_name" label="班级" min-width="120">
            <template #default="{ row }">{{ row.class_name || '-' }}</template>
          </el-table-column>
          <el-table-column prop="warning_level" label="风险等级" min-width="120">
            <template #default="{ row }">
              <StatusBadge :type="row.warning_level" :label="riskLabel(row.warning_level)" />
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="触发原因" min-width="260" show-overflow-tooltip />
          <el-table-column prop="suggestion" label="系统建议" min-width="260" show-overflow-tooltip>
            <template #default="{ row }">{{ row.suggestion || '-' }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="110">
            <template #default="{ row }">
              <StatusBadge :type="row.status === 'handled' ? 'handled' : 'pending'" :label="row.status === 'handled' ? '已处理' : '待处理'" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="126" fixed="right">
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
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { formatTime, riskLabel } from '@/utils/presentation'
import http from '@/api/http'

const loading = ref(false)
const handlingId = ref(null)
const warnings = ref([])

const pendingCount = computed(() => warnings.value.filter((item) => item.status !== 'handled').length)
const highCount = computed(() => warnings.value.filter((item) => item.warning_level === 'high').length)

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

onMounted(loadWarnings)
</script>

<style scoped>
.warning-page {
  display: grid;
  gap: var(--mh-space-4);
}

.handled-time {
  color: var(--mh-muted);
  font-size: 12px;
}
</style>
