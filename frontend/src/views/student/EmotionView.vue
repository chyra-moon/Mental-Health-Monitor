<template>
  <div class="page emotion-page">
    <PageHeader title="情绪识别" description="可使用摄像头拍照或上传图片，识别结果用于个人记录和校内支持参考。" />

    <el-alert
      v-if="cameraError"
      class="state-alert"
      :title="cameraError"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-radio-group v-model="mode" class="mode-switch" aria-label="选择情绪识别方式">
      <el-radio-button value="camera">摄像头拍照</el-radio-button>
      <el-radio-button value="upload">图片上传</el-radio-button>
    </el-radio-group>

    <el-card class="capture-card" shadow="never">
      <div v-if="mode === 'camera'" class="mode-panel">
        <div class="video-wrapper">
          <video ref="videoRef" autoplay playsinline muted aria-label="摄像头预览"></video>
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
          aria-label="上传待识别图片"
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
    </el-card>

    <section v-if="result" class="result-section" aria-live="polite">
      <h3>识别结果</h3>

      <div class="result-grid">
        <el-card class="result-card" shadow="never">
          <span>主导情绪</span>
          <strong>{{ emotionLabel(result.dominant_emotion) }}</strong>
          <p>置信度 {{ (result.confidence * 100).toFixed(1) }}%</p>
        </el-card>

        <el-card class="result-card" shadow="never">
          <span>关注等级</span>
          <el-tag :type="riskType(result.risk_level)" size="large">
            {{ riskLabel(result.risk_level) }}
          </el-tag>
          <p>{{ result.suggestion || '建议结合近期记录继续观察。' }}</p>
        </el-card>
      </div>

      <el-card class="scores-card" shadow="never">
        <template #header>情绪得分分布</template>
        <div v-for="(score, emotion) in result.emotion_scores" :key="emotion" class="score-row">
          <span class="score-label">{{ emotionLabel(emotion) }}</span>
          <el-progress
            :percentage="Number((score * 100).toFixed(1))"
            :stroke-width="16"
            :color="emotionColor(emotion)"
            :format="() => `${(score * 100).toFixed(1)}%`"
          />
        </div>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera, Plus, RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { analyzeEmotionImage } from '@/api/emotion'
import { emotionColor, emotionLabel, riskLabel, riskType } from '@/domain/mentalHealth'

const mode = ref('camera')
const videoRef = ref(null)
const cameraReady = ref(false)
const cameraError = ref('')
const capturedImage = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const analyzing = ref(false)
const result = ref(null)

let mediaStream = null

const canAnalyze = computed(() => {
  if (mode.value === 'camera') return !!capturedImage.value && !analyzing.value
  return !!selectedFile.value && !analyzing.value
})

async function startCamera() {
  if (mediaStream) return
  cameraError.value = ''
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
    cameraError.value = '无法启动摄像头，已切换为图片上传。请检查浏览器权限或使用上传方式。'
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

    const res = await analyzeEmotionImage(blob)

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
  display: grid;
  max-width: 760px;
  margin: 0 auto;
  gap: 16px;
}

.state-alert {
  margin-bottom: 0;
}

.mode-switch {
  display: flex;
  justify-content: center;
}

.capture-card {
  min-width: 0;
}

.mode-panel {
  display: grid;
  gap: 16px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 520px;
  min-height: 300px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: var(--mh-radius-md);
  background: #111827;
}

.video-wrapper video {
  display: block;
  width: 100%;
  height: 100%;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111827;
  color: #f9fafb;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.preview-img {
  display: block;
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
}

.result-section {
  display: grid;
  gap: 16px;
}

.result-section h3 {
  margin: 0;
  color: var(--mh-ink);
  font-size: 18px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.result-card {
  text-align: center;
}

.result-card span {
  display: block;
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 800;
}

.result-card strong {
  display: block;
  margin: 8px 0;
  color: var(--mh-ink);
  font-size: 24px;
}

.result-card p {
  margin: 10px 0 0;
  color: var(--mh-muted);
  line-height: 1.6;
}

.score-row {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.score-label {
  color: var(--mh-text);
}

@media (max-width: 720px) {
  .result-grid {
    grid-template-columns: 1fr;
  }

  .video-wrapper {
    min-height: 260px;
  }
}

@media (max-width: 520px) {
  .btn-row {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
