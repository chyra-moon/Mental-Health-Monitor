<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>视频分析</h2>
        <p>模拟摄像头采集视频，逐帧分析学生情绪变化并生成心理评估报告</p>
      </div>
    </div>

    <!-- 控制栏 -->
    <el-card class="control-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="5">
          <label class="control-label">班级</label>
          <el-select v-model="selectedClassId" placeholder="请选择班级" style="width:100%" @change="onClassChange">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <label class="control-label">学生</label>
          <el-select v-model="selectedStudentId" placeholder="请选择学生" style="width:100%" :disabled="!selectedClassId" @change="onStudentChange">
            <el-option v-for="s in filteredStudents" :key="s.id" :label="s.real_name || s.username" :value="s.id" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <label class="control-label">抽帧数量</label>
          <el-input-number v-model="frameCount" :min="5" :max="60" style="width:100%" />
        </el-col>
        <el-col :span="5">
          <label class="control-label">&nbsp;</label>
          <el-button
            :type="primaryButtonType"
            size="large"
            :disabled="primaryButtonDisabled"
            :loading="primaryButtonLoading"
            @click="handlePrimaryAction"
          >
            {{ primaryButtonLabel }}
          </el-button>
        </el-col>
        <el-col :span="6" class="tr">
          <label class="control-label">&nbsp;</label>
          <div v-if="selectedStudentId && checkResult" class="check-status">
            <span v-if="checkResult.available" class="text-success">检测到最新数据</span>
            <span v-else class="text-warning">{{ checkResult.hint }}</span>
          </div>
          <div v-else-if="selectedStudentId && checkResult === null" class="text-muted">正在检测...</div>
          <div v-if="videoDuration > 0" class="video-info">视频时长: {{ videoDuration.toFixed(1) }}s &nbsp; 间隔: {{ captureIntervalMs }}ms</div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 摄像头模拟区 -->
    <el-card class="camera-card" shadow="never">
      <div class="camera-box" ref="cameraBoxRef">
        <div v-if="phase === 'idle'" class="camera-placeholder">
          <el-button type="primary" size="large" :disabled="!canStart" @click="handleStart">
            打开摄像头，开始采集数据
          </el-button>
        </div>

        <div v-if="phase === 'connecting'" class="camera-placeholder">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p style="margin-top:12px;color:#fff">摄像头启动中...</p>
        </div>

        <video
          v-show="phase === 'playing' || phase === 'summarizing' || phase === 'completed'"
          ref="videoRef"
          class="camera-video"
          playsinline
          muted
          @loadedmetadata="onVideoMeta"
          @ended="onVideoEnded"
        />

        <div v-if="phase === 'summarizing'" class="camera-complete-overlay">
          <span>分析汇总中</span>
        </div>

        <div v-if="phase === 'completed'" class="camera-complete-overlay">
          <span>采集完成</span>
        </div>

        <div v-if="phase === 'playing'" class="recording-dot">
          <span class="dot"></span> REC
        </div>
      </div>
    </el-card>

    <!-- 进度条 -->
    <div v-if="phase === 'playing' || phase === 'summarizing' || (phase === 'completed' && frameResults.length > 0)" class="progress-bar-area">
      <el-progress
        :percentage="progressPercentage"
        :status="phase === 'completed' ? 'success' : ''"
        :stroke-width="12"
      >
        <span class="progress-text">{{ completedFrameCount }} / {{ frameCount }} 帧</span>
      </el-progress>
    </div>

    <!-- 实时分析表格 -->
    <el-card v-if="frameResults.length > 0" class="table-card" shadow="never">
      <template #header>逐帧分析结果</template>
      <el-table :data="frameResults" stripe max-height="320" style="width:100%">
        <el-table-column prop="frame_index" label="帧序号" width="80" align="center" />
        <el-table-column label="时间戳" width="110">
          <template #default="{ row }">{{ (row.timestamp_ms / 1000).toFixed(1) }}s</template>
        </el-table-column>
        <el-table-column label="分析状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.analysis_status === 'pending'" type="info" size="small">分析中</el-tag>
            <el-tag v-else-if="row.analysis_status === 'ok'" type="success" size="small">成功</el-tag>
            <el-tag v-else-if="row.analysis_status === 'no_face'" type="warning" size="small">无人脸</el-tag>
            <el-tag v-else type="danger" size="small">异常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="主导情绪" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.dominant_emotion" :style="{ backgroundColor: barColor(row.dominant_emotion), color:'#fff', border:'none' }" size="small">
              {{ emotionLabel(row.dominant_emotion) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.confidence !== null && row.confidence !== undefined">{{ (row.confidence * 100).toFixed(1) }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="情绪分数分布" min-width="300">
          <template #default="{ row }">
            <div v-if="row.emotion_scores" class="scores-bar">
              <template v-for="(score, emo) in row.emotion_scores" :key="emo">
                <el-tooltip :content="`${emotionLabel(emo)}: ${(score * 100).toFixed(1)}%`" placement="top">
                  <div class="bar-segment" :style="{ width: (score * 100).toFixed(0) + '%', backgroundColor: barColor(emo) }" />
                </el-tooltip>
              </template>
            </div>
            <span v-else class="text-muted">{{ row.error_message || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ECharts -->
    <el-card v-if="frameResults.length > 0" class="chart-card" shadow="never">
      <template #header>情绪变化曲线</template>
      <div ref="chartRef" class="chart-container" />
    </el-card>

    <!-- 汇总评估 -->
    <el-card v-if="sessionSummary" class="summary-card" shadow="never">
      <template #header>心理评估报告</template>
      <el-row :gutter="16">
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">主导情绪</div>
            <el-tag :style="{ backgroundColor: barColor(sessionSummary.dominant_emotion), color:'#fff', border:'none', fontSize:'16px', padding:'6px 16px' }">
              {{ emotionLabel(sessionSummary.dominant_emotion) || '无' }}
            </el-tag>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">负面情绪占比</div>
            <div class="stat-value" :class="sessionSummary.negative_ratio >= 0.3 ? 'text-danger' : 'text-success'">
              {{ (sessionSummary.negative_ratio * 100).toFixed(1) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">风险等级</div>
            <el-tag :type="riskType(sessionSummary.risk_level)" size="large" effect="dark">
              {{ riskLabel(sessionSummary.risk_level) }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
      <el-divider />
      <div class="reason-area">
        <p><strong>评估依据：</strong>{{ sessionSummary.reason }}</p>
        <p><strong>干预建议：</strong>{{ sessionSummary.suggestion }}</p>
      </div>
    </el-card>

    <!-- 历史会话 -->
    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="history-header">
          <span>历史会话</span>
          <el-button size="small" @click="loadHistory" :loading="historyLoading">刷新</el-button>
        </div>
      </template>
      <el-table v-loading="historyLoading" :data="pagedHistorySessions" stripe style="width: 100%">
        <el-table-column prop="class_name" label="班级" width="100" align="center" />
        <el-table-column prop="student_name" label="学生" width="100" />
        <el-table-column label="留存文件" min-width="200">
          <template #default="{ row }">
            <span v-if="row.status === 'completed'">{{ row.video_filename }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'completed'" type="success" size="small">已完成</el-tag>
            <el-tag v-else-if="row.status === 'running'" type="warning" size="small">进行中</el-tag>
            <el-tag v-else type="danger" size="small">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="有效帧" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.status === 'completed'">{{ row.analyzed_frames }} / {{ row.total_frames }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'completed'" :type="riskType(row.risk_level)" size="small">{{ riskLabel(row.risk_level) }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180" />
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewDetail(row.id)">详情</el-button>
            <el-button size="small" type="warning" link @click="handleReplay(row)">回放</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="historySessions.length > historyPageSize" class="pagination-bar">
        <span class="page-total">共 {{ historySessions.length }} 条会话</span>
        <el-pagination
          v-model:current-page="historyCurrentPage"
          v-model:page-size="historyPageSize"
          :page-sizes="[6, 10, 15, 20]"
          :total="historySessions.length"
          background
          layout="sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="会话详情" width="900px" top="3vh">
      <template v-if="detailSession">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="班级">{{ detailSession.session.class_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学生">{{ detailSession.session.student_name }}</el-descriptions-item>
          <el-descriptions-item label="留存文件">{{ detailSession.session.video_filename }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="riskType(detailSession.session.risk_level)" size="small">{{ riskLabel(detailSession.session.risk_level) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="主导情绪">
            <el-tag :style="{ backgroundColor: barColor(detailSession.session.dominant_emotion), color:'#fff', border:'none' }" size="small">
              {{ emotionLabel(detailSession.session.dominant_emotion) || '无' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负面占比">{{ detailSession.session.negative_ratio ? (detailSession.session.negative_ratio * 100).toFixed(1) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="有效帧">{{ detailSession.session.analyzed_frames }} / {{ detailSession.session.total_frames }}</el-descriptions-item>
          <el-descriptions-item label="分析时间">{{ detailSession.session.started_at }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <el-table :data="detailSession.frames" stripe max-height="300" size="small">
          <el-table-column prop="frame_index" label="帧序号" width="80" align="center" />
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.analysis_status === 'ok'" type="success" size="small">成功</el-tag>
              <el-tag v-else-if="row.analysis_status === 'no_face'" type="warning" size="small">无人脸</el-tag>
              <el-tag v-else type="danger" size="small">异常</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="情绪" width="100" align="center">
            <template #default="{ row }">{{ emotionLabel(row.dominant_emotion) }}</template>
          </el-table-column>
          <el-table-column label="置信度" width="90" align="center">
            <template #default="{ row }">{{ row.confidence ? (row.confidence * 100).toFixed(1) + '%' : '-' }}</template>
          </el-table-column>
        </el-table>
        <p v-if="detailSession.session.reason" style="margin-top:12px"><strong>评估依据：</strong>{{ detailSession.session.reason }}</p>
        <p v-if="detailSession.session.suggestion"><strong>建议：</strong>{{ detailSession.session.suggestion }}</p>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import http from '@/api/http'

const EMOTION_MAP = {
  happy: { label: '开心', color: '#67c23a' },
  sad: { label: '悲伤', color: '#409eff' },
  angry: { label: '愤怒', color: '#f56c6c' },
  fear: { label: '恐惧', color: '#e6a23c' },
  disgust: { label: '厌恶', color: '#909399' },
  surprise: { label: '惊讶', color: '#b37feb' },
  neutral: { label: '平静', color: '#67c8b9' },
}
const RISK_MAP = { low: '低风险', medium: '中风险', high: '高风险' }
const RISK_TYPE = { low: 'success', medium: 'warning', high: 'danger' }
const emotionLabel = (v) => EMOTION_MAP[v]?.label || v || '-'
const barColor = (v) => EMOTION_MAP[v]?.color || '#909399'
const riskLabel = (v) => RISK_MAP[v] || v || '-'
const riskType = (v) => RISK_TYPE[v] || 'info'

// ========== 控制状态 ==========
const students = ref([])
const classes = ref([])
const selectedClassId = ref(null)
const selectedStudentId = ref(null)
const checkResult = ref(undefined)  // null=检测中 undefined=未检测 {available, hint, ...}
const frameCount = ref(20)

const filteredStudents = computed(() => {
  if (!selectedClassId.value) return []
  return students.value.filter((s) => s.class_id === selectedClassId.value)
})

// ========== 分析状态 ==========
const phase = ref('idle')
const sessionId = ref(null)
const streamSrc = ref(null)
const lastAnalyzedFilename = ref(null)
const lastAnalyzedStudentId = ref(null)
const videoDuration = ref(0)
const captureIntervalMs = ref(0)
const frameResults = ref([])
const sessionSummary = ref(null)
const videoRef = ref(null)
const cameraBoxRef = ref(null)
let captureTimer = null
let frameIndex = 0
let totalFrameCount = 0
let canvasEl = null
let canvasCtx = null
let finishStarted = false
let activeUploads = 0
let queuedUploads = []
let uploadPromises = []

const MAX_PARALLEL_UPLOADS = 2
const VIDEO_PLAYBACK_RATE = 1
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// ========== 历史 ==========
const historySessions = ref([])
const historyLoading = ref(false)
const historyCurrentPage = ref(1)
const historyPageSize = ref(6)
const detailVisible = ref(false)
const detailSession = ref(null)

const canStart = computed(() =>
  selectedStudentId.value && checkResult.value?.available && phase.value === 'idle'
)
const completedFrameCount = computed(() =>
  frameResults.value.filter((f) => f.analysis_status !== 'pending').length
)
const progressPercentage = computed(() => {
  if (!frameCount.value) return 0
  return Math.min(100, Math.round((completedFrameCount.value / frameCount.value) * 100))
})
const primaryButtonLabel = computed(() => {
  if (phase.value === 'completed') return '再来一次'
  if (phase.value === 'idle') return '打开摄像头，开始采集数据'
  if (phase.value === 'summarizing') return '分析汇总中...'
  return '正在分析中...'
})
const primaryButtonType = computed(() => (phase.value === 'completed' ? 'success' : 'primary'))
const primaryButtonLoading = computed(() => phase.value === 'connecting' || phase.value === 'summarizing')
const primaryButtonDisabled = computed(() => {
  if (phase.value === 'completed') return false
  if (phase.value === 'idle') return !canStart.value
  return true
})
const pagedHistorySessions = computed(() => {
  const start = (historyCurrentPage.value - 1) * historyPageSize.value
  return historySessions.value.slice(start, start + historyPageSize.value)
})

// ========== ECharts ==========
const chartRef = ref(null)
let chartInst = null

function buildChartOption() {
  const frames = frameResults.value
  const xData = frames.map((_, i) => `帧${i + 1}`)
  const emotionKeys = ['happy', 'sad', 'angry', 'fear', 'disgust', 'surprise', 'neutral']
  const series = emotionKeys.map((emo) => ({
    name: EMOTION_MAP[emo].label,
    type: 'line',
    data: frames.map((f) => (f.emotion_scores ? f.emotion_scores[emo] : null)),
    smooth: true,
    lineStyle: { color: EMOTION_MAP[emo].color, width: 2 },
    itemStyle: { color: EMOTION_MAP[emo].color },
    connectNulls: false,
  }))
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: emotionKeys.map((e) => EMOTION_MAP[e].label), top: 0 },
    grid: { left: 48, right: 16, top: 40, bottom: 24 },
    xAxis: { type: 'category', data: xData, name: '帧序号' },
    yAxis: { type: 'value', min: 0, max: 1, name: '置信度' },
    series,
  }
}

function updateChart() {
  if (!chartRef.value) return
  if (!chartInst) chartInst = echarts.init(chartRef.value)
  chartInst.setOption(buildChartOption(), true)
}

function resizeChart() { chartInst?.resize() }

// ========== 初始加载 ==========
async function loadStudents() {
  try {
    const [studentRes, classRes] = await Promise.all([
      http.get('/users/admin/list'),
      http.get('/admin/classes'),
    ])
    students.value = (studentRes.data?.items || studentRes.data || []).filter((u) => u.role === 'student')
    classes.value = classRes.data || []
  } catch {}
}

function onClassChange() {
  selectedStudentId.value = null
  checkResult.value = undefined
  lastAnalyzedFilename.value = null
  lastAnalyzedStudentId.value = null
}

async function onStudentChange(val) {
  checkResult.value = null
  if (val !== lastAnalyzedStudentId.value) {
    lastAnalyzedFilename.value = null
    lastAnalyzedStudentId.value = null
  }
  if (!val) { checkResult.value = undefined; return }
  try {
    const res = await http.get(`/admin/video/check/${val}`)
    checkResult.value = res.data
  } catch {
    checkResult.value = { available: false, hint: '检测失败' }
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await http.get('/admin/video/sessions', { params: { limit: 50 } })
    historySessions.value = res.data?.items || []
    historyCurrentPage.value = 1
  } finally {
    historyLoading.value = false
  }
}

async function viewDetail(id) {
  try {
    const res = await http.get(`/admin/video/sessions/${id}`)
    detailSession.value = res.data
    detailVisible.value = true
  } catch {
    ElMessage.error('获取详情失败')
  }
}

function handleReplay(row) {
  ElMessage.info('回放功能开发中')
}

// ========== 视频元数据 ==========
function onVideoMeta() {
  const vid = videoRef.value
  if (!vid || !vid.duration) return
  videoDuration.value = vid.duration
  totalFrameCount = frameCount.value
  captureIntervalMs.value = Math.round((vid.duration * 1000) / totalFrameCount)
  resizeCaptureCanvas()
}

// ========== 开始采集 ==========
async function handleStart(filename = null) {
  if (!selectedStudentId.value) return
  if (!filename && !canStart.value) return

  phase.value = 'connecting'
  frameResults.value = []
  sessionSummary.value = null
  frameIndex = 0
  finishStarted = false
  resetUploadState()
  if (chartInst) { chartInst.dispose(); chartInst = null }

  try {
    const formData = new FormData()
    formData.append('student_id', selectedStudentId.value)
    formData.append('frame_count', frameCount.value)
    if (filename) formData.append('filename', filename)
    const res = await http.post('/admin/video/sessions', formData)
    sessionId.value = res.data.id
    streamSrc.value = res.data.stream_src
  } catch (e) {
    phase.value = 'idle'
    // 错误信息从拦截器获取，可能是 "当前没有xxx的最新数据"
    return
  }

  await wait(1500)

  const vid = videoRef.value
  if (!vid || !streamSrc.value) { phase.value = 'idle'; return }

  // 用 fetch 带 token 获取视频（<video> 原生请求不带 Authorization）
  try {
    const token = localStorage.getItem('token')
    const resp = await fetch(streamSrc.value, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const blob = await resp.blob()
    if (vid.src && vid.src.startsWith('blob:')) URL.revokeObjectURL(vid.src)
    vid.src = URL.createObjectURL(blob)
  } catch (e) {
    phase.value = 'idle'
    ElMessage.error('视频加载失败: ' + (e.message || '未知'))
    return
  }

  try {
    await waitForVideoMetadata(vid)
    vid.pause()
    vid.playbackRate = VIDEO_PLAYBACK_RATE
    vid.currentTime = 0
  } catch (e) {
    phase.value = 'idle'
    ElMessage.error(e.message || '视频元数据加载失败')
    return
  }
  onVideoMeta()

  ensureCaptureCanvas()

  totalFrameCount = frameCount.value
  frameIndex = 0
  phase.value = 'playing'
  await captureFramesDuringPlayback()
  await finishSession()
}

async function handlePrimaryAction() {
  if (phase.value === 'completed') {
    const filename = lastAnalyzedStudentId.value === selectedStudentId.value ? lastAnalyzedFilename.value : null
    resetAnalysisForNextRun()
    if (filename) {
      await handleStart(filename)
      return
    }
    if (selectedStudentId.value) {
      await onStudentChange(selectedStudentId.value)
      if (checkResult.value?.available) await handleStart()
    }
    return
  }

  await handleStart()
}

function resetAnalysisForNextRun() {
  clearTimeout(captureTimer)
  resetUploadState()
  frameResults.value = []
  sessionSummary.value = null
  sessionId.value = null
  streamSrc.value = null
  videoDuration.value = 0
  captureIntervalMs.value = 0
  frameIndex = 0
  totalFrameCount = 0
  finishStarted = false
  phase.value = 'idle'
  if (chartInst) {
    chartInst.dispose()
    chartInst = null
  }
  const vid = videoRef.value
  if (vid?.src?.startsWith('blob:')) URL.revokeObjectURL(vid.src)
  if (vid) vid.removeAttribute('src')
}

function ensureCaptureCanvas() {
  if (!canvasEl) {
    canvasEl = document.createElement('canvas')
    canvasCtx = canvasEl.getContext('2d')
  }
  resizeCaptureCanvas()
}

function resizeCaptureCanvas() {
  if (!canvasEl) return

  const vid = videoRef.value
  const sourceWidth = vid?.videoWidth || 640
  const sourceHeight = vid?.videoHeight || 480
  const maxSide = 960
  const scale = Math.min(1, maxSide / Math.max(sourceWidth, sourceHeight))

  canvasEl.width = Math.max(1, Math.round(sourceWidth * scale))
  canvasEl.height = Math.max(1, Math.round(sourceHeight * scale))
}

async function waitForVideoMetadata(vid) {
  if (Number.isFinite(vid.duration) && vid.duration > 0 && vid.readyState >= 1) return

  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      cleanup()
      reject(new Error('视频元数据加载超时'))
    }, 10000)
    const cleanup = () => {
      clearTimeout(timeout)
      vid.removeEventListener('loadedmetadata', onLoaded)
      vid.removeEventListener('error', onError)
    }
    const onLoaded = () => {
      cleanup()
      resolve()
    }
    const onError = () => {
      cleanup()
      reject(new Error('视频元数据加载失败'))
    }
    vid.addEventListener('loadedmetadata', onLoaded, { once: true })
    vid.addEventListener('error', onError, { once: true })
    vid.load()
  })
}

async function captureFramesDuringPlayback() {
  const vid = videoRef.value
  if (!vid || !Number.isFinite(vid.duration) || vid.duration <= 0) {
    ElMessage.error('视频时长无效，无法抽帧')
    return
  }

  const total = frameCount.value
  const intervalMs = (vid.duration * 1000) / total
  vid.playbackRate = VIDEO_PLAYBACK_RATE

  try {
    await vid.play()
  } catch (e) {
    ElMessage.error('视频播放失败: ' + (e.message || '未知'))
    return
  }

  const startedAt = performance.now()
  for (let idx = 0; idx < total; idx++) {
    if (phase.value !== 'playing') return

    const targetElapsedMs = Math.min(vid.duration * 1000 - 50, (idx + 0.5) * intervalMs)
    const delayMs = targetElapsedMs - (performance.now() - startedAt)
    if (delayMs > 0) await wait(delayMs)
    if (phase.value !== 'playing' || vid.ended) return
    await waitForFrameReady(vid)

    const timestampMs = Math.round(vid.currentTime * 1000)
    try {
      canvasCtx.drawImage(vid, 0, 0, canvasEl.width, canvasEl.height)
      const blob = await canvasToBlob()
      enqueueFrameUpload(idx, timestampMs, blob)
    } catch {
      upsertFrameResult({
        frame_index: idx, timestamp_ms: timestampMs,
        analysis_status: 'error', dominant_emotion: null,
        confidence: null, emotion_scores: null, error_message: '抽帧失败',
      })
    }

    frameIndex = idx + 1
    await new Promise((resolve) => requestAnimationFrame(resolve))
  }
  vid.pause()
}

async function waitForFrameReady(vid) {
  if (vid.readyState >= 2) return

  await new Promise((resolve) => {
    const timeout = setTimeout(() => {
      cleanup()
      resolve()
    }, 2000)
    const cleanup = () => {
      clearTimeout(timeout)
      vid.removeEventListener('loadeddata', onReady)
      vid.removeEventListener('canplay', onReady)
    }
    const onReady = () => {
      cleanup()
      resolve()
    }
    vid.addEventListener('loadeddata', onReady, { once: true })
    vid.addEventListener('canplay', onReady, { once: true })
  })
}

function canvasToBlob() {
  return new Promise((resolve, reject) => {
    canvasEl.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('toBlob failed'))
    }, 'image/jpeg', 0.85)
  })
}

function resetUploadState() {
  activeUploads = 0
  queuedUploads = []
  uploadPromises = []
}

function enqueueFrameUpload(idx, timestampMs, blob) {
  upsertFrameResult({
    frame_index: idx,
    timestamp_ms: timestampMs,
    analysis_status: 'pending',
    dominant_emotion: null,
    confidence: null,
    emotion_scores: null,
    error_message: '等待分析',
  })

  const promise = new Promise((resolve) => {
    queuedUploads.push({
      run: () => uploadFrame(idx, timestampMs, blob),
      resolve,
    })
    pumpUploadQueue()
  })
  uploadPromises.push(promise)
}

function pumpUploadQueue() {
  while (activeUploads < MAX_PARALLEL_UPLOADS && queuedUploads.length > 0) {
    const item = queuedUploads.shift()
    activeUploads++
    item.run().finally(() => {
      activeUploads--
      item.resolve()
      pumpUploadQueue()
    })
  }
}

async function uploadFrame(idx, timestampMs, blob) {
  try {
    const fd = new FormData()
    fd.append('file', blob, `frame_${idx}.jpg`)
    fd.append('frame_index', idx)
    fd.append('timestamp_ms', timestampMs)

    const res = await http.post(`/admin/video/sessions/${sessionId.value}/frames`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    })

    upsertFrameResult({
      frame_index: idx,
      timestamp_ms: timestampMs,
      analysis_status: res.data?.analysis_status || 'error',
      dominant_emotion: res.data?.dominant_emotion || null,
      confidence: res.data?.confidence || null,
      emotion_scores: res.data?.emotion_scores || null,
      error_message: res.data?.error_message || null,
    })
  } catch {
    upsertFrameResult({
      frame_index: idx, timestamp_ms: timestampMs,
      analysis_status: 'error', dominant_emotion: null,
      confidence: null, emotion_scores: null, error_message: '请求失败',
    })
  }
}

function upsertFrameResult(result) {
  const index = frameResults.value.findIndex((item) => item.frame_index === result.frame_index)
  if (index >= 0) frameResults.value[index] = result
  else frameResults.value.push(result)
  frameResults.value.sort((a, b) => a.frame_index - b.frame_index)
  updateChart()
}

async function finishSession() {
  if (finishStarted) return
  finishStarted = true
  clearTimeout(captureTimer)
  phase.value = 'summarizing'

  if (!sessionId.value) return

  await Promise.allSettled(uploadPromises)

  try {
    const res = await http.post(`/admin/video/sessions/${sessionId.value}/complete`)
    sessionSummary.value = res.data
    lastAnalyzedFilename.value = res.data?.video_filename || null
    lastAnalyzedStudentId.value = selectedStudentId.value
    phase.value = 'completed'
    // 刷新检查结果（视频已重命名）
    if (selectedStudentId.value) onStudentChange(selectedStudentId.value)
  } catch {
    phase.value = 'completed'
    ElMessage.error('汇总评估失败')
  }

  loadHistory()
}

function onVideoEnded() {
  if (phase.value === 'playing' && frameIndex < totalFrameCount) {
    finishSession()
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  loadStudents()
  loadHistory()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  clearTimeout(captureTimer)
  if (chartInst) { chartInst.dispose(); chartInst = null }
  window.removeEventListener('resize', resizeChart)
  // 清理 blob URL
  const vid = videoRef.value
  if (vid?.src?.startsWith('blob:')) URL.revokeObjectURL(vid.src)
})

watch(() => frameResults.value.length, () => {
  nextTick(() => updateChart())
})
watch(historyPageSize, () => {
  historyCurrentPage.value = 1
})
</script>

<style scoped>
.page { max-width: 100%; overflow-x: hidden; padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 20px; color: #303133; }
.page-header p { margin: 0; font-size: 13px; color: #909399; }

.control-card { margin-bottom: 16px; }
.control-label { display: block; margin-bottom: 4px; font-size: 13px; color: #606266; }
.check-status { padding-top: 4px; font-size: 13px; min-height: 32px; display: flex; align-items: center; }
.text-success { color: #67c23a; }
.text-warning { color: #e6a23c; }
.text-muted { color: #909399; }
.video-info { font-size: 12px; color: #909399; text-align: right; }
.tr { text-align: right; }

.camera-card { margin-bottom: 16px; }
.camera-box {
  position: relative; width: 100%; min-height: 360px;
  background: #000; border-radius: 8px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}
.camera-placeholder {
  display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff;
}
.camera-video { width: 100%; height: 100%; object-fit: contain; max-height: 480px; }
.camera-complete-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,.6); display: flex; align-items: center; justify-content: center;
  color: #67c23a; font-size: 24px; font-weight: 700;
}
.recording-dot {
  position: absolute; top: 12px; right: 16px;
  display: flex; align-items: center; gap: 6px;
  color: #f56c6c; font-size: 12px; font-weight: 600; letter-spacing: 1px;
}
.dot { width: 10px; height: 10px; border-radius: 50%; background: #f56c6c; animation: blink 1s infinite; }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.3; } }

.progress-bar-area { margin-bottom: 16px; }
.progress-text { font-size: 13px; color: #303133; }

.table-card { margin-bottom: 16px; }
.scores-bar { display: flex; height: 16px; border-radius: 3px; overflow: hidden; background: #f0f0f0; min-width: 200px; }
.bar-segment { height: 100%; transition: width .3s; }

.chart-card { margin-bottom: 16px; }
.chart-container { width: 100%; height: 360px; }

.summary-card { margin-bottom: 16px; }
.stat-item { text-align: center; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
.reason-area p { margin: 8px 0; color: #606266; line-height: 1.8; }

.history-card { margin-bottom: 16px; overflow: hidden; }
.history-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 16px;
  flex-wrap: wrap;
}
.page-total { color: #7d8fb3; font-size: 13px; }
</style>
