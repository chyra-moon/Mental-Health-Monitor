import http from './http'

// 检查学生是否有可用分析素材
export function checkStudentVideo(studentId) {
  return http.get(`/admin/video/check/${studentId}`)
}

// 创建分析会话
export function createVideoSession(studentId, frameCount) {
  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('frame_count', frameCount)
  return http.post('/admin/video/sessions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 上传画面帧进行分析
export function uploadVideoFrame(sessionId, imageBlob, frameIndex, timestampMs) {
  const formData = new FormData()
  formData.append('file', imageBlob, `frame-${frameIndex}.jpg`)
  formData.append('frame_index', frameIndex)
  formData.append('timestamp_ms', timestampMs)
  return http.post(`/admin/video/sessions/${sessionId}/frames`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 完成分析
export function completeVideoSession(sessionId) {
  return http.post(`/admin/video/sessions/${sessionId}/complete`)
}

// 获取分析历史列表
export function listVideoSessions(params) {
  return http.get('/admin/video/sessions', { params })
}

// 获取分析报告详情
export function getVideoSession(sessionId) {
  return http.get(`/admin/video/sessions/${sessionId}`)
}
