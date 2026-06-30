import http from './http'

export function listStudents() {
  return http.get('/users/admin/list')
}
