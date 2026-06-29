<template>
  <div class="page video-analysis-page">
    <PageHeader
      eyebrow="留存视频复核"
      title="视频会话工作台"
      description="选择学生留存视频，完成抽帧识别、过程复核和风险信号整理。"
    >
      <template #actions>
        <el-button :loading="historyLoading" @click="loadHistory">刷新历史会话</el-button>
      </template>
    </PageHeader>

    <section class="video-summary" aria-label="视频会话概览">
      <div class="summary-item">
        <span>当前任务</span>
        <strong>{{ selectedStudentName }}</strong>
        <small>{{ selectedClassName }}</small>
      </div>
      <div class="summary-item">
        <span>历史会话</span>
        <strong>{{ historyStats.total }}</strong>
        <small>已完成 {{ historyStats.completed }} 条</small>
      </div>
      <div class="summary-item is-risk">
        <span>高风险记录</span>
        <strong>{{ historyStats.highRisk }}</strong>
        <small>来自已完成视频会话</small>
      </div>
      <div class="summary-item is-file">
        <span>最近留存文件</span>
        <strong :title="historyStats.latestFile">{{ historyStats.latestFile }}</strong>
        <small>{{ historyStats.latestStudent }}</small>
      </div>
    </section>

    <section class="video-workbench" aria-label="视频会话任务区">
      <VideoSessionSelector
        v-model:selected-class-id="selectedClassId"
        v-model:selected-student-id="selectedStudentId"
        v-model:frame-count="frameCount"
        :classes="classes"
        :students="students"
        :check-result="checkResult"
        :video-duration="videoDuration"
        :capture-interval-ms="captureIntervalMs"
        :primary-button-label="primaryButtonLabel"
        :primary-button-type="primaryButtonType"
        :primary-button-loading="primaryButtonLoading"
        :primary-button-disabled="primaryButtonDisabled"
        @class-change="onClassChange"
        @student-change="onStudentChange"
        @primary-action="handlePrimaryAction"
      />

      <div class="analysis-stage">
        <VideoCapturePanel
          :phase="phase"
          :can-start="canStart"
          @video-element="setVideoElement"
          @video-meta="onVideoMeta"
          @video-ended="onVideoEnded"
        />

        <VideoSessionProgress
          :phase="phase"
          :completed-frame-count="completedFrameCount"
          :frame-count="frameCount"
          :progress-percentage="progressPercentage"
          :has-frame-results="frameResults.length > 0"
        />
      </div>
    </section>

    <section class="analysis-results" :class="{ 'is-empty': !hasAnalysisResults }" aria-label="视频会话结果区">
      <template v-if="hasAnalysisResults">
        <VideoAssessmentReport :session-summary="sessionSummary" />
        <VideoEmotionCurve :frame-results="frameResults" />
        <VideoFrameResultsTable :frame-results="frameResults" />
      </template>
      <div v-else class="result-empty">
        <div>
          <strong>结果区等待会话数据</strong>
          <p>完成一次抽帧分析后，这里会显示风险等级、情绪曲线和逐帧复核明细。</p>
        </div>
        <span>未开始</span>
      </div>
    </section>

    <VideoSessionHistory
      v-model:current-page="historyCurrentPage"
      v-model:page-size="historyPageSize"
      :sessions="historySessions"
      :loading="historyLoading"
      @refresh="loadHistory"
      @detail="viewDetail"
    />

    <VideoSessionDetailDialog v-model="detailVisible" :detail-session="detailSession" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import VideoAssessmentReport from '@/components/video-analysis/VideoAssessmentReport.vue'
import VideoCapturePanel from '@/components/video-analysis/VideoCapturePanel.vue'
import VideoEmotionCurve from '@/components/video-analysis/VideoEmotionCurve.vue'
import VideoFrameResultsTable from '@/components/video-analysis/VideoFrameResultsTable.vue'
import VideoSessionDetailDialog from '@/components/video-analysis/VideoSessionDetailDialog.vue'
import VideoSessionHistory from '@/components/video-analysis/VideoSessionHistory.vue'
import VideoSessionProgress from '@/components/video-analysis/VideoSessionProgress.vue'
import VideoSessionSelector from '@/components/video-analysis/VideoSessionSelector.vue'
import { listAdminClasses } from '@/api/classes'
import { listStudents } from '@/api/users'
import { checkStudentVideo, getVideoSession, listVideoSessions } from '@/api/video'
import { useVideoSessionAnalysis } from '@/composables/useVideoSessionAnalysis'

const students = ref([])
const classes = ref([])
const selectedClassId = ref(null)
const selectedStudentId = ref(null)
const checkResult = ref(undefined)
const frameCount = ref(20)

const historySessions = ref([])
const historyLoading = ref(false)
const historyCurrentPage = ref(1)
const historyPageSize = ref(6)
const detailVisible = ref(false)
const detailSession = ref(null)

const selectedClassName = computed(() => {
  const item = classes.value.find((current) => current.id === selectedClassId.value)
  return item?.name || '未选择班级'
})

