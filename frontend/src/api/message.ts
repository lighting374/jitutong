import userAuth from '../services/auth'

export interface Message {
  id: number
  type: 'like' | 'reply' | 'report'
  content: string
  relatedComment?: string
  linkUrl?: string
  isRead: boolean
  createdAt: string
}

export interface MessagesResponse {
  messages: Message[]
  unreadCount: number
}

/**
 * 获取消息列表
 */
export async function getMessages(): Promise<MessagesResponse> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch('/api/user/messages', {
    method: 'GET',
    headers,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    const error = new Error(message)
    ;(error as any).status = res.status
    throw error
  }

  return res.json()
}

/**
 * 标记消息为已读
 */
export async function markMessageAsRead(messageId: number): Promise<void> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`/api/user/messages/${messageId}/read`, {
    method: 'PUT',
    headers,
  })

  if (!res.ok) {
    throw new Error('标记已读失败')
  }
}

/**
 * 删除消息
 */
export async function deleteMessage(messageId: number): Promise<void> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`/api/user/messages/${messageId}`, {
    method: 'DELETE',
    headers,
  })

  if (!res.ok) {
    throw new Error('删除消息失败')
  }
}

/**
 * 全部标记为已读
 */
export async function markAllAsRead(): Promise<void> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch('/api/user/messages/read-all', {
    method: 'PUT',
    headers,
  })

  if (!res.ok) {
    throw new Error('标记全部已读失败')
  }
}

/**
 * 清空所有消息
 */
export async function clearAllMessages(): Promise<void> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch('/api/user/messages/clear', {
    method: 'DELETE',
    headers,
  })

  if (!res.ok) {
    throw new Error('清空消息失败')
  }
}

/**
 * 获取未读消息数量
 */
export async function getUnreadCount(): Promise<number> {
  const token = userAuth.getToken()
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch('/api/user/messages/unread-count', {
    method: 'GET',
    headers,
  })

  if (!res.ok) {
    return 0
  }

  const data = await res.json()
  return data.count || 0
}

export default {
  getMessages,
  markMessageAsRead,
  deleteMessage,
  markAllAsRead,
  clearAllMessages,
  getUnreadCount,
}
