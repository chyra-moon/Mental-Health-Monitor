<template>
  <div class="page emotion-page">
    <PageHeader title="情绪识别" />

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
              class="upload-frame"
            >
              <div class="upload-frame-content" :class="{ 'is-filled': previewUrl }">
                <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="上传预览" />
                <div v-else class="upload-empty-state">
                  <el-icon class="el-icon--upload" :size="42"><Plus /></el-icon>
                  <strong>选择待识别图片</strong>
                  <span>支持 JPG / PNG / WEBP</span>
                </div>
                <div v-if="previewUrl" class="upload-change-hint">点击或拖拽可更换图片</div>
              </div>
            </el-upload>
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
      width="min(1040px, 92vw)"
      class="emotion-result-dialog"
      destroy-on-close
    >
      <div v-if="result" class="result-dialog-content">
        <div class="result-overview-grid">
          <section class="result-image-panel">
            <div class="section-head">
              <span>原始样本</span>
              <strong>{{ analysisSourceLabel }}</strong>
            </div>
            <div class="result-image-frame">
              <img v-if="resultImageSrc" :src="resultImageSrc" alt="本次识别原图" />
              <div v-else class="result-image-empty">暂无样本图像</div>
            </div>
            <div class="result-image-meta">
              <span>{{ analysisCapturedAt }}</span>
              <span>{{ resultImageResolution }}</span>
            </div>
          </section>

          <section class="result-main-panel">
            <div class="result-summary-section">
              <MetricCard
                label="主导情绪"
                :value="emotionLabel(result.dominant_emotion)"
                :note="`置信度 ${formatPercent(result.confidence)}`"
                :tone="result.risk_level || 'neutral'"
                icon="monitor"
                compact
              />
              <MetricCard
                label="关注等级"
                :value="riskLabel(result.risk_level)"
                note="系统风险评估结果"
                :tone="result.risk_level || 'neutral'"
                icon="warning"
                compact
              />
            </div>

            <div class="result-brief-grid">
              <div class="brief-card">
                <span>综合判断</span>
                <strong>{{ getRiskSummary(result) }}</strong>
                <p>{{ getObservationText(result) }}</p>
              </div>
              <div class="brief-card">
                <span>关注重点</span>
                <strong>{{ getCareLevelText(result) }}</strong>
                <p>{{ getCareActionText(result) }}</p>
              </div>
              <div class="brief-card">
                <span>记录建议</span>
                <strong>本周持续记录</strong>
                <p>建议在相近时间段完成 2-3 次自测，观察情绪是否稳定回落。</p>
              </div>
            </div>
          </section>
        </div>

        <div class="result-details-grid">
          <div class="scores-card-box">
            <div class="box-title-row">
              <h4 class="box-title">情绪概率明细</h4>
              <span>按模型输出概率排序</span>
            </div>
            <el-table
              :data="emotionScoreRows"
              class="emotion-score-table"
              size="small"
              :empty-text="'暂无概率明细'"
            >
              <el-table-column prop="label" label="情绪" width="86" />
              <el-table-column label="概率" width="86" align="center">
                <template #default="{ row }">{{ formatPercent(row.score) }}</template>
              </el-table-column>
              <el-table-column label="分布" min-width="180">
                <template #default="{ row }">
                  <el-progress
                    class="score-table-progress"
                    :percentage="row.percentage"
                    :stroke-width="8"
                    :color="emotionColor(row.emotion)"
                    :format="() => `${row.percentage}%`"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="150" />
            </el-table>
          </div>

          <div class="advice-card-box">
            <div class="box-title-row">
              <h4 class="box-title">心理干预与应对建议</h4>
              <span>{{ riskLabel(result.risk_level) }}</span>
            </div>
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

        <div class="result-next-card">
          <div>
            <span>记录归档</span>
            <strong>本次分析已写入识别记录</strong>
            <p>可在识别记录中再次打开完整版报告，查看概率明细和干预建议。</p>
          </div>
          <el-button @click="goToEmotionRecords">查看识别记录</el-button>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Camera, Plus, RefreshRight, Loading, CircleCheck, Opportunity } from '@element-plus/icons-vue'
import MetricCard from '@/components/MetricCard.vue'
import PageHeader from '@/components/PageHeader.vue'
import { analyzeEmotionImage } from '@/api/emotion'
import { emotionColor, emotionLabel, formatTime, riskLabel } from '@/domain/mentalHealth'

const router = useRouter()
const mode = ref('camera')
const videoRef = ref(null)
const cameraReady = ref(false)
const cameraError = ref('')
const capturedImage = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)

const result = ref(null)
const resultVisible = ref(false)
const resultImageSrc = ref('')
const resultImageObjectUrl = ref('')
const resultImageResolution = ref('标准预览画面')
const analysisSourceLabel = ref('-')
const analysisCapturedAt = ref('-')