const selectedStudentName = computed(() => {
  const item = students.value.find((current) => current.id === selectedStudentId.value)
  return item?.real_name || item?.username || '未选择学生'
})

const hasAnalysisResults = computed(() => frameResults.value.length > 0 || Boolean(sessionSummary.value))

const historyStats = computed(() => {
  const completed = historySessions.value.filter((item) => item.status === 'completed')
  const highRisk = completed.filter((item) => item.risk_level === 'high')
  const latest = historySessions.value[0]

  return {
    total: historySessions.value.length,
    completed: completed.length,
    highRisk: highRisk.length,
    latestFile: latest?.video_filename || '暂无记录',
    latestStudent: latest?.student_name ? `${latest.class_name || '未分班'} / ${latest.student_name}` : '等待会话记录',
  }
})

const {
  phase,
  videoRef,
  videoDuration,
  captureIntervalMs,
  frameResults,
  sessionSummary,
  canStart,
  completedFrameCount,
  progressPercentage,
  primaryButtonLabel,
  primaryButtonType,
  primaryButtonLoading,
  primaryButtonDisabled,
  handleStart,
  handlePrimaryAction,
  onVideoMeta,
  onVideoEnded,
  clearLastAnalyzedVideo,
  clearLastAnalyzedVideoIfStudentChanged,
} = useVideoSessionAnalysis({
  selectedStudentId,
  checkResult,
  frameCount,
  refreshStudentCheck: onStudentChange,
  refreshHistory: loadHistory,
})

async function loadStudents() {
  try {
    const [studentRes, classRes] = await Promise.all([
      listStudents(),
      listAdminClasses(),
    ])
    students.value = (studentRes.data?.items || studentRes.data || []).filter((item) => item.role === 'student')
    classes.value = classRes.data || []
  } catch {
    students.value = []
    classes.value = []
  }
}

function onClassChange() {
  selectedStudentId.value = null
  checkResult.value = undefined
  clearLastAnalyzedVideo()
}

async function onStudentChange(value) {
  checkResult.value = null
  clearLastAnalyzedVideoIfStudentChanged(value)
  if (!value) {
    checkResult.value = undefined
    return
  }
  try {
    const res = await checkStudentVideo(value)
    checkResult.value = res.data
  } catch {
    checkResult.value = { available: false, hint: '留存视频检测失败' }
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await listVideoSessions({ limit: 50 })
    historySessions.value = res.data?.items || []
    historyCurrentPage.value = 1
  } finally {
    historyLoading.value = false
  }
}

async function viewDetail(id) {
  try {
    const res = await getVideoSession(id)
    detailSession.value = res.data
    detailVisible.value = true
  } catch {
    ElMessage.error('获取会话详情失败')
  }
}

function setVideoElement(element) {
  videoRef.value = element
}

onMounted(() => {
  loadStudents()
  loadHistory()
})

watch(historyPageSize, () => {
  historyCurrentPage.value = 1
})
</script>

<style scoped>
.video-analysis-page {
  display: grid;
  max-width: 100%;
  gap: 16px;
  overflow-x: hidden;
}

.video-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  display: grid;
  min-width: 0;
  gap: 6px;
  padding: 14px 16px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
}

.summary-item span {
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 800;
}

.summary-item strong {
  overflow: hidden;
  color: var(--mh-ink);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-item small {
  overflow: hidden;
  color: var(--mh-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-item.is-risk strong {
  color: var(--mh-danger);
}

.summary-item.is-file strong {
  font-size: 16px;
  line-height: 1.35;
}

.video-workbench {
  display: grid;
  grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
  align-items: start;
  gap: 16px;
}

.analysis-stage {
  display: grid;
  min-width: 0;
  gap: 12px;
}

.analysis-results {
  display: grid;
  grid-template-columns: minmax(300px, 0.82fr) minmax(0, 1.18fr);
  gap: 16px;
}

.analysis-results :deep(.frame-table-card) {
  grid-column: 1 / -1;
}

.analysis-results.is-empty {
  display: block;
}

.result-empty {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 96px;
  padding: 18px 20px;
  border: 1px dashed var(--mh-line-strong);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
}

.result-empty strong {
  color: var(--mh-ink);
  font-size: 16px;
}

.result-empty p {
  margin: 6px 0 0;
  color: var(--mh-muted);
  line-height: 1.6;
}

.result-empty span {
  flex: 0 0 auto;
  padding: 6px 10px;
  border-radius: var(--mh-radius-sm);
  background: var(--mh-surface-muted);
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 800;
}

@media (max-width: 720px) {
  .video-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .video-workbench,
  .analysis-results {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .video-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-item {
    padding: 10px;
  }

  .summary-item strong {
    font-size: 18px;
  }

  .summary-item.is-file {
    grid-column: auto;
  }

  .summary-item.is-file strong {
    font-size: 14px;
  }

  .result-empty {
    align-items: flex-start;
    flex-direction: column;
  }

  .video-workbench {
    max-height: 740px;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .analysis-results.is-empty {
    display: none;
  }

  .history-card {
    max-height: 360px;
    overflow-x: hidden;
    overflow-y: auto;
  }
}
</style>
