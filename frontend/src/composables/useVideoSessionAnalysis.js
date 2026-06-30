import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createVideoSession, uploadVideoFrame, completeVideoSession } from '@/api/video'

export function useVideoSessionAnalysis({
  selectedStudentId,
  checkResult,
  frameCount,
  refreshStudentCheck,
  refreshHistory
}) {
  const phase = ref('idle') // idle, running, completed, error
  const videoRef = ref(null)
  const videoDuration = ref(0)
  const captureIntervalMs = ref(1000)
  const frameResults = ref([])
  const sessionSummary = ref(null)
  
  const currentSessionId = ref(null)
  const completedFrameCount = ref(0)
  const isCapturing = ref(false)
  const analysisError = ref('')

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
    phase.value = 'idle'
    frameResults.value = []
    sessionSummary.value = null
    completedFrameCount.value = 0
    currentSessionId.value = null
    analysisError.value = ''
  }

  function clearLastAnalyzedVideoIfStudentChanged(newStudentId) {
    clearLastAnalyzedVideo()
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
    phase.value = 'running'
    completedFrameCount.value = 0
    frameResults.value = []
    sessionSummary.value = null
    analysisError.value = ''

    try {
      // 1. 创建视频分析会话
      const sessionRes = await createVideoSession(selectedStudentId.value, frameCount.value)
      const sessionData = sessionRes.data
      currentSessionId.value = sessionData.id

      // 2. 加载视频
      if (videoRef.value) {
        videoRef.value.src = sessionData.stream_src
        videoRef.value.load()
        // 视频元数据加载后会自动触发 onVideoMeta，启动抽帧循环
      } else {
        throw new Error('未找到视频播放器引用')
      }
    } catch (err) {
      phase.value = 'error'
      isCapturing.value = false
      analysisError.value = err.message || '启动分析失败'
      ElMessage.error(analysisError.value)
    }
  }

  // 视频加载元数据回调
  function onVideoMeta(event) {
    const video = event.target
    videoDuration.value = video.duration || 0
    
    // 计算抽帧间隔 (秒)
    const intervalSec = videoDuration.value / (frameCount.value + 1)
    captureIntervalMs.value = Math.max(0.5, intervalSec) * 1000

    // 开始抽帧循环
    video.currentTime = intervalSec
    video.play().catch(() => {})
    startCaptureLoop(video)
  }

  // 抽帧采集逻辑
  async function startCaptureLoop(video) {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    const captureNextFrame = async () => {
      if (phase.value !== 'running' || completedFrameCount.value >= frameCount.value) {
        return
      }

      // 截图
      canvas.width = video.videoWidth || 640
      canvas.height = video.videoHeight || 480
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      const frameIdx = completedFrameCount.value
      const timestampMs = Math.round(video.currentTime * 1000)

      try {
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85))
        
        // 上传帧图片
        const frameRes = await uploadVideoFrame(currentSessionId.value, blob, frameIdx, timestampMs)
        
        if (frameRes.data) {
          frameResults.value.push(frameRes.data)
        }
        
        completedFrameCount.value++

        // 移至下一个时间点
        const nextTime = (completedFrameCount.value + 1) * (videoDuration.value / (frameCount.value + 1))
        if (completedFrameCount.value < frameCount.value && nextTime < videoDuration.value) {
          video.currentTime = nextTime
          // 延迟一点以确保视频渲染了当前帧，再进行下一次采集
          setTimeout(captureNextFrame, 350)
        } else {
          // 所有帧采集完成，结束会话
          await finishAnalysis()
        }
      } catch (err) {
        console.error('Frame capture error:', err)
        // 容错：即使一帧失败也继续
        completedFrameCount.value++
        if (completedFrameCount.value < frameCount.value) {
          setTimeout(captureNextFrame, 300)
        } else {
          await finishAnalysis()
        }
      }
    }

    // 延迟 500ms 开启第一次采集
    setTimeout(captureNextFrame, 500)
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
      ElMessage.success('视频情绪分析完成')
      
      if (refreshHistory) {
        await refreshHistory()
      }
    } catch (err) {
      phase.value = 'error'
      isCapturing.value = false
      analysisError.value = err.message || '完成分析报告失败'
      ElMessage.error(analysisError.value)
    }
  }

  function onVideoEnded() {
    // 视频播放结束时的回调，防呆
    if (phase.value === 'running' && completedFrameCount.value < frameCount.value) {
      finishAnalysis()
    }
  }

  return {
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
    clearLastAnalyzedVideoIfStudentChanged
  }
}
