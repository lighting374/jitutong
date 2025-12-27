import { ref } from 'vue'

const USER_TOKEN_KEY = 'user_token'
const USER_INFO_KEY = 'user_info'
const USER_TOKEN_EXPIRES_KEY = 'user_token_expires_at'

const currentUser = ref<any | null>(null)

export interface UserSessionPayload {
  token: string
  expiresIn?: number
  user?: any
}

const persistUser = (user: any) => {
  if (user) {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(user))
    currentUser.value = user
  }
}

export const updateStoredUser = (user: any) => {
  persistUser(user)
}

export const setSession = ({ token, expiresIn, user }: UserSessionPayload) => {
  if (token) {
    localStorage.setItem(USER_TOKEN_KEY, token)
    if (typeof expiresIn === 'number') {
      const expiresAt = Date.now() + expiresIn * 1000
      localStorage.setItem(USER_TOKEN_EXPIRES_KEY, String(expiresAt))
    }
  }
  if (user) {
    persistUser(user)
  }
}

export const clearSession = () => {
  localStorage.removeItem(USER_TOKEN_KEY)
  localStorage.removeItem(USER_INFO_KEY)
  localStorage.removeItem(USER_TOKEN_EXPIRES_KEY)
  currentUser.value = null
}

export const getToken = () => {
  return localStorage.getItem(USER_TOKEN_KEY)
}

export const getUser = () => {
  if (currentUser.value) return currentUser.value
  const raw = localStorage.getItem(USER_INFO_KEY)
  if (!raw) return null
  try {
    currentUser.value = JSON.parse(raw)
    return currentUser.value
  } catch (err) {
    console.warn('Failed to parse stored user info', err)
    return null
  }
}

export const isTokenExpired = () => {
  const expiresAt = localStorage.getItem(USER_TOKEN_EXPIRES_KEY)
  if (!expiresAt) return false
  return Date.now() > Number(expiresAt)
}

export const isBanned = () => {
  const user = getUser()
  return user && user.status === 'banned'
}

export const isAuthenticated = () => {
  const token = getToken()
  if (!token) return false
  if (isTokenExpired()) {
    clearSession()
    return false
  }
  // 检查是否被封禁
  if (isBanned()) {
    clearSession()
    return false
  }
  return true
}

export default {
  setSession,
  clearSession,
  getToken,
  getUser,
  isAuthenticated,
  isTokenExpired,
  isBanned,
  updateStoredUser,
}
