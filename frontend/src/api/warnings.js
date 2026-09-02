import http from './http'

export function listMyWarnings() {
  return http.get('/warnings/my')
}

export function listAdminWarnings() {
  return http.get('/warnings/admin/list')
}

export function markWarningHandled(warningId) {
  return http.put(`/warnings/admin/${warningId}/status`)
}
