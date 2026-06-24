<template>
  <div class="page emotion-page">
    <PageHeader
      eyebrow="情绪检测"
      title="拍照或上传图片进行情绪识别"
      description="检测结果会保存为历史记录，用于后续趋势分析和风险提醒。"
    />

    <section class="detect-shell">
      <div class="capture-panel">
        <div class="mode-row">
          <el-radio-group v-model="mode">
            <el-radio-button value="camera">摄像头拍照</el-radio-button>
            <el-radio-button value="upload">图片上传</el-radio-button>
          </el-radio-group>
        </div>

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

        <div v-else class="mode-panel upload-panel">
          <el-upload
            drag
            accept="image/jpeg,image/png,image/webp"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload" :size="44"><Plus /></el-icon>
            <div class="el-upload__text">拖拽图片到此处或 <em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 JPG / PNG / WEBP</div>
            </template>
          </el-upload>
          <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="上传预览" />
        </div>

        <div class="btn-row action-row">
          <el-button type="primary" :loading="analyzing" :disabled="!canAnalyze" @click="analyzeImage">
            开始识别
          </el-button>
          <el-button v-if="result" @click="resetAll">重新识别</el-button>
        </div>
      </div>

      <aside class="guide-panel">
        <span>Detection Flow</span>
        <h2>检测前确认</h2>
        <ul>
          <li>保持面部清晰，避免强逆光。</li>
          <li>检测仅用于状态辅助观察。</li>
          <li>结果会进入历史记录和趋势统计。</li>
        </ul>
      </aside>
    </section>

    <section v-if="result" class="result-section">
      <div class="result-grid">
        <div class="business-panel result-card">
          <span class="card-kicker">主导情绪</span>
          <strong>{{ emotionLabel(result.dominant_emotion) }}</strong>
          <p>置信度：{{ (result.confidence * 100).toFixed(1) }}%</p>
        </div>

        <div class="business-panel result-card risk-card">
          <span class="card-kicker">风险判断</span>
          <StatusBadge :type="result.risk_level" :label="riskLabel(result.risk_level)" />
          <p>{{ result.suggestion || '-' }}</p>
        </div>
      </div>

      <div class="business-panel scores-card">
        <div class="panel-title-row">
          <div>
            <h2>情绪得分分布</h2>
            <p>展示本次识别中各情绪类别的相对得分</p>
          </div>
        </div>
        <div v-for="(score, emotion) in result.emotion_scores" :key="emotion" class="score-row">
          <span class="score-label">{{ emotionLabel(emotion) }}</span>
          <el-progress
            :percentage="Number((score * 100).toFixed(1))"
            :stroke-width="14"
            :color="barColor(emotion)"
            :format="() => `${(score * 100).toFixed(1)}%`"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera, Plus, RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { emotionColor as barColor, emotionLabel, riskLabel } from '@/utils/presentation'
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

const canAnalyze = computed(() => {
  if (mode.value === 'camera') return !!capturedImage.value && !analyzing.value
  return !!selectedFile.value && !analyzing.value
})

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
  display: grid;
  gap: var(--mh-space-4);
}

.detect-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: var(--mh-space-4);
  align-items: start;
}

.capture-panel,
.guide-panel {
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: var(--mh-surface);
  box-shadow: var(--mh-shadow-soft);
}

.capture-panel {
  padding: var(--mh-space-4);
}

.mode-row {
  display: flex;
  justify-content: center;
  margin-bottom: var(--mh-space-4);
}

.mode-panel {
  min-height: 260px;
}

.video-wrapper {
  position: relative;
  width: min(100%, 680px);
  aspect-ratio: 4 / 3;
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: #18211f;
}

.video-wrapper video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #ffffff;
  background: #18211f;
}

.upload-panel :deep(.el-upload-dragger) {
  min-height: 240px;
  display: grid;
  align-content: center;
  border-radius: var(--mh-radius);
  border-color: var(--mh-line-strong);
  background: var(--mh-surface-soft);
}

.btn-row {
  display: flex;
  gap: var(--mh-space-3);
  justify-content: center;
  margin-top: var(--mh-space-4);
  flex-wrap: wrap;
}

.action-row {
  padding-top: var(--mh-space-2);
  border-top: 1px solid var(--mh-line);
}

.preview-img {
  display: block;
  max-width: min(380px, 100%);
  margin: var(--mh-space-4) auto 0;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
}

.guide-panel {
  padding: var(--mh-space-5);
}

.guide-panel span,
.card-kicker {
  color: var(--mh-warm);
  font-size: 12px;
  font-weight: 820;
}

.guide-panel h2 {
  margin: 10px 0 0;
  color: var(--mh-ink);
  font-size: 19px;
}

.guide-panel ul {
  display: grid;
  gap: 10px;
  margin: var(--mh-space-4) 0 0;
  padding: 0 0 0 18px;
  color: var(--mh-text);
  line-height: 1.7;
}

.result-section {
  display: grid;
  gap: var(--mh-space-4);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--mh-space-4);
}

.result-card strong {
  display: block;
  margin-top: 10px;
  color: var(--mh-ink);
  font-size: 28px;
}

.result-card p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  line-height: 1.7;
}

.risk-card {
  border-left: 5px solid var(--mh-warm);
}

.score-row {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr);
  align-items: center;
  gap: var(--mh-space-3);
  margin-bottom: 14px;
}

.score-label {
  color: var(--mh-text);
  font-weight: 720;
}

@media (max-width: 900px) {
  .detect-shell,
  .result-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .score-row {
    grid-template-columns: 1fr;
  }
}
</style>
