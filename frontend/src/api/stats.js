import http from './http'

export function getStudentTrend(days) {
  return http.get('/stats/student/trend', { params: { days } })
}

export function getAdminOverview() {
  return http.get('/stats/admin/overview')
}

export function getAdminEmotionDistribution() {
  return http.get('/stats/admin/emotion-distribution')
}

export function getAdminRiskTrend() {
  return http.get('/stats/admin/risk-trend')
}

