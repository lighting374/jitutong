import userAuth from '../services/userAuth'

const BASE_URL = '/api/user'

/**
 * 用户端 API 基础请求封装。
 * 1. 自动附带 token。
 * 2. 非 FormData 请求默认使用 JSON。
 * 3. 统一错误抛出。
 */
async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {}

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const token = userAuth.getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers || {}),
    },
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    throw new Error(message)
  }

  if (res.status === 204) {
    return null
  }

  return res.json()
}

export interface LoginPayload {
  phone: string
  password: string
}

/**
 * POST /api/user/login
 * 使用手机号 + 密码登录，返回 token 与用户会话。
 */
export const loginUser = async (payload: LoginPayload) => {
  const response = await request('/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  
  // 检查用户是否被封禁
  if (response && response.user && response.user.status === 'banned') {
    throw new Error('您的账号已被封禁，无法登录。如有疑问，请联系管理员。')
  }
  
  return response
}

export interface RegisterPayload {
  phone: string
  password: string
  nickname?: string
}

/**
 * POST /api/user/register
 * 注册新用户，可附带昵称。
 */
export const registerUser = (payload: RegisterPayload) => {
  return request('/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/**
 * GET /api/user/profile
 * 获取当前登录用户的基础资料。
 */
export const getUserProfile = () => {
  return request('/profile')
}

/**
 * PUT /api/user/profile
 * 更新资料：昵称、头像、个签等。
 * 支持文件上传（头像）
 */
export const updateUserProfile = (data: Record<string, any>, avatarFile?: File) => {
  // 如果有头像文件，使用 FormData
  if (avatarFile) {
    const formData = new FormData()
    formData.append('nickname', data.nickname || '')
    formData.append('bio', data.bio || '')
    formData.append('avatar', avatarFile)
    
    return request('/profile', {
      method: 'PUT',
      body: formData,
      // 不设置 Content-Type，让浏览器自动设置 multipart/form-data
      headers: {},
    })
  }
  
  // 没有头像文件，使用 JSON
  return request('/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export interface UserMessage {
  id: string | number
  type: 'system' | 'comment_reply' | 'like' | string
  content: string
  date: string
  read: boolean
  link?: string | null
}

/**
 * GET /api/user/messages
 * 拉取站内通知列表与未读数量。
 */
export const getUserMessages = (): Promise<{ items: UserMessage[]; unreadCount: number }> => {
  return request('/messages')
}

/**
 * POST /api/user/messages/:id/read
 * 单条消息设为已读。
 */
export const markMessageRead = (messageId: string | number) => {
  return request(`/messages/${messageId}/read`, { method: 'POST' })
}

/**
 * POST /api/user/messages/read-all
 * 一键清空未读。
 */
export const markAllMessagesRead = () => {
  return request('/messages/read-all', { method: 'POST' })
}

export interface HistoryItem {
  id: string
  buildingId: number
  wikiId: number
  name: string
  lastVisited: string
  imageUrl?: string  // 可选，后端可能返回 null
  mainImage?: string  // 备用字段
  image_url?: string  // 备用字段
  main_image?: string // 备用字段
}

/**
 * GET /api/user/history
 * 获取「最近浏览地点」。
 */
export const getBrowsingHistory = (): Promise<{ items: HistoryItem[] }> => {
  return request('/history')
}

/**
 * DELETE /api/user/history
 * 清空浏览历史。
 */
export const clearBrowsingHistory = () => {
  return request('/history', { method: 'DELETE' })
}

export interface FavoriteItem {
  buildingId: number
  wikiId: number
  name: string
  description: string
  imageUrl: string
  type?: string
}

/**
 * GET /api/user/favorites
 * 收藏列表。
 */
export const getFavorites = (): Promise<{ items: FavoriteItem[] }> => {
  return request('/favorites')
}

/**
 * POST /api/user/favorites
 * 添加收藏，需要同时传递 buildingId 和 wikiId。
 */
export const addFavorite = (params: { buildingId: number | string; wikiId: number | string }) => {
  return request('/favorites', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

/**
 * DELETE /api/user/favorites
 * 取消收藏，需要同时传递 buildingId 和 wikiId。
 */
export const removeFavorite = (params: { buildingId: number | string; wikiId: number | string }) => {
  const search = new URLSearchParams()
  search.set('buildingId', String(params.buildingId))
  search.set('wikiId', String(params.wikiId))
  return request(`/favorites?${search.toString()}`, { method: 'DELETE' })
}

/**
 * GET /api/user/favorites/status?buildingId=xxx&wikiId=yyy
 * 查询是否已收藏（用于详情页状态同步）。
 */
export const getFavoriteStatus = (params: { buildingId?: number; wikiId?: number }) => {
  const search = new URLSearchParams()
  if (params.buildingId) search.set('buildingId', String(params.buildingId))
  if (params.wikiId) search.set('wikiId', String(params.wikiId))
  return request(`/favorites/status?${search.toString()}`)
}

export interface AddHistoryPayload {
  buildingId: number | string
  wikiId: number | string
  name: string
  imageUrl?: string
  address?: string
}

/**
 * POST /api/user/history
 * 记录用户浏览地点
 */
export const addBrowsingHistory = (payload: AddHistoryPayload) => {
  return request('/history', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export interface MyReview {
  id: string | number
  locationId: string | number
  locationName: string
  rating: number
  comment: string
  createdAt: string
  updatedAt?: string
  wikiId?: number
  // 回复相关字段
  parentId?: number | null
  parentUserName?: string
  parentComment?: string
}

/**
 * GET /api/user/my-comments
 * 获取当前用户发表的评论列表
 */
export const getMyReviews = (): Promise<{ items: MyReview[] }> => {
  return request('/my-comments')
}

export default {
  loginUser,
  registerUser,
  getUserProfile,
  updateUserProfile,
  getUserMessages,
  markMessageRead,
  markAllMessagesRead,
  getBrowsingHistory,
  clearBrowsingHistory,
  addBrowsingHistory,
  getMyReviews,
  getFavorites,
  addFavorite,
  removeFavorite,
  getFavoriteStatus,
}
