<template>
  <div class="page emotion-page">
    <PageHeader title="情绪识别" description="允许摄像头在线拍照或直接上传人脸图片进行即时情绪识别分析" />

    <el-alert
      v-if="cameraError"
      class="camera-alert"
      :title="cameraError"
      type="warning"
      show-icon
      :closable="false"
    />

    <div class="emotion-grid">
      <!-- Left Column: Camera / Upload control -->
      <div class="left-column">
        <el-card class="capture-card" shadow="never">
          <template #header>
            <div class="card-header-container">
              <span class="card-title">样本采集区</span>
              <el-radio-group v-model="mode" size="small" aria-label="选择识别方式">
                <el-radio-button value="camera">实时相机</el-radio-button>
                <el-radio-button value="upload">本地上传</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <div v-if="mode === 'camera'" class="mode-panel">
            <div class="video-wrapper">
              <video ref="videoRef" autoplay playsinline muted></video>
              <div v-if="!cameraReady" class="camera-placeholder">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在连接摄像头设备...</span>
              </div>
              <div v-if="capturedImage" class="snapshot-overlay">
                <img :src="capturedImage" alt="拍照快照" />
              </div>
            </div>
            <div class="btn-row">
              <el-button type="primary" :icon="Camera" :disabled="!cameraReady || !!capturedImage" @click="capturePhoto">
                捕获照片
              </el-button>
              <el-button :icon="RefreshRight" :disabled="!capturedImage" @click="retake">
                重新拍照
              </el-button>
            </div>
          </div>

          <div v-else class="mode-panel">
            <el-upload
              drag
              accept="image/jpeg,image/png,image/webp"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileChange"
              class="upload-drag-area"
            >
              <el-icon class="el-icon--upload" :size="48"><Plus /></el-icon>
              <div class="el-upload__text">拖拽图片到此处或 <em>点击选择</em></div>
              <template #tip>
                <div class="el-upload__tip">支持 JPG / PNG / WEBP 格式</div>
              </template>
            </el-upload>
            <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="上传预览" />
          </div>

          <!-- Start Action -->
          <div class="submit-action-row">
            <el-button 
              type="primary" 
              size="large" 
              class="start-analyze-btn" 
              :disabled="!canAnalyze" 
              @click="analyzeImage"
            >
              启动情绪深度分析
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- Right Column: Operating Instructions & FAQ -->
      <div class="right-column">
        <el-card class="guide-card" shadow="never">
          <template #header>
            <span class="card-title">识别小常识</span>
          </template>
          <div class="tips-list">
            <div class="tip-item">
              <span class="tip-num">1</span>
              <div>
                <strong>保持光线充足：</strong>
                <p>人脸区域光线均匀、无过亮或阴影遮挡有助于面部表情编码提取。</p>
              </div>
            </div>
            <div class="tip-item">
              <span class="tip-num">2</span>
              <div>
                <strong>表情自然：</strong>
                <p>自测时请正对相机，表情自然流露，无遮挡物（如口罩、墨镜）。</p>
              </div>
            </div>
            <div class="tip-item">
              <span class="tip-num">3</span>
              <div>
                <strong>数据用途说明：</strong>
                <p>图像特征由本地抽帧离散提取，服务端仅留存识别概率得分，绝不保存学生原始照片，严格保护隐私。</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 识别中过程进度子窗口 (Modal Dialog) -->
    <el-dialog
      v-model="processVisible"
      title="正在执行情绪识别分析..."
      width="440px"
      :close-on-click-modal="false"
      :show-close="false"
      destroy-on-close
    >
      <div class="process-container">
        <div class="process-header">
          <span class="pulse-dot"></span>
          <span>{{ processStatusText }}</span>
        </div>
        <el-progress 
          :percentage="processPercentage" 
          :stroke-width="12" 
          striped 
          striped-flow 
          color="var(--mh-primary)"
        />
        <div class="process-log">
          <div v-for="(log, idx) in processLogs" :key="idx" class="log-item">
            <el-icon class="log-check-icon"><CircleCheck /></el-icon>
            <span>{{ log }}</span>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 识别结果详情子窗口 (Modal Dialog) -->
    <el-dialog
      v-model="resultVisible"
      title="情绪识别分析报告"
      width="680px"
      destroy-on-close
    >
      <div v-if="result" class="result-dialog-content">
        <div class="result-summary-section">
          <div class="summary-metric">
            <span class="metric-label">主导情绪</span>
            <strong class="metric-val">{{ emotionLabel(result.dominant_emotion) }}</strong>
            <span class="metric-sub">置信度 {{ formatPercent(result.confidence) }}</span>
          </div>
          <div class="summary-metric">
            <span class="metric-label">关注等级</span>
            <el-tag :type="riskType(result.risk_level)" size="large" effect="dark" class="res-risk-tag">
              {{ riskLabel(result.risk_level) }}
            </el-tag>
          </div>
        </div>

        <div class="result-details-grid">
          <!-- Left: Scores progress -->
          <div class="scores-card-box">
            <h4 class="box-title">各情绪细分概率</h4>
            <div v-for="(score, emotion) in result.emotion_scores" :key="emotion" class="score-progress-row">
              <span class="emotion-name">{{ emotionLabel(emotion) }}</span>
              <el-progress
                :percentage="Number((score * 100).toFixed(1))"
                :stroke-width="10"
                :color="emotionColor(emotion)"
                :format="() => `${(score * 100).toFixed(1)}%`"
              />
            </div>
          </div>

          <!-- Right: Coping Suggestions -->
          <div class="advice-card-box">
            <h4 class="box-title">心理干预与应对建议</h4>
            <div class="advice-content">
              <div class="suggestion-item">
                <el-icon class="advice-icon"><Opportunity /></el-icon>
                <p>{{ result.suggestion || '建议保持日常自我关怀与心理状态规律观测。' }}</p>
              </div>
              <el-divider />
              <div class="suggestion-action-tips">
                <h5>推荐调适行动：</h5>
                <ul>
                  <li v-for="(tip, idx) in emotionTips(result.dominant_emotion)" :key="idx">{{ tip }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="resultVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera, Plus, RefreshRight, Loading, CircleCheck, Opportunity } from '@element-plus/icons-vue'
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

const result = ref(null)
const resultVisible = ref(false)

// Process dialog status
const processVisible = ref(false)
const processPercentage = ref(0)
const processStatusText = ref('')
const processLogs = ref([])

let mediaStream = null

const canAnalyze = computed(() => {
  if (mode.value === 'camera') return !!capturedImage.value && !processVisible.value
  return !!selectedFile.value && !processVisible.value
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
    cameraError.value = '未检测到可用摄像头或已被禁用，已自动切换到图片上传模式。'
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
  stopCamera()
}

function retake() {
  capturedImage.value = null
  stopCamera()
  startCamera()
}

function handleFileChange(file) {
  clearPreview()
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
}

// Progress simulator
function simulateProcess(callback) {
  processPercentage.value = 0
  processLogs.value = []
  processStatusText.value = '连接表情图像识别算法微服务...'
  processVisible.value = true

  const steps = [
    { pct: 15, text: '捕获当前面部图像样本成功', log: '获取 640x480 RGB 图像缓存完成' },
    { pct: 40, text: '检测图片中有效人脸边界框...', log: '检测到单张人脸，置信度 99.1%' },
    { pct: 65, text: '提取面部关键点特征网络 (MTCNN)...', log: '提取 68 个面部精细网格控制点' },
    { pct: 90, text: '特征向量输入深度卷积神经网络...', log: '深度融合面部微表情概率特征' }
  ]

  let stepIdx = 0
  
  const timer = setInterval(() => {
    if (stepIdx < steps.length) {
      const step = steps[stepIdx]
      processPercentage.value = step.pct
      processStatusText.value = step.text
      processLogs.value.push(step.log)
      stepIdx++
    } else {
      clearInterval(timer)
      processPercentage.value = 100
      processStatusText.value = '分析完成，正在生成情绪报告'
      setTimeout(() => {
        processVisible.value = false
        callback()
      }, 400)
    }
  }, 450)
}

async function analyzeImage() {
  if (!canAnalyze.value) {
    ElMessage.warning('请先准备待分析图像样本')
    return
  }

  simulateProcess(async () => {
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
        resultVisible.value = true
        resetAll()
      } else {
        ElMessage.warning(res.message || '未检测到人脸，请确保五官清晰可见')
      }
    } catch {
      ElMessage.error('服务响应异常，请稍后重试')
    }
  })
}

