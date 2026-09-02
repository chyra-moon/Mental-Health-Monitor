<template>
  <div class="page warning-workflow">
    <PageHeader title="预警处置">
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadWarnings" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="loadError"
      class="state-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <section class="triage-summary" v-loading="loading">
      <MetricCard label="待跟进预警数" :value="pendingCount" unit="条" note="需要线下干预确认并更新状态" :tone="pendingCount ? 'warning' : 'stable'" icon="bell" />
      <MetricCard label="重点关注高危数" :value="highPendingCount" unit="条" note="建议 2 小时内开启排查干预" :tone="highPendingCount ? 'danger' : 'stable'" icon="warning" />
      <MetricCard label="超 24h 未处置" :value="overdueCount" unit="条" note="超时未确认的系统风险记录" :tone="overdueCount ? 'warning' : 'stable'" icon="alarm" />
      <MetricCard label="今日已完成跟进" :value="handledTodayCount" unit="条" note="表示今日更新状态的预警数量" tone="info" icon="check" />
    </section>

    <el-card class="warning-table-card" shadow="never">
      <template #header>
        <div class="table-toolbar">
          <div class="toolbar-left">
            <span class="card-title">预警信号列表</span>
            <small class="card-desc">共 {{ filteredWarnings.length }} 条</small>
          </div>
          <el-radio-group v-model="activeFilter" size="small" aria-label="筛选预警状态">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="pending">待处置</el-radio-button>
            <el-radio-button value="high">高风险</el-radio-button>
            <el-radio-button value="handled">已处理</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table 
        v-loading="loading" 
        :data="paginatedWarnings" 
        stripe 
        size="small" 
        max-height="320"
        class="warnings-table"
      >
        <el-table-column label="处置优先级" min-width="120">
          <template #default="{ row }">
            <span class="priority-pill" :class="`priority-pill--${priorityTone(row)}`">
              {{ priorityLabel(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="等待时间" width="100" align="center">
          <template #default="{ row }">
            <span class="wait-time-text">
              {{ row.status === 'handled' ? '已处置' : `${waitingHours(row)}h` }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="预警时间" min-width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="学生信息" min-width="180">
          <template #default="{ row }">
            <div class="student-cell">
              <strong>{{ row.class_name || '未分班' }} · {{ row.real_name || '未命名' }}</strong>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="warning_level" label="风险等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="riskType(row.warning_level)" size="small">
              {{ riskLabel(row.warning_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="触发依据" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ warningReason(row) }}</template>
        </el-table-column>
        <el-table-column label="跟进状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'handled' ? 'success' : 'warning'" size="small">
              {{ row.status === 'handled' ? '已处理' : '待处置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-cell">
              <el-button size="small" @click="openWarningDetail(row)">详情</el-button>
              <el-button
                v-if="row.status !== 'handled'"
                type="primary"
                size="small"
                :loading="handlingId === row.id"
                @click="markWarningHandledClick(row)"
              >
                标记已处理
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredWarnings.length"
          layout="prev, pager, next, total"
          size="small"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      title="预警处置详情"
      width="640px"
      destroy-on-close
    >
      <div v-if="selectedWarning" class="detail-content">
        <div class="detail-heading">
          <div class="heading-left">
            <span>关联学生档案</span>
            <strong>{{ selectedWarning.real_name || selectedWarning.username || '未命名' }}</strong>
            <p>{{ selectedWarning.class_name || '未分班' }} · 账号: {{ selectedWarning.username }}</p>
          </div>
          <div class="heading-right">
            <el-tag :type="riskType(selectedWarning.warning_level)" size="large" effect="dark">
              {{ riskLabel(selectedWarning.warning_level) }}
            </el-tag>
            <el-tag :type="selectedWarning.status === 'handled' ? 'success' : 'warning'" size="large" effect="plain">
              {{ selectedWarning.status === 'handled' ? '已完成标记' : '待跟进' }}
            </el-tag>
          </div>
        </div>

        <el-descriptions :column="2" border class="detail-desc">
          <el-descriptions-item label="触发时间">{{ formatTime(selectedWarning.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="处理时间">{{ formatTime(selectedWarning.handled_at) }}</el-descriptions-item>
          <el-descriptions-item label="等待时间" :span="2">
            {{ selectedWarning.status === 'handled' ? '已标记处理' : `${waitingHours(selectedWarning)} 小时` }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h5>触发预警原因：</h5>
          <p class="section-text">{{ warningReason(selectedWarning) }}</p>
        </div>

        <div class="detail-section">
          <h5>系统评估干预建议：</h5>
          <p class="section-text suggestion-text">{{ warningSuggestion(selectedWarning) }}</p>
        </div>

        <el-alert
          title="跟进声明"
          type="info"
          description="在此页“标记已处理”仅代表辅导员或心理咨询中心已完成线下排查确认或电话问询建档。更详细的干预个案分析仍需在干预系统中建立。"
          :closable="false"
          show-icon
        />
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="selectedWarning && selectedWarning.status !== 'handled'"
          type="primary"
          :loading="handlingId === selectedWarning.id"
          @click="markWarningHandledClick(selectedWarning)"
        >
          确认完成跟进
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import MetricCard from '@/components/MetricCard.vue'
import PageHeader from '@/components/PageHeader.vue'
import { listAdminWarnings, markWarningHandled } from '@/api/warnings'
import { formatTime, riskLabel, riskType } from '@/domain/mentalHealth'

const WARNING_RESPONSE_HOURS = 24

const loading = ref(false)
const loadError = ref('')
const handlingId = ref(null)
const warnings = ref([])
const activeFilter = ref('all')
const detailVisible = ref(false)
const selectedWarning = ref(null)

const currentPage = ref(1)
const pageSize = ref(8)

const pendingWarnings = computed(() => warnings.value.filter((item) => item.status !== 'handled'))
const pendingCount = computed(() => pendingWarnings.value.length)
const highPendingCount = computed(
  () => pendingWarnings.value.filter((item) => item.warning_level === 'high').length
)
const overdueCount = computed(() => pendingWarnings.value.filter((item) => isOverdue(item)).length)
const handledTodayCount = computed(
  () => warnings.value.filter((item) => item.status === 'handled' && isToday(item.handled_at)).length
)

const filteredWarnings = computed(() => {
  const rows = warnings.value.filter((item) => {
    if (activeFilter.value === 'pending') return item.status !== 'handled'
    if (activeFilter.value === 'high') return item.warning_level === 'high'
    if (activeFilter.value === 'handled') return item.status === 'handled'
    return true
  })

  return [...rows].sort((a, b) => {
    const priorityDiff = priorityRank(b) - priorityRank(a)
    if (priorityDiff) return priorityDiff
    return new Date(b.created_at || 0) - new Date(a.created_at || 0)
  })
})

const paginatedWarnings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWarnings.value.slice(start, end)
})

watch(activeFilter, () => {
  currentPage.value = 1
})

const loadWarnings = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listAdminWarnings()
    warnings.value = res.data || []
  } catch (error) {
    loadError.value = error?.message || '预警列表加载失败，请重试。'
  } finally {
    loading.value = false
  }
}

const openWarningDetail = (row) => {
  selectedWarning.value = row
  detailVisible.value = true
}

const markWarningHandledClick = async (row) => {
  try {
    await ElMessageBox.confirm(
      '请确认已与该学生进行线下沟通、电话排查或建档记录。确认后此预警标记为处理状态。',
      '确认标记预警',
      {
        confirmButtonText: '完成处置',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return
  }

  handlingId.value = row.id
  try {
    await markWarningHandled(row.id)
    ElMessage.success('跟进记录更新成功')
    detailVisible.value = false
    selectedWarning.value = null
    await loadWarnings()
  } catch (error) {
    ElMessage.error(error?.message || '更新跟进记录失败')
  } finally {
    handlingId.value = null
  }
}

const warningReason = (row) => row?.reason || '近期心境指标偏离预定区间'
const warningSuggestion = (row) => row?.suggestion || '建议安排线下排查，了解其学习压力及睡眠情况。'

const waitingHours = (row) => {
  if (!row?.created_at) return 0
  const elapsed = Date.now() - new Date(row.created_at).getTime()
  return Math.max(0, Math.floor(elapsed / 36e5))
}

const isOverdue = (row) => row.status !== 'handled' && waitingHours(row) >= WARNING_RESPONSE_HOURS

const priorityRank = (row) => {
  if (row.status === 'handled') return 0
  if (isOverdue(row) && row.warning_level === 'high') return 4
  if (row.warning_level === 'high') return 3
  if (isOverdue(row)) return 2
  if (row.warning_level === 'medium') return 1
  return 0
}

const priorityLabel = (row) => {
  if (row.status === 'handled') return '已处置'
  if (isOverdue(row) && row.warning_level === 'high') return '高危超时'
  if (row.warning_level === 'high') return '优先排查'
  if (isOverdue(row)) return '预警超时'
  if (row.warning_level === 'medium') return '建议跟进'
  return '日常关注'
}

const priorityType = (row) => {
  if (row.status === 'handled') return 'success'
  if (row.warning_level === 'high' || isOverdue(row)) return 'danger'
  if (row.warning_level === 'medium') return 'warning'
  return 'info'
}

const priorityTone = (row) => {
  if (row.status === 'handled') return 'done'
  if (isOverdue(row) && row.warning_level === 'high') return 'critical'
  if (row.warning_level === 'high') return 'high'
  if (isOverdue(row)) return 'overdue'
  if (row.warning_level === 'medium') return 'medium'
  return 'normal'
}

const isToday = (value) => {
  if (!value) return false
  const date = new Date(value)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

onMounted(loadWarnings)
</script>

<style scoped>
.warning-workflow {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.triage-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.warning-table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.warning-table-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
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

.warnings-table {
  margin-top: 4px;
}

.priority-cell, .student-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.priority-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  height: 26px;
  padding: 0 10px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: var(--mh-surface);
  color: var(--mh-text);
  font-size: 12px;
  font-weight: 750;
  line-height: 1;
}

.priority-pill--critical {
  border-color: #fca5a5;
  background: #fef2f2;
  color: #b91c1c;
}

.priority-pill--high {
  border-color: #fecaca;
  background: #fff7f7;
  color: #dc2626;
}

.priority-pill--overdue,
.priority-pill--medium {
  border-color: #fed7aa;
  background: #fff7ed;
  color: #b45309;
}

.priority-pill--done,
.priority-pill--normal {
  border-color: var(--mh-line-strong);
  background: #fafafa;
  color: var(--mh-muted);
}

.wait-time-text {
  color: var(--mh-text);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  font-weight: 650;
}

.student-cell strong {
  color: var(--mh-ink);
  font-size: 12.5px;
  white-space: nowrap;
}

.action-cell {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-heading {
  display: flex;
  justify-content: space-between;
  align-items: start;
  border-bottom: 1px solid var(--mh-line);
  padding-bottom: 12px;
}

.heading-left span {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.heading-left strong {
  display: block;
  font-size: 20px;
  color: var(--mh-ink);
  margin-top: 4px;
}

.heading-left p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--mh-muted);
}

.heading-right {
  display: flex;
  gap: 8px;
}

.detail-section h5 {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}

.section-text {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--mh-text);
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  padding: 10px 12px;
  border-radius: var(--mh-radius-md);
}

.suggestion-text {
  font-weight: 600;
  color: var(--mh-ink);
  border-color: var(--mh-primary-soft);
}

@media (max-width: 800px) {
  .triage-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .table-toolbar, .detail-heading {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .heading-right {
    justify-content: flex-start;
  }
}
</style>
