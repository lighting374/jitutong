/**
 * API 请求拦截器
 * 拦截所有 API 响应，检测用户是否被封禁
 */

import userAuth from '../services/userAuth'

// 保存原始的 fetch 函数
let originalFetch: typeof fetch = window.fetch

/**
 * 包装 fetch 请求，添加封禁检测
 */
export async function interceptedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  // 使用原始的 fetch，避免无限递归
  const response = await originalFetch(url, options)

  // 登录请求不拦截，直接返回
  if (url.includes('/login')) {
    return response
  }

  // 检查是否返回 403 Forbidden（可能是被封禁）
  if (response.status === 403) {
    const data = await response.clone().json().catch(() => ({}))
    
    // 检查错误信息是否包含封禁相关关键词
    const message = data.message || data.error || ''
    if (
      message.includes('banned') || 
      message.includes('封禁') ||
      message.includes('禁用')
    ) {
      console.warn('🚫 API 返回封禁状态')
      handleBanned()
      throw new Error('您的账号已被封禁')
    }
  }

  // 检查是否返回 401 Unauthorized
  if (response.status === 401) {
    console.warn('🔐 API 返回未授权状态，URL:', url)
    
    // 判断是管理员请求还是用户请求
    const isAdminRequest = url.includes('/api/admin/')
    
    if (isAdminRequest) {
      // 管理员请求，清除管理员 token
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      localStorage.removeItem('admin_token_expires_at')
      // 跳转到管理员登录页
      if (!window.location.pathname.includes('/admin/login')) {
        setTimeout(() => {
          window.location.href = '/admin/login?reason=expired'
        }, 100)
      }
    } else {
      // 用户请求，清除用户 session
      userAuth.clearSession()
      // 跳转到用户登录页
      if (!window.location.pathname.includes('/login')) {
        setTimeout(() => {
          window.location.href = '/login?reason=expired'
        }, 100)
      }
    }
  }

  return response
}

/**
 * 处理用户被封禁
 */
function handleBanned() {
  // 清除会话
  userAuth.clearSession()
  
  // 显示提示
  alert('您的账号已被封禁，无法继续操作。如有疑问，请联系管理员。')
  
  // 重定向到登录页
  window.location.href = '/login?reason=banned'
}

/**
 * 包装原生 fetch，自动添加拦截
 */
export function setupApiInterceptor() {
  // 保存原始 fetch 到模块级别变量
  originalFetch = window.fetch
  
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    // 只拦截 /api/ 开头的请求
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    
    if (url.startsWith('/api/')) {
      return interceptedFetch(url, init)
    }
    
    // 其他请求使用原生 fetch
    return originalFetch(input, init)
  }
  
  console.log('✅ API 拦截器已启动')
}

export default {
  interceptedFetch,
  setupApiInterceptor,
}
