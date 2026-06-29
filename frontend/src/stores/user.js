import { defineStore } from 'pinia'

const TOKEN_KEY = 'token'
const USER_KEY = 'user'

export function readStoredToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    clearStoredSession()
    return null
  }
}

export function persistSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearStoredSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: readStoredToken(),
    user: readStoredUser(),
  }),
  actions: {
    login(token, user) {
      this.token = token
      this.user = user
      persistSession(token, user)
    },
    updateUser(user) {
      this.user = user
      persistSession(this.token || readStoredToken(), user)
    },
    logout() {
      this.token = ''
      this.user = null
      clearStoredSession()
    },
  },
})
