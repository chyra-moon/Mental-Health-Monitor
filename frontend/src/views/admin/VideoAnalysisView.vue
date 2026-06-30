<template>
  <div class="page video-analysis-page">
    <PageHeader
      title="视频分析"
    />

    <!-- Block 1: Top overview statistics -->
    <section class="video-summary" v-loading="historyLoading" aria-label="视频会话概览">
      <MetricCard label="当前对象" :value="selectedStudentName" :note="selectedClassName" tone="neutral" icon="user" compact />
      <MetricCard label="分析记录总数" :value="historyStats.total" unit="场" :note="`已分析完成 ${historyStats.completed} 场`" tone="info" icon="video" compact />
      <MetricCard label="高危预警会话" :value="historyStats.highRisk" unit="场" note="触发高风险跟进警报" :tone="historyStats.highRisk ? 'danger' : 'stable'" icon="warning" compact />
      <MetricCard label="最近记录" :value="historyStats.latestFile" :note="historyStats.latestStudent" tone="neutral" icon="folder" compact />
    </section>

    <!-- Block 2: Middle control area (Form + Camera simulator) -->
    <section class="video-workbench" aria-label="视频会话任务区">
      <!-- Selector control card -->
      <div class="selector-container">
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
      </div>

      <!-- Camera viewport card -->
      <div class="camera-container">
        <VideoCapturePanel
          @video-element="setVideoElement"
          @video-meta="onVideoMeta"
          @video-ended="onVideoEnded"
        />
      </div>
    </section>

    <!-- Block 3: Bottom historical records table -->
    <section class="video-history-section" aria-label="历史会话列表">
      <VideoSessionHistory
        v-model:current-page="historyCurrentPage"
        v-model:page-size="historyPageSize"
        :sessions="historySessions"
        :loading="historyLoading"
        @refresh="loadHistory"
        @detail="viewDetail"
      />
    </section>

    <!-- 抽帧分析运行中 + 分析结果生成子窗口 (Dialog) -->
    <el-dialog
      v-model="analysisDialogVisible"
      title="视频分析报告"
      width="960px"
      :close-on-click-modal="phase !== 'running'"
      :show-close="phase !== 'running'"
      destroy-on-close
    >
      <div v-if="phase === 'running'" class="running-modal-body">
        <VideoSessionProgress
          :phase="phase"
          :completed-frame-count="completedFrameCount"
          :frame-count="frameCount"
          :progress-percentage="progressPercentage"
          :has-frame-results="frameResults.length > 0"
        />
      </div>
      
      <div v-else-if="phase === 'completed' && sessionSummary" class="result-modal-grid">
        <!-- Left Column: Report Details -->
        <div class="report-box">
          <VideoAssessmentReport :session-summary="sessionSummary" />
        </div>
        
        <!-- Right Column: Curves & Details Table -->
        <div class="charts-box-col">
          <VideoEmotionCurve :frame-results="frameResults" />
          <VideoFrameResultsTable :frame-results="frameResults" />
        </div>
      </div>
      
      <template #footer>
        <el-button type="primary" :disabled="phase === 'running'" @click="closeAnalysisDialog">
          确认并关闭
        </el-button>
      </template>
    </el-dialog>

    <!-- 历史详情子窗口 (Dialog) -->
    <VideoSessionDetailDialog v-model="detailVisible" :detail-session="detailSession" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import MetricCard from '@/components/MetricCard.vue'
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

const analysisDialogVisible = ref(false)

const selectedClassName = computed(() => {
  const item = classes.value.find((c) => c.id === selectedClassId.value)
  return item?.name || '未选择班级'
})

const selectedStudentName = computed(() => {
  const item = students.value.find((c) => c.id === selectedStudentId.value)
  return item?.real_name || item?.username || '未选择学生'
})

const historyStats = computed(() => {
  const completed = historySessions.value.filter((item) => item.status === 'completed')
  const highRisk = completed.filter((item) => item.risk_level === 'high')
  const latest = historySessions.value[0]

  return {
    total: historySessions.value.length,
    completed: completed.length,
    highRisk: highRisk.length,
    latestFile: latest ? '已生成报告' : '暂无记录',
    latestStudent: latest?.student_name ? `${latest.class_name || '未分班'} · ${latest.student_name}` : '暂无数据',
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

// Auto open analysis progress dialog when active analysis starts
watch(phase, (newPhase) => {
  if (newPhase === 'running') {
    analysisDialogVisible.value = true
  }
})

function closeAnalysisDialog() {
  analysisDialogVisible.value = false
  clearLastAnalyzedVideo()
}

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
    checkResult.value = { available: false }
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await listVideoSessions({ limit: 100 })
    historySessions.value = res.data?.items || []
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
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.video-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.video-workbench {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 12px;
  align-items: stretch;
  height: 360px;
  min-height: 0;
}

.selector-container,
.camera-container {
  height: 100%;
  min-height: 0;
}

.video-history-section {
  flex: 1;
  min-height: 0;
}

/* Dialog run-time popup layout */
.running-modal-body {
  padding: 8px 0;
}

.result-modal-grid {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.report-box {
  position: sticky;
  top: 0;
}

.charts-box-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

@media (max-width: 900px) {
  .video-workbench {
    grid-template-columns: 1fr;
  }
  .result-modal-grid {
    grid-template-columns: 1fr;
  }
  .report-box {
    position: static;
  }
  .charts-box-col {
    max-height: none;
    overflow-y: visible;
  }
}

@media (max-width: 800px) {
  .video-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
