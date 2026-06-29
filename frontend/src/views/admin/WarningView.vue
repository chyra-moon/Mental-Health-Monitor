<template>
  <div class="page warning-workflow">
    <PageHeader
      title="预警处置"
      description="按风险等级和等待时长查看需要跟进的学生预警，状态标记前请先完成一次线下确认或校内记录"
    >
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

    <section class="triage-summary" aria-label="预警处置概览">
      <el-card shadow="never" class="summary-card">
        <span>待处置预警</span>
        <strong>{{ pendingCount }}</strong>
        <p>需要辅导员或心理中心完成一次确认后再标记状态。</p>
      </el-card>
      <el-card shadow="never" class="summary-card">
        <span>高风险待跟进</span>
        <strong class="risk-high">{{ highPendingCount }}</strong>
        <p>建议优先查看学生、班级、触发原因和系统建议。</p>
      </el-card>
      <el-card shadow="never" class="summary-card">
        <span>超过 24 小时</span>
        <strong class="risk-medium">{{ overdueCount }}</strong>
        <p>以创建时间计算，提示当前状态仍未标记处理。</p>
      </el-card>
      <el-card shadow="never" class="summary-card">
        <span>今日已标记</span>
        <strong>{{ handledTodayCount }}</strong>
        <p>仅表示预警状态已更新，不代表干预流程已结案。</p>
      </el-card>
    </section>

    <el-card class="warning-table-card" shadow="never">
      <template #header>
        <div class="table-toolbar">
          <div>
            <strong>预警列表</strong>
            <small>共 {{ filteredWarnings.length }} 条，按处置优先级和预警时间排序</small>
          </div>
          <el-radio-group v-model="activeFilter" size="small" aria-label="筛选预警状态">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="pending">待处置</el-radio-button>
            <el-radio-button label="high">高风险</el-radio-button>
            <el-radio-button label="handled">已标记</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-empty v-if="!loading && filteredWarnings.length === 0" description="暂无符合条件的风险预警" />
      <el-table v-else v-loading="loading" :data="filteredWarnings" stripe size="small" max-height="520">
        <el-table-column label="处置优先级" min-width="140">
          <template #default="{ row }">
            <div class="priority-cell">
              <el-tag :type="priorityType(row)" effect="plain">{{ priorityLabel(row) }}</el-tag>
              <span v-if="row.status !== 'handled'">{{ waitingHours(row) }} 小时</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="预警时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="学生" min-width="190">
          <template #default="{ row }">
            <div class="student-cell">
              <strong>{{ row.real_name || row.username || '未命名学生' }}</strong>
              <span>{{ row.class_name || '未填写班级' }} · {{ row.username || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="warning_level" label="风险等级" min-width="110">
          <template #default="{ row }">
            <el-tag :type="riskType(row.warning_level)">
              {{ riskLabel(row.warning_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="触发原因" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">{{ warningReason(row) }}</template>
        </el-table-column>
        <el-table-column prop="suggestion" label="系统建议" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">{{ warningSuggestion(row) }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="150">
          <template #default="{ row }">
            <div class="status-cell">
              <el-tag :type="row.status === 'handled' ? 'success' : 'warning'">
                {{ row.status === 'handled' ? '已标记处理' : '待处置' }}
              </el-tag>
              <span v-if="row.handled_at">{{ formatTime(row.handled_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="176" fixed="right">
          <template #default="{ row }">
            <div class="action-cell">
              <el-button size="small" @click="openWarningDetail(row)">查看处置</el-button>
              <el-button
                v-if="row.status !== 'handled'"
                type="primary"
                size="small"
                :loading="handlingId === row.id"
                @click="markWarningHandled(row)"
              >
                标记
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      class="warning-detail-dialog"
      title="预警处置详情"
      width="720px"
      destroy-on-close
    >
      <div v-if="selectedWarning" class="detail-content">
        <div class="detail-heading">
          <div>
            <span>学生</span>
            <strong>{{ selectedWarning.real_name || selectedWarning.username || '未命名学生' }}</strong>
            <p>{{ selectedWarning.class_name || '未填写班级' }} · {{ selectedWarning.username || '-' }}</p>
          </div>
          <div class="detail-tags">
            <el-tag :type="riskType(selectedWarning.warning_level)">
              {{ riskLabel(selectedWarning.warning_level) }}
            </el-tag>
            <el-tag :type="selectedWarning.status === 'handled' ? 'success' : 'warning'" effect="plain">
              {{ selectedWarning.status === 'handled' ? '已标记处理' : '待处置' }}
            </el-tag>
          </div>
        </div>

        <dl class="detail-grid">
          <div>
            <dt>预警时间</dt>
            <dd>{{ formatTime(selectedWarning.created_at) }}</dd>
          </div>
          <div>
            <dt>等待时长</dt>
            <dd>{{ selectedWarning.status === 'handled' ? '已完成状态标记' : `${waitingHours(selectedWarning)} 小时` }}</dd>
          </div>
          <div>
            <dt>处理时间</dt>
            <dd>{{ formatTime(selectedWarning.handled_at) }}</dd>
          </div>
          <div>
            <dt>处置优先级</dt>
            <dd>{{ priorityLabel(selectedWarning) }}</dd>
          </div>
        </dl>

        <section class="detail-section">
          <h3>风险来源</h3>
          <p>{{ warningReason(selectedWarning) }}</p>
        </section>

        <section class="detail-section">
          <h3>系统建议</h3>
          <p>{{ warningSuggestion(selectedWarning) }}</p>
        </section>

        <el-alert
          title="当前接口只支持状态标记"
          type="info"
          show-icon
          :closable="false"
          description="本页的“已标记处理”仅表示管理员已完成一次线下确认或校内记录，并把预警状态更新为已处理。跟进记录、责任分配和干预结案仍需要后续接口接入。"
        />
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="selectedWarning && selectedWarning.status !== 'handled'"
          type="primary"
          :loading="handlingId === selectedWarning.id"
          @click="markWarningHandled(selectedWarning)"
        >
          确认已完成一次跟进
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { listAdminWarnings, markWarningHandled as updateWarningHandled } from '@/api/warnings'
import { formatTime, riskLabel, riskType } from '@/domain/mentalHealth'

const WARNING_RESPONSE_HOURS = 24

const loading = ref(false)
const loadError = ref('')
const handlingId = ref(null)
const warnings = ref([])
const activeFilter = ref('all')
const detailVisible = ref(false)
const selectedWarning = ref(null)

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

const loadWarnings = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listAdminWarnings()
    warnings.value = res.data || []
  } catch (error) {
    loadError.value = error?.message || '预警列表加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

const openWarningDetail = (row) => {
  selectedWarning.value = row
  detailVisible.value = true
}

const markWarningHandled = async (row) => {
  try {
    await ElMessageBox.confirm(
      '请确认已完成一次线下沟通、电话确认或校内记录。该操作只更新预警状态，不会生成干预记录或结案记录。',
      '标记预警状态',
      {
        confirmButtonText: '确认标记',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return
  }

  handlingId.value = row.id
  try {
    await updateWarningHandled(row.id)
    ElMessage.success('已标记为处理状态')
    detailVisible.value = false
    selectedWarning.value = null
    await loadWarnings()
  } catch (error) {
    ElMessage.error(error?.message || '预警状态更新失败，请稍后重试。')
  } finally {
    handlingId.value = null
  }
}

const warningReason = (row) => row?.reason || '系统记录到风险信号变化，当前记录未提供更详细来源。'
const warningSuggestion = (row) => row?.suggestion || '建议结合近期识别记录、测评结果和线下沟通情况再决定后续支持方式。'

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
  if (row.status === 'handled') return '已标记处理'
  if (isOverdue(row) && row.warning_level === 'high') return '高风险超时'
  if (row.warning_level === 'high') return '优先跟进'
  if (isOverdue(row)) return '超过 24 小时'
  if (row.warning_level === 'medium') return '建议待跟进'
  return '常规关注'
}

const priorityType = (row) => {
  if (row.status === 'handled') return 'success'
  if (row.warning_level === 'high' || isOverdue(row)) return 'danger'
  if (row.warning_level === 'medium') return 'warning'
  return 'info'
}

const isToday = (value) => {
  if (!value) return false
  const date = new Date(value)
  const today = new Date()
  return date.getFullYear() === today.getFullYear() && date.getMonth() === today.getMonth() && date.getDate() === today.getDate()
}

onMounted(loadWarnings)
</script>

<style scoped>
.warning-workflow {
  display: grid;
  gap: 16px;
}

.state-alert {
  margin-bottom: 0;
}

.triage-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  min-height: 108px;
}

.summary-card span {
  display: block;
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 800;
}

.summary-card strong {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 28px;
  line-height: 1.2;
}

.summary-card p {
  margin: 10px 0 0;
  color: var(--mh-muted);
  font-size: 13px;
  line-height: 1.6;
}

.risk-high {
  color: var(--mh-danger) !important;
}

.risk-medium {
  color: var(--mh-warning) !important;
}

.warning-table-card {
  min-width: 0;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.table-toolbar strong,
.table-toolbar small {
  display: block;
}

.table-toolbar strong {
  color: var(--mh-ink);
}

.table-toolbar small {
  margin-top: 4px;
  color: var(--mh-muted);
  font-size: 12px;
}

.priority-cell,
.status-cell,
.student-cell,
.action-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.priority-cell span,
.status-cell span,
.student-cell span {
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.4;
}

.student-cell strong {
  color: var(--mh-ink);
}

.action-cell {
  flex-direction: row;
  flex-wrap: wrap;
}

.detail-content {
  display: grid;
  gap: 16px;
}

.detail-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--mh-line);
}

.detail-heading span,
.detail-heading p,
.detail-grid dt {
  color: var(--mh-muted);
  font-size: 13px;
}

.detail-heading strong {
  display: block;
  margin-top: 4px;
  color: var(--mh-ink);
  font-size: 22px;
}

.detail-heading p {
  margin: 6px 0 0;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
}

.detail-grid div {
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface-muted);
}

.detail-grid dt,
.detail-grid dd {
  margin: 0;
}

.detail-grid dd {
  margin-top: 6px;
  color: var(--mh-ink);
  font-weight: 800;
}

.detail-section h3 {
  margin: 0 0 8px;
  color: var(--mh-ink);
  font-size: 15px;
}

.detail-section p {
  margin: 0;
  color: var(--mh-text);
  line-height: 1.7;
}

@media (max-width: 1080px) {
  .triage-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .triage-summary,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .table-toolbar,
  .detail-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .detail-tags {
    justify-content: flex-start;
  }
}
</style>
