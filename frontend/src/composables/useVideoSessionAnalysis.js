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
    // 学生切换、弹窗关闭或重新分析时释放 Object URL，避免旧采集记录的 Blob 常驻内存。
    if (analysisVideoObjectUrl) {
      URL.revokeObjectURL(analysisVideoObjectUrl)
      analysisVideoObjectUrl = ''
    }
  }

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
      const sessionRes = await createVideoSession(selectedStudentId.value, frameCount.value)
      const sessionData = sessionRes.data
      currentSessionId.value = sessionData.id
      analysisVideoFilename.value = sessionData.video_filename || ''

      // 打卡摄像头完成采集并落盘后，通过鉴权接口读取该次记录，再创建分析所需的 Object URL。
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

  function onVideoMeta(event) {
    const video = event.target
    // loadedmetadata 可能重复触发，captureStarted 保证同一会话只启动一次抽帧循环。
    if (phase.value !== 'running' || !currentSessionId.value || captureStarted.value) return
    videoRef.value = video
    videoDuration.value = video.duration || 0
    if (!Number.isFinite(videoDuration.value) || videoDuration.value <= 0) {
      onVideoError('视频时长读取失败，请确认视频文件可播放')
      return
    }
    
    const intervalSec = videoDuration.value / (frameCount.value + 1)
    captureIntervalMs.value = Math.max(0.5, intervalSec) * 1000

    captureStarted.value = true
    startCaptureLoop(video)
  }

  async function startCaptureLoop(video) {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    try {
      video.pause()

      // 每帧完成定位、渲染、编码和上传后再处理下一帧，保持 frame_index 顺序。
      for (let frameIdx = 0; frameIdx < frameCount.value; frameIdx++) {
        if (phase.value !== 'running') return

        // 采样点按 (frameIdx + 1) / (frameCount + 1) 分布，避开采集记录的首帧和结束边界。
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
          // 单帧上传失败只追加前端 error 结果，后续帧仍继续处理。
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
        // seek 完成、失败或超时后都移除监听器和定时器，避免旧回调影响后续采样。
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
    // seeked 只表示定位完成；浏览器支持时再等待对应采集帧可供 Canvas 绘制。
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
