import http from './http'

// 学生端：获取个人预警列表
export function listMyWarnings() {
  return http.get('/warnings/my')
}

// 管理员端：获取所有风险预警
export function listAdminWarnings() {
  return http.get('/warnings/admin/list')
}

// 管理员端：更新预警处理状态
export function markWarningHandled(warningId) {
  return http.put(`/warnings/admin/${warningId}/status`)
}
