import http from './http'

export function listMyRecords() {
  return http.get('/records/my')
}

export function listAdminRecords() {
  return http.get('/records/admin/all')
}
