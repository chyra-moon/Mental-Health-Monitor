<template>
  <div class="emotion-page">
    <h2 class="page-title">情绪识别</h2>

    <!-- 模式切换 -->
    <el-radio-group v-model="mode" class="mode-switch">
      <el-radio-button value="camera">📷 拍照</el-radio-button>
      <el-radio-button value="upload">🖼️ 上传图片</el-radio-button>
    </el-radio-group>

    <!-- 拍照模式 -->
    <div v-if="mode === 'camera'" class="camera-section">
      <div class="video-wrapper" v-show="!capturedImage">
        <video ref="videoRef" autoplay playsinline></video>
        <div class="camera-placeholder" v-if="!cameraReady">
          <p>正在启动摄像头...</p>
        </div>
      </div>
      <div class="btn-row" v-if="cameraReady && !capturedImage">
        <el-button type="primary" @click="capturePhoto" :icon="Camera">拍照</el-button>
      </div>
      <img v-if="capturedImage" :src="capturedImage" class="preview-img" />
      <div class="btn-row" v-if="capturedImage && mode === 'camera'">
        <el-button @click="retake">重拍</el-button>
        <el-button type="primary" :loading="analyzing" @click="analyzeImage">识别情绪</el-button>
      </div>
    </div>

    <!-- 上传模式 -->
    <div v-else class="upload-section">
      <el-upload
        ref="uploadRef"
        drag
        accept="image/jpeg,image/png"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload" :size="48"><Plus /></el-icon>
        <div class="el-upload__text">拖拽图片到此处或 <em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 JPG / PNG 格式</div>
        </template>
      </el-upload>
      <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
      <div class="btn-row" v-if="selectedFile && !result">
        <el-button type="primary" :loading="analyzing" @click="analyzeImage">识别情绪</el-button>
      </div>
    </div>

    <!-- 识别结果 -->
    <div v-if="result" class="result-section">
      <el-divider />
      <h3>识别结果</h3>

      <div class="result-grid">
        <el-card class="result-card emotion-card">
          <div class="emotion-icon">{{ emotionIcon(result.dominant_emotion) }}</div>
          <div class="emotion-label">{{ emotionLabel(result.dominant_emotion) }}</div>
          <div class="confidence">置信度：{{ (result.confidence * 100).toFixed(1) }}%</div>
        </el-card>

        <el-card class="result-card risk-card">
          <div class="risk-badge" :class="'risk-' + result.risk_level">
            {{ riskLabel(result.risk_level) }}
          </div>
          <p class="suggestion">{{ result.suggestion }}</p>
        </el-card>
      </div>

      <!-- 情绪概率分布 -->
      <el-card class="scores-card">
        <h4>情绪概率分布</h4>
        <div v-for="(score, emotion) in result.emotion_scores" :key="emotion" class="score-row">
          <span class="score-label">{{ emotionLabel(emotion) }}</span>
          <el-progress
            :percentage="(score * 100).toFixed(1)"
            :stroke-width="16"
            :color="barColor(emotion)"
            :format="() => (score * 100).toFixed(1) + '%'"
          />
        </div>
      </el-card>

      <div class="btn-row">
        <el-button type="primary" @click="resetPage">再来一次</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Camera } from '@element-plus/icons-vue'
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
let cameraStarted = false

const EMOTION_MAP = {
  happy: { label: '开心', icon: '😊', color: '#67c23a' },
  sad: { label: '悲伤', icon: '😢', color: '#409eff' },
  angry: { label: '愤怒', icon: '😠', color: '#f56c6c' },
  fear: { label: '恐惧', icon: '😨', color: '#909399' },
  disgust: { label: '厌恶', icon: '😣', color: '#e6a23c' },
  surprise: { label: '惊讶', icon: '😲', color: '#409eff' },
  neutral: { label: '平静', icon: '😐', color: '#67c23a' },
}

function emotionLabel(e) {
  return EMOTION_MAP[e]?.label || e
}
function emotionIcon(e) {
  return EMOTION_MAP[e]?.icon || '❓'
}
function barColor(e) {
  return EMOTION_MAP[e]?.color || '#909399'
}
function riskLabel(r) {
  return { low: '低风险 ✅', medium: '中风险 ⚠️', high: '高风险 🚨' }[r] || r
}

// 启动摄像头
function startCamera() {
  if (cameraStarted) return
  cameraStarted = true
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 } })
    .then((stream) => {
      mediaStream = stream
      videoRef.value.srcObject = stream
      cameraReady.value = true
    })
    .catch(() => {
      ElMessage.error('无法启动摄像头，请检查权限设置')
      mode.value = 'upload'
    })
}

function capturePhoto() {
  const video = videoRef.value
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  capturedImage.value = canvas.toDataURL('image/jpeg', 0.9)
  stopCamera()
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop())
    mediaStream = null
  }
  cameraStarted = false
  cameraReady.value = false
}

function retake() {
  capturedImage.value = null
  startCamera()
}

function handleFileChange(file) {
  selectedFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => (previewUrl.value = e.target.result)
  reader.readAsDataURL(file.raw)
}

async function analyzeImage() {
  analyzing.value = true
  try {
    let blob
    if (mode.value === 'camera') {
      const res = await fetch(capturedImage.value)
      blob = await res.blob()
    } else {
      blob = selectedFile.value
    }

    const formData = new FormData()
    formData.append('file', blob, 'face.jpg')

    const res = await http.post('/emotion/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })

    if (res.data) {
      result.value = res.data
    } else {
      ElMessage.warning(res.message || '未检测到人脸')
    }
  } catch (err) {
    ElMessage.error('识别失败，请重试')
  } finally {
    analyzing.value = false
  }
}

function resetPage() {
  result.value = null
  capturedImage.value = null
  selectedFile.value = null
  previewUrl.value = null
  if (mode.value === 'camera') startCamera()
}

onUnmounted(() => stopCamera())
</script>

<style scoped>
.emotion-page {
  max-width: 700px;
  margin: 0 auto;
}
.page-title {
  margin-bottom: 20px;
  font-size: 20px;
}
.mode-switch {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}
.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}
.video-wrapper video {
  width: 100%;
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
}
.preview-img {
  display: block;
  max-width: 300px;
  margin: 16px auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.result-section {
  margin-top: 8px;
}
.result-grid {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.result-card {
  flex: 1;
  text-align: center;
}
.emotion-icon {
  font-size: 48px;
  margin-bottom: 8px;
}
.emotion-label {
  font-size: 20px;
  font-weight: bold;
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
  font-size: 18px;
  font-weight: bold;
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
  margin-bottom: 16px;
}
.score-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.score-label {
  width: 40px;
  text-align: right;
  font-size: 13px;
  color: #606266;
  flex-shrink: 0;
}
.score-row .el-progress {
  flex: 1;
}
</style>
