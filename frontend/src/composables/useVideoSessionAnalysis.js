import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createVideoSession, fetchVideoBlob, uploadVideoFrame, completeVideoSession } from '@/api/video'

export function useVideoSessionAnalysis({
  selectedStudentId,
  checkResult,
  frameCount,
  refreshStudentCheck,
  refreshHistory
}) {
  const phase = ref('idle') // idle, running, completed, error
  const videoRef = ref(null)
  const analysisVideoSrc = ref('')
  const analysisVideoFilename = ref('')
  const videoDuration = ref(0)
  const captureIntervalMs = ref(1000)
  const frameResults = ref([])
  const sessionSummary = ref(null)
  
  const currentSessionId = ref(null)
  const completedFrameCount = ref(0)
  const isCapturing = ref(false)
  const isVideoLoading = ref(false)
  const captureStarted = ref(false)
  const analysisError = ref('')
  let analysisVideoObjectUrl = ''

  const canStart = computed(() => {
    return selectedStudentId.value && 
           checkResult.value?.available && 
           phase.value !== 'running'
  })

  const progressPercentage = computed(() => {
    if (!frameCount.value) return 0
    return Math.round((completedFrameCount.value / frameCount.value) * 100)
  })

  // 按钮文案和状态
  const primaryButtonLabel = computed(() => {
    if (phase.value === 'running') return '正在分析...'
    if (phase.value === 'completed') return '重新分析'
    return '开始会话分析'
  })

  const primaryButtonType = computed(() => {
    if (phase.value === 'running') return 'info'
    if (phase.value === 'completed') return 'default'
    return 'primary'
  })

  const primaryButtonLoading = computed(() => {
    return isCapturing.value
  })

  const primaryButtonDisabled = computed(() => {
    return !canStart.value && phase.value !== 'completed'
  })

  // 重置状态
  function clearLastAnalyzedVideo() {
    clearAnalysisVideoObjectUrl()
    phase.value = 'idle'
    analysisVideoSrc.value = ''
    analysisVideoFilename.value = ''
    frameResults.value = []
    sessionSummary.value = null
    completedFrameCount.value = 0
    currentSessionId.value = null
    videoDuration.value = 0
    captureIntervalMs.value = 1000
    isCapturing.value = false
    isVideoLoading.value = false
    captureStarted.value = false
    analysisError.value = ''
  }

  function clearLastAnalyzedVideoIfStudentChanged(newStudentId) {
    clearLastAnalyzedVideo()
  }

  function clearAnalysisVideoObjectUrl() {
    if (analysisVideoObjectUrl) {
      URL.revokeObjectURL(analysisVideoObjectUrl)
      analysisVideoObjectUrl = ''
    }
  }

  // 核心操作：开始/主操作
  async function handlePrimaryAction() {
    if (phase.value === 'completed') {
      clearLastAnalyzedVideo()
      if (refreshStudentCheck) await refreshStudentCheck(selectedStudentId.value)
      return
    }

    if (!selectedStudentId.value || !checkResult.value?.available) {
      ElMessage.warning('请先选择有可用视频的学生')
      return
    }

    isCapturing.value = true
    isVideoLoading.value = true
    captureStarted.value = false
    phase.value = 'running'
    completedFrameCount.value = 0
    frameResults.value = []
    sessionSummary.value = null
    analysisError.value = ''
    clearAnalysisVideoObjectUrl()
    analysisVideoSrc.value = ''
    analysisVideoFilename.value = ''

    try {
      // 1. 创建视频分析会话
      const sessionRes = await createVideoSession(selectedStudentId.value, frameCount.value)
      const sessionData = sessionRes.data
      currentSessionId.value = sessionData.id
      analysisVideoFilename.value = sessionData.video_filename || ''

      // 2. 受保护视频流需要先带登录态拉取为 Blob，再交给 video 标签播放
      const videoBlob = await fetchVideoBlob(sessionData.stream_src)
      analysisVideoObjectUrl = URL.createObjectURL(videoBlob)
      analysisVideoSrc.value = analysisVideoObjectUrl
      isVideoLoading.value = false
    } catch (err) {
      phase.value = 'error'
      isCapturing.value = false
      isVideoLoading.value = false
      analysisError.value = err.message || '启动分析失败'
      ElMessage.error(analysisError.value)
    }
  }

  // 视频加载元数据回调
  function onVideoMeta(event) {
    const video = event.target
    if (phase.value !== 'running' || !currentSessionId.value || captureStarted.value) return
    videoRef.value = video
    videoDuration.value = video.duration || 0
    if (!Number.isFinite(videoDuration.value) || videoDuration.value <= 0) {
      onVideoError('视频时长读取失败，请确认视频文件可播放')
      return
    }
    
    // 计算抽帧间隔 (秒)
    const intervalSec = videoDuration.value / (frameCount.value + 1)
    captureIntervalMs.value = Math.max(0.5, intervalSec) * 1000

    captureStarted.value = true
    startCaptureLoop(video)
  }

  // 抽帧采集逻辑
  async function startCaptureLoop(video) {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    try {
      video.pause()

      for (let frameIdx = 0; frameIdx < frameCount.value; frameIdx++) {
        if (phase.value !== 'running') return

        const targetTime = Math.min(
          Math.max((frameIdx + 1) * (videoDuration.value / (frameCount.value + 1)), 0),
          Math.max(videoDuration.value - 0.05, 0)
        )
        await seekVideo(video, targetTime)
        await waitForRenderableFrame(video)

        canvas.width = video.videoWidth || 640
        canvas.height = video.videoHeight || 480
        if (!canvas.width || !canvas.height) {
          throw new Error('视频画面尺寸读取失败')
        }

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        const timestampMs = Math.round(video.currentTime * 1000)
        const blob = await canvasToBlob(canvas)

        try {
          const frameRes = await uploadVideoFrame(currentSessionId.value, blob, frameIdx, timestampMs)
          if (frameRes.data) {
            frameResults.value.push(frameRes.data)
          }
        } catch (err) {
          frameResults.value.push({
            frame_index: frameIdx,
            timestamp_ms: timestampMs,
            analysis_status: 'error',
            dominant_emotion: null,
            confidence: null,
            emotion_scores: null,
            error_message: err.message || '帧分析请求失败'
          })
        }

        completedFrameCount.value++
      }

      video.currentTime = Math.max(videoDuration.value - 0.05, 0)
      await finishAnalysis()
    } catch (err) {
      phase.value = 'error'
      isCapturing.value = false
      analysisError.value = err.message || '视频抽帧失败'
      ElMessage.error(analysisError.value)
    }
  }

  function seekVideo(video, targetTime) {
    return new Promise((resolve, reject) => {
      let settled = false
      const finish = () => {
        if (settled) return
        settled = true
        cleanup()
        resolve()
      }
      const fail = () => {
        if (settled) return
        settled = true
        cleanup()
        reject(new Error('视频定位超时，请确认视频编码可被浏览器播放'))
      }
      const cleanup = () => {
        clearTimeout(timer)
        video.removeEventListener('seeked', finish)
        video.removeEventListener('error', fail)
      }
      const timer = setTimeout(fail, 5000)
      video.addEventListener('seeked', finish)
      video.addEventListener('error', fail)

      if (Math.abs(video.currentTime - targetTime) < 0.04) {
        finish()
        return
      }
      video.currentTime = targetTime
    })
  }

  function waitForRenderableFrame(video) {
    if ('requestVideoFrameCallback' in video) {
      return new Promise((resolve) => {
        const timer = setTimeout(resolve, 180)
        video.requestVideoFrameCallback(() => {
          clearTimeout(timer)
          resolve()
        })
      })
    }
    return new Promise((resolve) => setTimeout(resolve, 120))
  }

  function canvasToBlob(canvas) {
    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('视频帧编码失败'))
        }
      }, 'image/jpeg', 0.85)
    })
  }

  // 完成分析
  async function finishAnalysis() {
    try {
      if (videoRef.value) {
        videoRef.value.pause()
      }
      
      const compRes = await completeVideoSession(currentSessionId.value)
      sessionSummary.value = compRes.data
      phase.value = 'completed'
      isCapturing.value = false
      isVideoLoading.value = false
      ElMessage.success('视频情绪分析完成')
      
      if (refreshHistory) {
        await refreshHistory()
      }
    } catch (err) {
      phase.value = 'error'
      isCapturing.value = false
      isVideoLoading.value = false
      analysisError.value = err.message || '完成分析报告失败'
      ElMessage.error(analysisError.value)
    }
  }

  function onVideoError(message = '视频加载失败，请确认视频文件可播放') {
    if (phase.value === 'running') {
      phase.value = 'error'
      isCapturing.value = false
      isVideoLoading.value = false
      analysisError.value = typeof message === 'string' ? message : '视频加载失败，请确认视频文件可播放'
      ElMessage.error(analysisError.value)
    }
  }

  function onVideoEnded() {}

  return {
    phase,
    videoRef,
    analysisVideoSrc,
    analysisVideoFilename,
    videoDuration,
    captureIntervalMs,
    frameResults,
    sessionSummary,
    isVideoLoading,
    analysisError,
    canStart,
    completedFrameCount,
    progressPercentage,
    primaryButtonLabel,
    primaryButtonType,
    primaryButtonLoading,
    primaryButtonDisabled,
    handlePrimaryAction,
    onVideoMeta,
    onVideoError,
    onVideoEnded,
    clearLastAnalyzedVideo,
    clearLastAnalyzedVideoIfStudentChanged
  }
}
