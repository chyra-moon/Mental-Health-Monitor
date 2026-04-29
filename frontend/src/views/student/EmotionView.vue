<template>
  <div class="emotion-page">
    <div class="page-header">
      <div>
        <h2>情绪识别</h2>
        <p>支持摄像头拍照和图片上传识别</p>
      </div>
    </div>

    <el-radio-group v-model="mode" class="mode-switch">
      <el-radio-button value="camera">摄像头拍照</el-radio-button>
      <el-radio-button value="upload">图片上传</el-radio-button>
    </el-radio-group>

    <div v-if="mode === 'camera'" class="mode-panel">
      <div class="video-wrapper">
        <video ref="videoRef" autoplay playsinline muted></video>
        <div v-if="!cameraReady" class="camera-placeholder">正在启动摄像头...</div>
      </div>
      <div class="btn-row">
        <el-button type="primary" :icon="Camera" :disabled="!cameraReady" @click="capturePhoto">拍照</el-button>
        <el-button :icon="RefreshRight" :disabled="!capturedImage" @click="retake">重新拍照</el-button>
      </div>
      <img v-if="capturedImage" :src="capturedImage" class="preview-img" alt="拍照预览" />
    </div>

    <div v-else class="mode-panel">
      <el-upload
        drag
        accept="image/jpeg,image/png,image/webp"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload" :size="48"><Plus /></el-icon>
        <div class="el-upload__text">拖拽图片到此处或 <em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 JPG / PNG / WEBP</div>
        </template>
      </el-upload>
      <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="上传预览" />
    </div>

    <div class="btn-row">
      <el-button type="primary" :loading="analyzing" :disabled="!canAnalyze" @click="analyzeImage">开始识别</el-button>
      <el-button v-if="result" @click="resetAll">重新识别</el-button>
    </div>

    <div v-if="result" class="result-section">
      <el-divider />
      <h3>识别结果</h3>

      <div class="result-grid">
        <el-card class="result-card emotion-card" shadow="never">
          <div class="emotion-label">{{ emotionLabel(result.dominant_emotion) }}</div>
          <div class="confidence">置信度：{{ (result.confidence * 100).toFixed(1) }}%</div>
        </el-card>

        <el-card class="result-card risk-card" shadow="never">
          <div class="risk-badge" :class="'risk-' + result.risk_level">
            {{ riskLabel(result.risk_level) }}
          </div>
          <p class="suggestion">{{ result.suggestion || '-' }}</p>
        </el-card>
      </div>

      <el-card class="scores-card" shadow="never">
        <h4>情绪得分分布</h4>
        <div v-for="(score, emotion) in result.emotion_scores" :key="emotion" class="score-row">
          <span class="score-label">{{ emotionLabel(emotion) }}</span>
          <el-progress
            :percentage="Number((score * 100).toFixed(1))"
            :stroke-width="16"
            :color="barColor(emotion)"
            :format="() => `${(score * 100).toFixed(1)}%`"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera, Plus, RefreshRight } from '@element-plus/icons-vue'
import http from '@/api/http'

const mode = ref('camera')
const videoRef = ref(null)
const cameraReady = ref(false)
const capturedImage = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const analyzing = ref(false)
const result = ref(null)

let mediaStream = null

const EMOTION_MAP = {
  happy: { label: '开心', color: '#67c23a' },
  sad: { label: '悲伤', color: '#409eff' },
  angry: { label: '愤怒', color: '#f56c6c' },
  fear: { label: '恐惧', color: '#e6a23c' },
  disgust: { label: '厌恶', color: '#909399' },
  surprise: { label: '惊讶', color: '#9c27b0' },
  neutral: { label: '平静', color: '#67c23a' },
}

const RISK_MAP = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
}

const canAnalyze = computed(() => {
  if (mode.value === 'camera') return !!capturedImage.value && !analyzing.value
  return !!selectedFile.value && !analyzing.value
})

const emotionLabel = (value) => EMOTION_MAP[value]?.label || value || '-'
const barColor = (value) => EMOTION_MAP[value]?.color || '#909399'
const riskLabel = (value) => RISK_MAP[value] || value || '-'

async function startCamera() {
  if (mediaStream) return
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
    mediaStream = stream
    await nextTick()
    const video = videoRef.value
    if (!video) return
    video.srcObject = stream
    await video.play().catch(() => {})
    cameraReady.value = true
  } catch {
    ElMessage.error('无法启动摄像头，请检查权限设置')
    mode.value = 'upload'
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }
  cameraReady.value = false
}

function clearPreview() {
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = null
}

function clearInputs() {
  capturedImage.value = null
  selectedFile.value = null
  clearPreview()
}

function resetAll() {
  result.value = null
  clearInputs()
  if (mode.value === 'camera') {
    stopCamera()
    startCamera()
  }
}

function capturePhoto() {
  const video = videoRef.value
  if (!video) return
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  capturedImage.value = canvas.toDataURL('image/jpeg', 0.92)
  result.value = null
  stopCamera()
}

function retake() {
  capturedImage.value = null
  result.value = null
  stopCamera()
  startCamera()
}

function handleFileChange(file) {
  clearPreview()
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null
}

async function analyzeImage() {
  if (!canAnalyze.value) {
    ElMessage.warning('请先准备图片')
    return
  }

  analyzing.value = true
  try {
    let blob
    if (mode.value === 'camera') {
      const response = await fetch(capturedImage.value)
      blob = await response.blob()
    } else {
      blob = selectedFile.value
    }

    const formData = new FormData()
    formData.append('file', blob, 'face.jpg')

    const res = await http.post('/emotion/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    })

    if (res.data) {
      result.value = res.data
    } else {
      ElMessage.warning(res.message || '未检测到人脸')
    }
  } catch {
    ElMessage.error('识别失败，请稍后重试')
  } finally {
    analyzing.value = false
  }
}

watch(mode, async (nextMode, prevMode) => {
  if (prevMode) {
    result.value = null
    clearInputs()
  }

  if (nextMode === 'camera') {
    await startCamera()
  } else {
    stopCamera()
  }
})

onMounted(() => {
  if (mode.value === 'camera') {
    startCamera()
  }
})

onUnmounted(() => {
  stopCamera()
  clearPreview()
})
</script>

<style scoped>
.emotion-page {
  max-width: 760px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 6px;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.mode-switch {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.mode-panel {
  margin-bottom: 16px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 520px;
  min-height: 360px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.video-wrapper video {
  width: 100%;
  height: 100%;
  display: block;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: #000;
}

.btn-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
  flex-wrap: wrap;
}

.preview-img {
  display: block;
  max-width: 360px;
  width: 100%;
  margin: 16px auto 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

.result-section {
  margin-top: 8px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.result-card {
  text-align: center;
}

.emotion-label {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.confidence {
  font-size: 14px;
  color: #909399;
}

.risk-badge {
  display: inline-block;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}

.risk-low {
  background: #f0f9eb;
  color: #67c23a;
}

.risk-medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.risk-high {
  background: #fef0f0;
  color: #f56c6c;
}

.suggestion {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.scores-card {
  margin-top: 16px;
}

.scores-card h4 {
  margin: 0 0 16px;
}

.score-row {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.score-label {
  color: #606266;
}

@media (max-width: 720px) {
  .result-grid {
    grid-template-columns: 1fr;
  }

  .video-wrapper {
    min-height: 260px;
  }
}
</style>
