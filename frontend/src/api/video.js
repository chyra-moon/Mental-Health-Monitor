import http from './http'

// 检查学生是否有可用留存视频
export function checkStudentVideo(studentId) {
  return http.get(`/admin/video/check/${studentId}`)
}

// 创建视频分析会话
export function createVideoSession(studentId, frameCount) {
  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('frame_count', frameCount)
  return http.post('/admin/video/sessions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 上传视频抽帧图像进行分析
export function uploadVideoFrame(sessionId, imageBlob, frameIndex, timestampMs) {
  const formData = new FormData()
  formData.append('file', imageBlob, `frame-${frameIndex}.jpg`)
  formData.append('frame_index', frameIndex)
  formData.append('timestamp_ms', timestampMs)
  return http.post(`/admin/video/sessions/${sessionId}/frames`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 完成视频会话分析
export function completeVideoSession(sessionId) {
  return http.post(`/admin/video/sessions/${sessionId}/complete`)
}

// 获取视频会话历史列表
export function listVideoSessions(params) {
  return http.get('/admin/video/sessions', { params })
}

// 获取视频会话详细分析报告
export function getVideoSession(sessionId) {
  return http.get(`/admin/video/sessions/${sessionId}`)
}