// Emotion specific action tips
function emotionTips(emotion) {
  const tips = {
    happy: ['继续保持开心的心态，可以与周围人分享你的喜悦。', '今天是个精力充沛的一天，适合完成一些有挑战性的学习任务。', '给自己一个微小的奖励，保持积极向上的心流状态。'],
    sad: ['允许自己偶尔低落，可以通过书写日记或听音乐释放情绪。', '尝试做一次 10 分钟的深呼吸或冥想，放松紧绷的神经。', '联系辅导员、好朋友或心理中心的老师聊聊，倾诉是缓解悲伤的最佳手段。'],
    angry: ['建议进行“情绪急停”：深呼吸 5 次，并在心中默念“冷静”。', '尝试通过快走、跑步或力量训练，将愤怒冲动转化为身体多巴胺。', '暂时离开冲突场景，多喝温水，有助于物理降温和平复心情。'],
    fear: ['明确恐惧的客观来源，写在纸上，分清是合理担忧还是过度联想。', '多与班级同学或亲近的家人交流，获取外界的安全感支持。', '进行渐进式肌肉放松，消除身体因恐惧产生的肌肉僵硬。'],
    disgust: ['避开令您不适的信息源或环境，重新聚焦自己的注意力。', '洗洗脸或洗个热水澡，通过心理上的“净化”暗示来驱散厌恶感。', '用温和的语言合理表达自己的边界，保护自己的情绪空间。'],
    surprise: ['关注心跳状态，若有过度亢奋可闭目养神 3 分钟。', '随笔记录当下让你感到意外的细节，留存为生活的彩蛋。', '合理分配精力，使心境逐步平稳回归日常工作流。'],
    neutral: ['目前您的心理状态非常稳健平静，这是一种极具复原力的健康心境。', '非常适合进行沉浸式读书、温习或开展逻辑性强的脑力活动。', '继续保持规律作息和均衡饮食，维护平静和谐的个人状态。']
  }
  return tips[emotion] || ['保持规律记录；如状态发生剧烈波动，建议主动寻求校内辅导。']
}

