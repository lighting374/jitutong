<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">个人中心</h1>
      <p class="text-gray-600">管理您的个人信息和偏好设置</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"
        ></div>
        <p class="text-gray-600">正在加载您的信息...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Profile Card -->
      <div class="card">
        <div v-if="!isEditing" class="text-center">
          <div class="relative inline-block mb-6">
            <img
              :src="getAvatarUrl(user.avatar)"
              alt="用户头像"
              class="w-32 h-32 rounded-full object-cover border-4 border-gray-100 shadow-md mx-auto"
              @error="handleImageError"
              @load="() => console.log('✅ 头像加载成功!')"
            />
            <div
              class="absolute bottom-0 right-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center shadow-lg"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>
          <h2 class="text-2xl font-heading font-bold text-gray-900 mb-2">{{ user.nickname }}</h2>
          <p class="text-gray-600 mb-6">同济大学用户</p>
          <button @click="handleEdit" class="btn btn-primary">
            <svg
              class="w-5 h-5 inline-block mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            编辑资料
          </button>
        </div>

        <!-- Edit Form -->
        <form v-else @submit.prevent="handleSave" class="space-y-6">
          <div class="text-center">
            <div class="relative inline-block mb-4">
              <img
                :src="editForm.avatar || '/avatar.jpg'"
                alt="头像预览"
                class="w-32 h-32 rounded-full object-cover border-4 border-gray-100 shadow-md"
              />
              <label
                for="avatar-upload"
                class="absolute bottom-0 right-0 w-10 h-10 bg-primary hover:bg-primary/90 rounded-full flex items-center justify-center shadow-lg cursor-pointer transition-all"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </label>
              <input
                id="avatar-upload"
                type="file"
                @change="handleAvatarChange"
                accept="image/*"
                class="hidden"
              />
            </div>
            <p class="text-sm text-gray-500 mb-6">点击相机图标更换头像</p>
          </div>

          <div>
            <label for="nickname" class="block text-sm font-medium text-gray-700 mb-2">昵称</label>
            <input
              id="nickname"
              type="text"
              v-model="editForm.nickname"
              placeholder="请输入2-10个字符的昵称"
              class="input-field"
            />
            <p v-if="nicknameError" class="mt-2 text-sm text-secondary">{{ nicknameError }}</p>
          </div>

          <div class="flex gap-3 justify-end">
            <button type="button" @click="handleCancel" class="btn btn-ghost">取消</button>
            <button type="submit" class="btn btn-accent" :disabled="isSaving">
              <span v-if="isSaving" class="flex items-center">
                <svg
                  class="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                保存中...
              </span>
              <span v-else>保存</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Quick Links -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <router-link
          to="/my-comments"
          class="card group hover:shadow-medium hover:border-primary/20 border border-transparent transition-all"
        >
          <div class="flex items-center space-x-4">
            <div
              class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center group-hover:bg-primary/10 transition-colors"
            >
              <svg
                class="w-6 h-6 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 group-hover:text-primary transition-colors">
                我的评论与评分
              </h3>
              <p class="text-sm text-gray-600">查看您的所有评论</p>
            </div>
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </router-link>

        <router-link
          to="/my-favorites"
          class="card group hover:shadow-medium hover:border-primary/20 border border-transparent transition-all"
        >
          <div class="flex items-center space-x-4">
            <div
              class="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center group-hover:bg-secondary/10 transition-colors"
            >
              <svg class="w-6 h-6 text-secondary" fill="currentColor" viewBox="0 0 24 24">
                <path
                  d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 group-hover:text-primary transition-colors">
                我的收藏地点
              </h3>
              <p class="text-sm text-gray-600">管理收藏的地点</p>
            </div>
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </router-link>

        <router-link
          to="/my-history"
          class="card group hover:shadow-medium hover:border-primary/20 border border-transparent transition-all"
        >
          <div class="flex items-center space-x-4">
            <div
              class="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center group-hover:bg-purple-100 transition-colors"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 group-hover:text-primary transition-colors">
                浏览历史
              </h3>
              <p class="text-sm text-gray-600">回顾浏览过的地点</p>
            </div>
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </router-link>

        <router-link
          to="/my-messages"
          class="card group hover:shadow-medium hover:border-primary/20 border border-transparent transition-all relative"
        >
          <div class="flex items-center space-x-4">
            <div
              class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center group-hover:bg-accent/10 transition-colors relative"
            >
              <svg
                class="w-6 h-6 text-accent"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
              <span
                v-if="unreadCount > 0"
                class="absolute -top-1 -right-1 min-w-[1.25rem] h-5 px-1 bg-secondary text-white text-xs rounded-full flex items-center justify-center"
                >{{ unreadCount }}</span
              >
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 group-hover:text-primary transition-colors">
                消息通知
              </h3>
              <p class="text-sm text-gray-600">查看最新通知</p>
            </div>
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </router-link>
      </div>

      <!-- Logout Button -->
      <div class="card">
        <button
          @click="handleLogout"
          class="w-full btn bg-gray-100 text-gray-700 hover:bg-secondary hover:text-white transition-all"
        >
          <svg
            class="w-5 h-5 inline-block mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
          登出账号
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getUserProfile,
  getUserMessages,
  updateUserProfile as updateUserProfileApi,
} from '../../api/user'
import userAuth from '../../services/userAuth'
import { fixAvatarUrl } from '../../config/apiConfig'

