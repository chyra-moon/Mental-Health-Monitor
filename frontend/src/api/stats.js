import http from './http'

// 学生端：获取情绪趋势数据
export function getStudentTrend(days) {
  return http.get('/stats/student/trend', { params: { days } })
}

// 管理员端：获取概览统计
export function getAdminOverview() {
  return http.get('/stats/admin/overview')
}

// 管理员端：获取情绪分布数据
export function getAdminEmotionDistribution() {
  return http.get('/stats/admin/emotion-distribution')
}

// 管理员端：获取风险变化趋势
export function getAdminRiskTrend() {
  return http.get('/stats/admin/risk-trend')
}

