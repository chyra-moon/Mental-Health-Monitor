import http from './http'
import { readStoredToken } from '@/stores/user'

export function checkStudentVideo(studentId) {
  return http.get(`/admin/video/check/${studentId}`)
}

export function createVideoSession(studentId, frameCount) {
  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('frame_count', frameCount)
  return http.post('/admin/video/sessions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export async function fetchVideoBlob(streamSrc) {
  const token = readStoredToken()
  const response = await fetch(streamSrc, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  if (!response.ok) {
    throw new Error('视频文件加载失败')
  }
  return response.blob()
}

export function uploadVideoFrame(sessionId, imageBlob, frameIndex, timestampMs) {
  const formData = new FormData()
  formData.append('file', imageBlob, `frame-${frameIndex}.jpg`)
  formData.append('frame_index', frameIndex)
  formData.append('timestamp_ms', timestampMs)
  return http.post(`/admin/video/sessions/${sessionId}/frames`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function completeVideoSession(sessionId) {
  return http.post(`/admin/video/sessions/${sessionId}/complete`)
}

export function listVideoSessions(params) {
  return http.get('/admin/video/sessions', { params })
}

export function getVideoSession(sessionId) {
  return http.get(`/admin/video/sessions/${sessionId}`)
}