const router = useRouter()

const user = ref({
  id: '',
  nickname: '',
  avatar: '/avatar.jpg',
  bio: '',
  gender: '',
})
const editForm = ref<{
  nickname: string
  bio: string
  avatar: string
  avatarFile?: File
}>({
  nickname: '',
  bio: '',
  avatar: '',
  avatarFile: undefined,
})

const isLoading = ref(true)
const isEditing = ref(false)
const isSaving = ref(false)
const nicknameError = ref('')
const unreadCount = ref(0)

const fetchUnreadCount = async () => {
  try {
    const res = await getUserMessages()
    unreadCount.value = res?.unreadCount || 0
  } catch (error) {
    console.error('获取未读消息失败:', error)
    unreadCount.value = 0
  }
}

// 加载用户信息
const loadUserData = async () => {
  isLoading.value = true
  try {
    const data = await getUserProfile()
    console.log('📥 getUserProfile 返回的数据:', data)
    
    // 兼容后端的 avatar_url 和 avatar 字段
    const rawAvatar = data.avatar || data.avatar_url
    console.log('🖼️ 原始头像字段:', rawAvatar)
    
    // 修复头像 URL：如果是相对路径，转换为完整 URL
    let avatarUrl = fixAvatarUrl(rawAvatar)
    console.log('🔍 处理后的头像 URL:', avatarUrl)
    
    // 优先使用 localStorage 中的头像（如果有）
    const localUser = userAuth.getUser()
    const finalAvatarUrl = avatarUrl !== '/avatar.jpg' ? avatarUrl : (localUser?.avatar || '/avatar.jpg')
    
    console.log('💾 localStorage 中的头像:', localUser?.avatar)
    console.log('✅ 最终使用的头像 URL:', finalAvatarUrl)
    
    user.value = {
      ...user.value,
      ...data,
      avatar: finalAvatarUrl,
    }
    
    // 测试图片是否可访问
    if (avatarUrl && avatarUrl.startsWith('http')) {
      console.log('🧪 测试图片是否可访问:', avatarUrl)
      fetch(avatarUrl, { method: 'HEAD' })
        .then(res => {
          if (res.ok) {
            console.log('✅ 图片可访问！状态码:', res.status)
          } else {
            console.error('❌ 图片不可访问！状态码:', res.status)
          }
        })
        .catch(err => console.error('❌ 图片请求失败:', err))
    }
    
    await fetchUnreadCount()
  } catch (error) {
    console.error('加载用户信息失败:', error)
    alert('登录状态已失效，请重新登录。')
    userAuth.clearSession()
    router.push({ name: 'Login' })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (!userAuth.isAuthenticated()) {
    router.push({ name: 'Login' })
    return
  }
  await loadUserData()
})

// --- 事件处理方法 ---

// 1. 点击 "编辑资料"
const handleEdit = () => {
  editForm.value = {
    nickname: user.value.nickname,
    bio: user.value.bio,
    avatar: user.value.avatar,
    avatarFile: undefined,  // 清除之前的文件
  }
  isEditing.value = true
  nicknameError.value = '' // 清除旧的错误信息
}

// 2. 点击 "取消"
const handleCancel = () => {
  // 清理预览 URL
  if (editForm.value.avatar && editForm.value.avatar.startsWith('blob:')) {
    URL.revokeObjectURL(editForm.value.avatar)
  }
  isEditing.value = false
}

// 3. 处理头像文件更改
const handleAvatarChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }
    
    // 验证文件大小（最大 2MB）
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过 2MB')
      return
    }
    
    // 保存 File 对象，用于上传
    editForm.value.avatarFile = file
    
    // 创建预览 URL
    const previewUrl = URL.createObjectURL(file)
    editForm.value.avatar = previewUrl
    
    console.log('✅ 头像文件已选择:', file.name, '大小:', (file.size / 1024).toFixed(2), 'KB')
  }
}