// Process dialog status
const processVisible = ref(false)
const processPercentage = ref(0)
const processStatusText = ref('')
const processLogs = ref([])

let mediaStream = null

const emotionScoreRows = computed(() => {
  const scores = result.value?.emotion_scores || {}
  return Object.entries(scores)
    .map(([emotion, score]) => {
      const normalizedScore = Number(score) || 0
      return {
        emotion,
        label: emotionLabel(emotion),
        score: normalizedScore,
        percentage: Number((normalizedScore * 100).toFixed(1)),
        description: getScoreDescription(normalizedScore)
      }
    })
    .sort((a, b) => b.score - a.score)
})

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

function clearResultImage() {
  if (resultImageObjectUrl.value) {
    URL.revokeObjectURL(resultImageObjectUrl.value)
  }
  resultImageObjectUrl.value = ''
  resultImageSrc.value = ''
  resultImageResolution.value = '标准预览画面'
}

function loadResultImageResolution(src) {
  if (!src) return
  const image = new Image()
  image.onload = () => {
    resultImageResolution.value = `${image.naturalWidth} x ${image.naturalHeight}`
  }
  image.onerror = () => {
    resultImageResolution.value = '标准预览画面'
  }
  image.src = src
}

function prepareResultImageSnapshot(sourceMode, file, cameraImage) {
  clearResultImage()
  analysisSourceLabel.value = sourceMode === 'camera' ? '实时相机采集' : file?.name || '本地上传图片'
  analysisCapturedAt.value = formatTime(new Date())

  if (sourceMode === 'camera') {
    resultImageSrc.value = cameraImage || ''
  } else if (file) {
    const objectUrl = URL.createObjectURL(file)
    resultImageObjectUrl.value = objectUrl
    resultImageSrc.value = objectUrl
  }

  loadResultImageResolution(resultImageSrc.value)
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
  processStatusText.value = '准备图像样本'
  processVisible.value = true

  const steps = [
    { pct: 18, text: '读取图像信息', log: '样本读取完成' },
    { pct: 42, text: '定位面部区域', log: '面部区域确认完成' },
    { pct: 68, text: '计算情绪概率', log: '情绪得分生成中' },
    { pct: 90, text: '整理分析报告', log: '建议内容生成中' }
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
      processStatusText.value = '分析完成'
      setTimeout(async () => {
        let shouldOpenResult = false
        try {
          shouldOpenResult = await callback()
        } finally {
          processVisible.value = false
        }
        if (shouldOpenResult) {
          await nextTick()
          resultVisible.value = true
        }
      }, 120)
    }
  }, 450)
}

async function analyzeImage() {
  if (!canAnalyze.value) {
    ElMessage.warning('请先准备待分析图像样本')
    return
  }

  const analysisMode = mode.value
  const cameraImage = capturedImage.value
  const uploadFile = selectedFile.value
  let analysisRequest

  try {
    let blob
    if (analysisMode === 'camera') {
      const response = await fetch(cameraImage)
      blob = await response.blob()
    } else {
      blob = uploadFile
    }
    analysisRequest = analyzeEmotionImage(blob)
      .then((res) => ({ res }))
      .catch((error) => ({ error }))
  } catch {
    ElMessage.error('图像样本读取失败，请重新采集后再试')
    return
  }

  simulateProcess(async () => {
    try {
      const { res, error } = await analysisRequest
      if (error) throw error

      if (res.data) {
        prepareResultImageSnapshot(analysisMode, uploadFile, cameraImage)
        result.value = res.data
        return true
      } else {
        ElMessage.warning(res.message || '未检测到人脸，请确保五官清晰可见')
      }
    } catch {
      ElMessage.error('服务响应异常，请稍后重试')
    }
    return false
  })
}

function goToEmotionRecords() {
  resultVisible.value = false
  router.push({
    name: 'StudentEmotionRecords',
    query: result.value?.id ? { record: result.value.id } : {}
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

function getRiskSummary(data) {
  if (data.risk_level === 'high') return '需要重点关注'
  if (data.risk_level === 'medium') return '存在轻度波动'
  return '状态相对平稳'
}

function getObservationText(data) {
  const emotion = emotionLabel(data.dominant_emotion)
  if (data.risk_level === 'high') {
    return `本次主导情绪为${emotion}，建议尽快联系辅导员或心理中心。`
  }
  if (data.risk_level === 'medium') {
    return `本次主导情绪为${emotion}，建议结合测评进一步确认近期状态。`
  }
  return `本次主导情绪为${emotion}，整体处于日常观察范围。`
}

function getCareLevelText(data) {
  if (data.risk_level === 'high') return '优先沟通'
  if (data.risk_level === 'medium') return '连续观察'
  return '常规记录'
}

function getCareActionText(data) {
  if (data.risk_level === 'high') return '建议尽快联系辅导员或心理中心，补充线下沟通记录。'
  if (data.risk_level === 'medium') return '建议结合测评结果和近一周识别记录继续观察。'
  return '保持规律作息和自我记录，作为后续趋势对照。'
}

function getScoreDescription(score) {
  if (score >= 0.45) return '主要情绪信号'
  if (score >= 0.25) return '次级情绪信号'
  if (score >= 0.1) return '弱信号'
  return '低占比'
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
  clearResultImage()
})

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.emotion-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 100%;
  height: 100%;
}

.camera-alert {
  margin-bottom: 4px;
}

.emotion-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.7fr);
  gap: 12px;
  align-items: stretch;
  flex: 1;
  min-height: 0;
}

