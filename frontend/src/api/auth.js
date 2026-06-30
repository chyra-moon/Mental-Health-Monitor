import http from './http'

export function login(data) {
  return http.post('/auth/login', data)
}

export function registerStudent(data) {
  return http.post('/auth/register', data)
}

export function getMe() {
  return http.get('/auth/me')
}

export function updateStudentProfile(data) {
  return http.put('/auth/profile', data)
}
