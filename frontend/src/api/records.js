import http from './http'

// 学生端获取自己的记录列表
export function listMyRecords() {
  return http.get('/records/my')
}

// 管理员端获取所有学生的记录列表
export function listAdminRecords() {
  return http.get('/records/admin/all')
}