.left-column,
.right-column {
  min-height: 0;
}

.capture-card,
.guide-card {
  height: 100%;
}

.capture-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: calc(100% - 49px);
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
  flex: 1;
  min-height: 0;
  align-items: center;
}

.video-wrapper {
  position: relative;
  width: min(100%, 520px);
  aspect-ratio: 4 / 3;
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
  width: min(100%, 520px);
}

.upload-frame {
  width: min(100%, 520px);
  flex: none;
}

.upload-frame :deep(.el-upload),
.upload-frame :deep(.el-upload-dragger) {
  width: 100%;
  height: 100%;
}

.upload-frame :deep(.el-upload-dragger) {
  padding: 0;
  border: 0;
  background: transparent;
}

.upload-frame-content {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  min-height: 0;
  border: 1px dashed var(--mh-line-strong);
  border-radius: var(--mh-radius-lg);
  overflow: hidden;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.18s ease, background 0.18s ease;
}

.upload-frame-content.is-filled {
  border-style: solid;
  background: #0f172a;
}

.upload-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--mh-muted);
}

.upload-empty-state strong {
  font-size: 15px;
  color: var(--mh-ink);
}

.upload-empty-state span {
  font-size: 12px;
}

.preview-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.upload-change-hint {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  height: 32px;
  border-radius: var(--mh-radius-sm);
  background: rgba(15, 23, 42, 0.72);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 650;
}

.submit-action-row {
  margin-top: 4px;
  padding-top: 16px;
  border-top: 1px solid var(--mh-line);
  width: 100%;
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
  gap: 14px;
  max-height: calc(100dvh - 250px);
  overflow: auto;
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
  box-shadow: 0 0 0 0 rgba(82, 82, 91, 0.28);
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
:deep(.emotion-result-dialog .el-dialog__body) {
  padding-top: 12px;
}

.result-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-overview-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.85fr) minmax(0, 1.35fr);
  gap: 16px;
  align-items: stretch;
}

.result-image-panel,
.result-main-panel,
.scores-card-box,
.advice-card-box {
  background: var(--mh-surface);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
}

.result-image-panel {
  padding: 14px;
}

.result-main-panel {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-head,
.box-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-head span,
.box-title-row span {
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.section-head strong {
  color: var(--mh-ink);
  font-size: 12px;
  font-weight: 750;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-image-frame {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: var(--mh-radius-sm);
  background: #0f172a;
  overflow: hidden;
  border: 1px solid var(--mh-line);
}

.result-image-frame img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.result-image-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
  font-size: 12px;
}

.result-image-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
  color: var(--mh-muted);
  font-size: 11.5px;
}

.result-summary-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.result-brief-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.brief-card {
  min-height: 104px;
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: #fbfbfc;
}

.brief-card span {
  display: block;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.brief-card strong {
  display: block;
  margin-top: 6px;
  color: var(--mh-ink);
  font-size: 16px;
}

.brief-card p {
  margin: 8px 0 0;
  color: var(--mh-text);
  font-size: 12px;
  line-height: 1.6;
}

.result-details-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(300px, 0.75fr);
  gap: 16px;
}

.box-title {
  margin: 0;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--mh-ink);
  border-left: 3px solid var(--mh-accent);
  padding-left: 8px;
}

.scores-card-box {
  padding: 16px;
}

.emotion-score-table {
  width: 100%;
}

.emotion-score-table :deep(.el-table__cell) {
  padding: 7px 0;
}

.score-table-progress :deep(.el-progress__text) {
  min-width: 38px;
  font-size: 11px !important;
}

.advice-card-box {
  padding: 16px;
}

.result-next-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: #fbfbfc;
}

.result-next-card span {
  display: block;
  margin-bottom: 4px;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.result-next-card strong {
  display: block;
  color: var(--mh-ink);
  font-size: 14px;
}

.result-next-card p {
  margin: 5px 0 0;
  color: var(--mh-text);
  font-size: 12px;
  line-height: 1.55;
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
  color: var(--mh-accent);
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
    box-shadow: 0 0 0 0 rgba(82, 82, 91, 0.28);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(82, 82, 91, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(82, 82, 91, 0);
  }
}

@media (max-width: 800px) {
  .emotion-grid,
  .result-overview-grid,
  .result-details-grid,
  .result-brief-grid {
    grid-template-columns: 1fr;
  }
}
</style>
