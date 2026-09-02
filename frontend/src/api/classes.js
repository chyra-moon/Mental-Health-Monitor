import http from './http'

export function listClasses() {
  return http.get('/classes')
}

export function listAdminClasses() {
  return http.get('/admin/classes')
}

export function createClass(data) {
  return http.post('/admin/classes', data)
}

export function deleteClass(classId) {
  return http.delete(`/admin/classes/${classId}`)
}
