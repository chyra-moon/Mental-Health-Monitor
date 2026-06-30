import http from './http'

// 学生端：获取可选班级列表
export function listClasses() {
  return http.get('/classes')
}

// 管理员端：获取班级列表（带人数统计）
export function listAdminClasses() {
  return http.get('/admin/classes')
}

// 管理员端：新建班级
export function createClass(data) {
  return http.post('/admin/classes', data)
}

// 管理员端：删除班级
export function deleteClass(classId) {
  return http.delete(`/admin/classes/${classId}`)
}
