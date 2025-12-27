import { ref } from 'vue'

// 根据角色使用不同的 token key，避免多账号冲突
function getTokenKey(role?: string): string {
  if (role === 'wiki_admin') return 'wiki_admin_token'
  if (role === 'admin') return 'admin_token'
  return 'admin_token' // 默认
}

function getUserKey(role?: string): string {
  if (role === 'wiki_admin') return 'wiki_admin_user'
  if (role === 'admin') return 'admin_user'
  return 'admin_user' // 默认
}

function getExpiresKey(role?: string): string {
  if (role === 'wiki_admin') return 'wiki_admin_token_expires_at'
  if (role === 'admin') return 'admin_token_expires_at'
  return 'admin_token_expires_at' // 默认
}

const TOKEN_KEY = 'admin_token'
const USER_KEY = 'admin_user'
const EXPIRES_AT_KEY = 'admin_token_expires_at'

const user = ref<any>(null)

function saveToken(token: string, role?: string, expiresInSeconds?: number) {
  const tokenKey = getTokenKey(role)
  const expiresKey = getExpiresKey(role)
  
  localStorage.setItem(tokenKey, token)
  if (expiresInSeconds) {
    const at = Date.now() + expiresInSeconds * 1000
    localStorage.setItem(expiresKey, String(at))
  }
}

function clearToken(role?: string) {
  const tokenKey = getTokenKey(role)
  const userKey = getUserKey(role)
  const expiresKey = getExpiresKey(role)
  
  localStorage.removeItem(tokenKey)
  localStorage.removeItem(expiresKey)
  localStorage.removeItem(userKey)
  user.value = null
}

export async function login(username: string, password: string) {
  let res: Response
  try {
    console.log('[Auth] 发送登录请求...', { username, url: '/api/admin/login' })
    res = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    console.log('[Auth] 收到响应:', { 
      status: res.status, 
      ok: res.ok, 
      statusText: res.statusText,
      headers: Object.fromEntries(res.headers.entries())
    })
  } catch (netErr: any) {
    console.error('[Auth] 网络错误:', netErr)
    throw new Error('无法连接到后台服务。请确认后端服务器正在运行。\n详细错误：' + (netErr && netErr.message ? netErr.message : String(netErr)))
  }

  // 处理非 200 响应
  if (!res.ok) {
    let errMsg = `登录失败 (HTTP ${res.status})`
    try {
      const err = await res.json()
      console.error('[Auth] 登录失败响应:', err)
      errMsg = err.message || err.msg || err.error || errMsg
    } catch (parseErr) {
      console.error('[Auth] 无法解析错误响应:', parseErr)
      const text = await res.text().catch(() => '')
      console.error('[Auth] 原始响应文本:', text)
    }
    throw new Error(errMsg)
  }

  let data: any
  try {
    data = await res.json()
    console.log('[Auth] 登录成功，原始响应数据:', JSON.stringify(data, null, 2))
  } catch (parseErr) {
    console.error('[Auth] 无法解析成功响应:', parseErr)
    throw new Error('服务器响应格式错误：无法解析 JSON')
  }
  
  // 兼容多种后端响应格式
  const token = data.token || data.access_token || data.data?.token
  const expiresIn = data.expiresIn || data.expires_in || data.expiresAt
  const u = data.user || data.admin || data.userInfo || data.data?.user || data.data
  
  if (!token) {
    console.error('[Auth] 响应中缺少 token，完整响应:', JSON.stringify(data, null, 2))
    throw new Error('登录响应格式错误：缺少 token')
  }
  
  if (!u || typeof u !== 'object') {
    console.error('[Auth] 响应中缺少有效的用户信息，完整响应:', JSON.stringify(data, null, 2))
    throw new Error('登录响应格式错误：缺少用户信息')
  }
  
  const userRole = u.role || 'admin' // 获取用户角色
  
  saveToken(token, userRole, expiresIn)
  const userKey = getUserKey(userRole)
  localStorage.setItem(userKey, JSON.stringify(u))
  user.value = u
  
  console.log('[Auth] Token 已保存到:', getTokenKey(userRole))
  console.log('[Auth] 用户信息已保存:', u)
  
  return data
}

export function logout() {
  const currentUser = getUser()
  const role = currentUser?.role
  clearToken(role)
}

export function getToken() {
  // 尝试从当前用户角色获取 token
  const currentUser = getUser()
  if (currentUser?.role) {
    return localStorage.getItem(getTokenKey(currentUser.role))
  }
  
  // 回退：尝试所有可能的 token
  const adminToken = localStorage.getItem('admin_token')
  const wikiToken = localStorage.getItem('wiki_admin_token')
  return adminToken || wikiToken || null
}

export function getUser() {
  if (user.value) return user.value
  
  // 尝试所有可能的用户信息
  const adminUser = localStorage.getItem('admin_user')
  const wikiUser = localStorage.getItem('wiki_admin_user')
  
  const raw = adminUser || wikiUser
  if (!raw) return null
  try {
    user.value = JSON.parse(raw)
    return user.value
  } catch {
    return null
  }
}

export function isTokenExpired() {
  const currentUser = getUser()
  const role = currentUser?.role
  const expiresKey = getExpiresKey(role)
  
  const at = localStorage.getItem(expiresKey)
  if (!at) return true
  return Date.now() > Number(at)
}

export function isAuthenticated() {
  const t = getToken()
  if (!t) return false
  if (isTokenExpired()) {
    const currentUser = getUser()
    clearToken(currentUser?.role)
    return false
  }
  return true
}

export default {
  login,
  logout,
  getToken,
  getUser,
  isAuthenticated,
  isTokenExpired,
}