// 4. 表单验证
const validateForm = () => {
  nicknameError.value = ''
  const nickname = editForm.value.nickname.trim()
  if (nickname.length < 2 || nickname.length > 16) {
    nicknameError.value = '昵称长度必须在 2 到 16 个字符之间'
    return false
  }
  return true
}

// 5. 点击 "保存"
const handleSave = async () => {
  if (!validateForm()) {
    return // 验证失败，停止提交
  }

  isSaving.value = true
  try {
    console.log('📤 提交更新数据:', {
      nickname: editForm.value.nickname,
      bio: editForm.value.bio,
      hasAvatarFile: !!editForm.value.avatarFile,
      avatarFileName: editForm.value.avatarFile?.name
    })
    
    // 传递数据和头像文件
    const response = await updateUserProfileApi(
      {
        nickname: editForm.value.nickname,
        bio: editForm.value.bio,
      },
      editForm.value.avatarFile  // 传递 File 对象
    )
    console.log('📥 后端返回:', response)
    
    // 更新本地用户信息
    if (response && response.user) {
      // 后端返回了完整的用户信息
      const updatedUser = { ...response.user }
      
      // 修复头像 URL：如果是相对路径，转换为完整 URL
      if (updatedUser.avatar) {
        updatedUser.avatar = fixAvatarUrl(updatedUser.avatar)
        console.log('🔧 修复头像 URL:', updatedUser.avatar)
      }
      
      user.value = {
        ...user.value,
        ...updatedUser,
      }
      console.log('✅ 使用后端返回的用户信息')
    } else {
      // 后端没有返回用户信息，手动更新
      user.value = {
        ...user.value,
        nickname: editForm.value.nickname,
        bio: editForm.value.bio,
      }
      console.log('⚠️ 后端未返回用户信息，使用本地数据')
    }
    
    console.log('✅ 本地用户信息已更新:', {
      nickname: user.value.nickname,
      avatar: user.value.avatar,
      avatarIsUrl: user.value.avatar?.startsWith('http'),
      fullUserObject: user.value
    })
    
    console.log('🖼️ 头像将显示为:', getAvatarUrl(user.value.avatar))
    
    // 清理 blob URL
    if (editForm.value.avatar && editForm.value.avatar.startsWith('blob:')) {
      URL.revokeObjectURL(editForm.value.avatar)
    }
    
    // 保存到 localStorage
    userAuth.updateStoredUser(user.value)
    
    // 更新时间戳，强制刷新头像
    avatarTimestamp.value = Date.now()
    console.log('🔄 已更新头像时间戳:', avatarTimestamp.value)
    
    // 退出编辑模式
    isEditing.value = false
    
    // 强制重新加载用户信息，确保头像立即显示
    await loadUserData()
    alert('资料更新成功！')
  } catch (error) {
    console.error('❗ 更新失败:', error)
    alert('更新失败，请稍后重试。')
  } finally {
    isSaving.value = false
  }
}

// 6. 获取头像 URL（添加时间戳防止缓存）
const avatarTimestamp = ref(Date.now())

const getAvatarUrl = (avatar: string | undefined) => {
  if (!avatar || avatar === '/avatar.jpg') {
    return '/avatar.jpg'
  }
  
  // 如果是完整 URL，添加时间戳防止缓存
  if (avatar.startsWith('http')) {
    const separator = avatar.includes('?') ? '&' : '?'
    return `${avatar}${separator}t=${avatarTimestamp.value}`
  }
  
  return avatar
}

// 7. 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  console.error('❌ 头像加载失败:', img.src)
  console.error('🔍 请在浏览器新标签页打开这个 URL 测试:', img.src.split('?')[0])
  
  // 尝试不带时间戳加载
  const urlWithoutTimestamp = img.src.split('?')[0] || '/avatar.jpg'
  if (img.src.includes('?')) {
    console.log('🔄 尝试不带时间戳加载...')
    img.src = urlWithoutTimestamp
  } else {
    // 如果还是失败，使用默认头像
    img.src = '/avatar.jpg'
  }
}

// 8. 点击 "登出"
const handleLogout = () => {
  // 确认：弹出确认框
  if (confirm('您确定要登出吗？')) {
    userAuth.clearSession()
    router.push({ name: 'Login' })
  }
}
</script>