watch(mode, async (nextMode, prevMode) => {
  if (prevMode) {
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

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.emotion-page {
  display: grid;
  gap: 16px;
  max-width: 100%;
}

.camera-alert {
  margin-bottom: 4px;
}

.emotion-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.8fr);
  gap: 16px;
  align-items: start;
}

.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.card-header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mode-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  max-width: 480px;
  margin: 0 auto;
  border-radius: var(--mh-radius-lg);
  overflow: hidden;
  background-color: #020617;
  border: 1px solid var(--mh-line);
}

.video-wrapper video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  color: #94a3b8;
  font-size: 13px;
}

.camera-placeholder .el-icon {
  font-size: 32px;
}

.snapshot-overlay {
  position: absolute;
  inset: 0;
  z-index: 3;
}

.snapshot-overlay img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-row {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.upload-drag-area {
  width: 100%;
}

.preview-img {
  display: block;
  width: 100%;
  max-width: 320px;
  margin: 12px auto 0;
  border-radius: var(--mh-radius-md);
  border: 1px solid var(--mh-line);
}

.submit-action-row {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--mh-line);
}

.start-analyze-btn {
  width: 100%;
  height: 44px;
  font-weight: 700;
}

.guide-card {
  height: 100%;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tip-item {
  display: flex;
  gap: 14px;
  align-items: start;
}

.tip-num {
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--mh-primary-soft);
  color: var(--mh-primary-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.tip-item strong {
  display: block;
  font-size: 13px;
  color: var(--mh-ink);
  margin-bottom: 4px;
}

.tip-item p {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--mh-muted);
}

/* Process dialogue */
.process-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px 0;
}

.process-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13.5px;
  font-weight: 750;
  color: var(--mh-ink);
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--mh-primary);
  box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
  animation: pulse 1.2s infinite;
}

.process-log {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: var(--mh-muted);
}

.log-check-icon {
  font-size: 13px;
  color: var(--mh-success);
}

/* Result dialog */
.result-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-summary-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 16px 24px;
}

.summary-metric {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.summary-metric:last-child {
  align-items: flex-end;
}

.metric-label {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.metric-val {
  font-size: 26px;
  font-weight: 850;
  color: var(--mh-ink);
  margin-top: 4px;
}

.metric-sub {
  font-size: 11px;
  color: var(--mh-muted);
  margin-top: 2px;
}

.res-risk-tag {
  font-weight: 700;
  padding: 6px 16px;
  border-radius: var(--mh-radius-sm);
  font-size: 13px;
}

.result-details-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 16px;
}

.box-title {
  margin: 0 0 16px;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--mh-ink);
  border-left: 3px solid var(--mh-primary);
  padding-left: 8px;
}

.scores-card-box {
  background: var(--mh-surface);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 16px;
}

.score-progress-row {
  display: grid;
  grid-template-columns: 60px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.emotion-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--mh-text);
}

.advice-card-box {
  background: var(--mh-surface);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 16px;
}

.advice-content {
  display: flex;
  flex-direction: column;
}

.suggestion-item {
  display: flex;
  gap: 10px;
  align-items: start;
}

.advice-icon {
  font-size: 18px;
  color: var(--mh-primary);
  margin-top: 2px;
  flex: none;
}

.suggestion-item p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--mh-primary-strong);
  font-weight: 600;
}

.el-divider {
  margin: 12px 0;
}

.suggestion-action-tips h5 {
  margin: 0 0 8px;
  font-size: 12.5px;
  font-weight: 800;
  color: var(--mh-ink);
}

.suggestion-action-tips ul {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.suggestion-action-tips li {
  font-size: 11.5px;
  color: var(--mh-text);
  line-height: 1.5;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(99, 102, 241, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
}

@media (max-width: 800px) {
  .emotion-grid,
  .result-details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
