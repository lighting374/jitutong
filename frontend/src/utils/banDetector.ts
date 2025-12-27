/**
 * 用户封禁状态检测器
 * 定期检查用户是否被封禁，如果被封禁则自动退出登录
 */

import userAuth from '../services/userAuth'
import { getUserProfile } from '../api/user'
import { useRouter } from 'vue-router'

let checkInterval: number | null = null
let isChecking = false

/**
 * 开始定期检测用户封禁状态
 * @param intervalSeconds 检测间隔（秒），默认 5 秒
 */
export function startBanDetection(intervalSeconds: number = 5) {
  // 如果已经在检测，先停止
  if (checkInterval) {
    stopBanDetection()
  }

  console.log(`🔍 开始定期检测用户封禁状态，间隔: ${intervalSeconds} 秒`)

  // 立即执行一次检测
  checkBanStatus()

  // 设置定期检测
  checkInterval = window.setInterval(() => {
    checkBanStatus()
  }, intervalSeconds * 1000)
}

/**
 * 停止定期检测
 */
export function stopBanDetection() {
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
    console.log('⏹️ 停止定期检测用户封禁状态')
  }
}

/**
 * 检查用户封禁状态
 */
async function checkBanStatus() {
  // 避免重复检测
  if (isChecking) {
    return
  }

  // 检查是否已登录
  if (!userAuth.isAuthenticated()) {
    stopBanDetection()
    return
  }

  isChecking = true

  try {
    console.log('🔍 检测用户状态...')
    
    // 获取当前本地用户信息
    const localUser = userAuth.getUser()
    const previousStatus = localUser?.status
    
    // 调用后端 API 获取最新用户信息
    const response = await getUserProfile()
    
    if (response && response.user) {
      const user = response.user
      const currentStatus = user.status
      
      console.log(`📊 用户状态: ${previousStatus} → ${currentStatus}`)
      
      // 检查是否被封禁
      if (currentStatus === 'banned') {
        console.warn('🚫 检测到用户已被封禁')
        handleUserBanned()
      } else if (currentStatus === 'active') {
        console.log('✅ 用户状态正常')
        
        // 如果之前是封禁状态，现在解禁了，显示提示
        if (previousStatus === 'banned') {
          console.log('🎉 用户已被解禁')
          // 可以选择显示一个友好的提示
          // alert('您的账号已解禁，可以正常使用了！')
        }
        
        // 更新本地用户信息（包括最新的 status）
        userAuth.updateStoredUser(user)
      }
    }
  } catch (error) {
    console.error('❌ 检测用户状态失败:', error)
    // 如果是 401 或 403 错误，可能是 token 失效或被封禁
    if (error instanceof Error) {
      if (error.message.includes('401')) {
        console.warn('🔐 Token 已过期')
        userAuth.clearSession()
        window.location.href = '/login?reason=expired'
      } else if (error.message.includes('403') || error.message.includes('banned')) {
        handleUserBanned()
      }
    }
  } finally {
    isChecking = false
  }
}

/**
 * 处理用户被封禁的情况
 */
function handleUserBanned() {
  // 停止检测
  stopBanDetection()
  
  // 清除会话
  userAuth.clearSession()
  
  // 显示提示
  alert('您的账号已被封禁，即将退出登录。如有疑问，请联系管理员。')
  
  // 重定向到登录页
  window.location.href = '/login?reason=banned'
}

/**
 * 手动触发一次检测
 */
export function checkNow() {
  return checkBanStatus()
}

export default {
  startBanDetection,
  stopBanDetection,
  checkNow,
}
