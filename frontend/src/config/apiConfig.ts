/**
 * API 配置文件
 * 统一管理后端服务器地址，方便切换环境
 */

// 后端服务器地址配置
// 注意：修改这里的地址后，还需要同步修改 vite.config.ts 中的代理配置
// 开发环境：使用本地或局域网地址
// 生产环境：使用服务器地址
export const API_CONFIG = {
  // 开发环境后端地址
  BACKEND_URL: 'http://123.60.110.146',
  
  // 其他可选配置
  // BACKEND_URL: 'http://localhost:5000',  // 本地开发
  // BACKEND_URL: 'http://192.168.214.197:5000',  // 其他IP
}

/**
 * 获取完整的后端 URL
 * @param path 相对路径，如 '/uploads/avatar.jpg'
 * @returns 完整的 URL
 */
export function getBackendUrl(path: string = ''): string {
  if (!path) return API_CONFIG.BACKEND_URL
  
  // 如果已经是完整 URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  
  // 确保路径以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_CONFIG.BACKEND_URL}${normalizedPath}`
}

/**
 * 修复头像 URL
 * @param avatar 头像路径
 * @returns 完整的头像 URL
 */
export function fixAvatarUrl(avatar: string | undefined): string {
  if (!avatar) return '/avatar.jpg'
  
  // 如果是完整 URL，直接返回
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  
  // 如果是默认头像，直接返回
  if (avatar === '/avatar.jpg') {
    return avatar
  }
  
  // 相对路径，拼接后端地址
  return getBackendUrl(avatar)
}
