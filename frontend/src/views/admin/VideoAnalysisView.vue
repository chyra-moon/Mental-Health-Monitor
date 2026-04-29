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
          <el-button type="primary" size="large" :disabled="!canStart" :loading="phase === 'connecting'" @click="handleStart">
            {{ phase === 'idle' ? '打开摄像头，开始采集数据' : '分析进行中...' }}
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
          v-show="phase === 'playing' || phase === 'completed'"
          ref="videoRef"
          class="camera-video"
          autoplay
          playsinline
          muted
          @loadedmetadata="onVideoMeta"
          @ended="onVideoEnded"
        />

        <div v-if="phase === 'completed'" class="camera-complete-overlay">
          <span>采集完成</span>
        </div>

        <div v-if="phase === 'playing'" class="recording-dot">
          <span class="dot"></span> REC
        </div>
      </div>
    </el-card>

    <!-- 进度条 -->
    <div v-if="phase === 'playing' || (phase === 'completed' && frameResults.length > 0)" class="progress-bar-area">
      <el-progress
        :percentage="frameResults.length > 0 ? Math.round((frameResults.length / frameCount) * 100) : 0"
        :status="phase === 'completed' ? 'success' : ''"
        :stroke-width="12"
      >
        <span class="progress-text">{{ frameResults.length }} / {{ frameCount }} 帧</span>
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
            <el-tag v-if="row.analysis_status === 'ok'" type="success" size="small">成功</el-tag>
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
      <el-table v-loading="historyLoading" :data="historySessions" stripe>
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
let uploadQueue = Promise.resolve()
let finishStarted = false
let pendingCaptures = 0

// ========== 历史 ==========
const historySessions = ref([])
const historyLoading = ref(false)
const detailVisible = ref(false)
const detailSession = ref(null)

const canStart = computed(() =>
  selectedStudentId.value && checkResult.value?.available && phase.value === 'idle'
)

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
}

async function onStudentChange(val) {
  checkResult.value = null
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
async function handleStart() {
  if (!canStart.value) return

  phase.value = 'connecting'
  frameResults.value = []
  sessionSummary.value = null
  frameIndex = 0
  finishStarted = false
  pendingCaptures = 0
  uploadQueue = Promise.resolve()
  if (chartInst) { chartInst.dispose(); chartInst = null }

  try {
    const formData = new FormData()
    formData.append('student_id', selectedStudentId.value)
    formData.append('frame_count', frameCount.value)
    const res = await http.post('/admin/video/sessions', formData)
    sessionId.value = res.data.id
    streamSrc.value = res.data.stream_src
  } catch (e) {
    phase.value = 'idle'
    // 错误信息从拦截器获取，可能是 "当前没有xxx的最新数据"
    return
  }

  await new Promise((r) => setTimeout(r, 1500))

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
    await vid.play()
  } catch (e) {
    phase.value = 'idle'
    ElMessage.error('视频播放失败')
    return
  }

  phase.value = 'playing'

  if (!vid.duration) {
    await new Promise((resolve) => {
      const check = () => { if (vid.duration) resolve(); else setTimeout(check, 100) }
      check()
    })
  }
  onVideoMeta()

  ensureCaptureCanvas()

  totalFrameCount = frameCount.value
  frameIndex = 0
  startCaptureLoop()
}

function startCaptureLoop() {
  const intervalMs = captureIntervalMs.value
  if (intervalMs <= 0) return
  captureNextFrame(0, intervalMs)
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
  const maxSide = 1280
  const scale = Math.min(1, maxSide / Math.max(sourceWidth, sourceHeight))

  canvasEl.width = Math.max(1, Math.round(sourceWidth * scale))
  canvasEl.height = Math.max(1, Math.round(sourceHeight * scale))
}

function captureNextFrame(delayMs, intervalMs) {
  captureTimer = setTimeout(async () => {
    if (phase.value !== 'playing' || frameIndex >= totalFrameCount) {
      await finishSession()
      return
    }

    const vid = videoRef.value
    if (!vid || vid.ended) {
      await finishSession()
      return
    }
    if (vid.readyState < 2) {
      captureNextFrame(50, intervalMs)
      return
    }

    const timestampMs = Math.round(vid.currentTime * 1000)
    const idx = frameIndex
    frameIndex++
    pendingCaptures++

    try {
      canvasCtx.drawImage(vid, 0, 0, canvasEl.width, canvasEl.height)
    } catch {
      pendingCaptures--
      recordFrameResult({
        frame_index: idx, timestamp_ms: timestampMs,
        analysis_status: 'error', dominant_emotion: null,
        confidence: null, emotion_scores: null, error_message: '抽帧失败',
      })
      captureNextFrame(intervalMs, intervalMs)
      return
    }

    let blob
    try {
      blob = await new Promise((resolve, reject) => {
        canvasEl.toBlob((b) => { if (b) resolve(b); else reject(new Error('toBlob failed')) }, 'image/jpeg', 0.85)
      })
    } catch {
      recordFrameResult({
        frame_index: idx, timestamp_ms: timestampMs,
        analysis_status: 'error', dominant_emotion: null,
        confidence: null, emotion_scores: null, error_message: '抽帧失败',
      })
      pendingCaptures--
      captureNextFrame(intervalMs, intervalMs)
      return
    }

    enqueueFrameUpload(idx, timestampMs, blob)
    pendingCaptures--

    if (frameIndex >= totalFrameCount) {
      await finishSession()
      return
    }
    captureNextFrame(intervalMs, intervalMs)
  }, delayMs)
}

function enqueueFrameUpload(idx, timestampMs, blob) {
  uploadQueue = uploadQueue
    .catch(() => {})
    .then(() => uploadFrame(idx, timestampMs, blob))
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

    recordFrameResult({
      frame_index: idx,
      timestamp_ms: timestampMs,
      analysis_status: res.data?.analysis_status || 'error',
      dominant_emotion: res.data?.dominant_emotion || null,
      confidence: res.data?.confidence || null,
      emotion_scores: res.data?.emotion_scores || null,
      error_message: res.data?.error_message || null,
    })
  } catch {
    recordFrameResult({
      frame_index: idx, timestamp_ms: timestampMs,
      analysis_status: 'error', dominant_emotion: null,
      confidence: null, emotion_scores: null, error_message: '请求失败',
    })
  }
}

function recordFrameResult(result) {
  frameResults.value.push(result)
  frameResults.value.sort((a, b) => a.frame_index - b.frame_index)
  updateChart()
}

async function finishSession() {
  if (finishStarted) return
  finishStarted = true
  clearTimeout(captureTimer)
  phase.value = 'completed'

  if (!sessionId.value) return

  while (pendingCaptures > 0) {
    await new Promise((resolve) => setTimeout(resolve, 50))
  }
  await uploadQueue.catch(() => {})

  try {
    const res = await http.post(`/admin/video/sessions/${sessionId.value}/complete`)
    sessionSummary.value = res.data
    // 刷新检查结果（视频已重命名）
    if (selectedStudentId.value) onStudentChange(selectedStudentId.value)
  } catch {
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
</script>

<style scoped>
.page { padding: 0; }
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

.history-card { margin-bottom: 16px; }
.history-header { display: flex; justify-content: space-between; align-items: center; }
</style>
