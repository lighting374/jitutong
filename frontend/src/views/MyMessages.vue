<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <router-link
          to="/user"
          class="inline-flex items-center text-gray-600 hover:text-primary transition-colors mb-4"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          返回个人中心
        </router-link>
        <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">📬 消息通知</h1>
        <p class="text-gray-600">查看您的评论互动消息</p>
      </div>

      <!-- 筛选标签 -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div class="flex items-center space-x-4 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            @click="activeTab = tab.value"
            class="px-4 py-2 rounded-lg whitespace-nowrap transition-colors"
            :class="activeTab === tab.value 
              ? 'bg-primary text-white' 
              : 'text-gray-600 hover:bg-gray-100'"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="ml-2 px-2 py-0.5 text-xs rounded-full"
              :class="activeTab === tab.value ? 'bg-white text-primary' : 'bg-gray-200 text-gray-700'">
              {{ tab.count }}
            </span>
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p class="text-gray-600">加载中...</p>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else-if="filteredMessages.length > 0" class="space-y-4">
        <div
          v-for="message in filteredMessages"
          :key="message.id"
          class="bg-white rounded-lg shadow-sm p-6 transition-all hover:shadow-md"
          :class="message.isRead ? 'opacity-75' : 'border-l-4 border-primary'"
        >
          <div class="flex items-start space-x-4">
            <!-- 图标 -->
            <div class="flex-shrink-0">
              <div class="w-12 h-12 rounded-full flex items-center justify-center"
                :class="getMessageIconBg(message.type)">
                <span class="text-2xl">{{ getMessageIcon(message.type) }}</span>
              </div>
            </div>

            <!-- 内容 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ getMessageTitle(message.type) }}
                  </h3>
                  <span v-if="!message.isRead" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                    新
                  </span>
                </div>
                <span class="text-sm text-gray-500">{{ formatDate(message.createdAt) }}</span>
              </div>

              <p class="text-gray-700 mb-3">{{ message.content }}</p>

              <!-- 相关评论预览 -->
              <div v-if="message.relatedComment" class="bg-gray-50 rounded-lg p-3 mb-3">
                <p class="text-sm text-gray-600 line-clamp-2">{{ message.relatedComment }}</p>
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center space-x-4">
                <button
                  v-if="message.linkUrl"
                  @click="handleViewDetail(message)"
                  class="text-primary hover:text-primary-dark text-sm font-medium"
                >
                  查看详情 →
                </button>
                <button
                  v-if="!message.isRead"
                  @click="markAsRead(message.id)"
                  class="text-gray-500 hover:text-gray-700 text-sm"
                >
                  标记已读
                </button>
                <button
                  @click="deleteMessage(message.id)"
                  class="text-red-500 hover:text-red-700 text-sm"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="bg-white rounded-lg shadow-sm p-12 text-center">
        <div class="text-6xl mb-4">📭</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">暂无消息</h3>
        <p class="text-gray-600">当有人与您的评论互动时，您会在这里收到通知</p>
      </div>

      <!-- 批量操作 -->
      <div v-if="messages.length > 0" class="mt-6 flex justify-center space-x-4">
        <button
          @click="markAllAsRead"
          class="px-6 py-2 bg-white text-gray-700 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
        >
          全部标记为已读
        </button>
        <button
          @click="clearAllMessages"
          class="px-6 py-2 bg-white text-red-600 rounded-lg border border-red-300 hover:bg-red-50 transition-colors"
        >
          清空所有消息
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Message {
  id: number
  type: 'like' | 'reply' | 'report'
  content: string
  relatedComment?: string
  linkUrl?: string
  isRead: boolean
  createdAt: string
}

const loading = ref(true)
const messages = ref<Message[]>([])
const activeTab = ref('all')

const tabs = computed(() => [
  { value: 'all', label: '全部', count: messages.value.length },
  { value: 'like', label: '点赞', count: messages.value.filter(m => m.type === 'like').length },
  { value: 'reply', label: '回复', count: messages.value.filter(m => m.type === 'reply').length },
  { value: 'report', label: '举报', count: messages.value.filter(m => m.type === 'report').length },
  { value: 'unread', label: '未读', count: messages.value.filter(m => !m.isRead).length },
])

const filteredMessages = computed(() => {
  if (activeTab.value === 'all') {
    return messages.value
  } else if (activeTab.value === 'unread') {
    return messages.value.filter(m => !m.isRead)
  } else {
    return messages.value.filter(m => m.type === activeTab.value)
  }
})

// 获取消息图标
const getMessageIcon = (type: string) => {
  const icons = {
    like: '❤️',
    reply: '💬',
    report: '⚠️'
  }
  return icons[type as keyof typeof icons] || '📬'
}

// 获取消息图标背景色
const getMessageIconBg = (type: string) => {
  const colors = {
    like: 'bg-red-100',
    reply: 'bg-blue-100',
    report: 'bg-yellow-100'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-100'
}

// 获取消息标题
const getMessageTitle = (type: string) => {
  const titles = {
    like: '收到点赞',
    reply: '收到回复',
    report: '评论被举报'
  }
  return titles[type as keyof typeof titles] || '新消息'
}

// 格式化时间
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  // 如果时间为负数（未来时间或时间差异常），显示“刚刚”
  if (days < 0) {
    return '刚刚'
  }

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      // 如果分钟数为负数或零，显示"0分钟前"
      if (minutes <= 0) {
        return '0分钟前'
      }
      return `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  }
  return date.toLocaleDateString('zh-CN')
}

// 加载消息
const loadMessages = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('user_token')
    if (!token) {
      router.push('/user/login')
      return
    }

    const response = await fetch('/api/user/messages', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取消息失败')
    }

    const data = await response.json()
    console.log('后端返回的消息数据:', data)
    console.log('data.items:', data.items)
    console.log('data.messages:', data.messages)
    messages.value = data.items || data.messages || []
  } catch (error) {
    console.error('加载消息失败:', error)
    alert('加载消息失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleViewDetail = (message: Message) => {
  if (message.linkUrl) {
    // 标记为已读
    if (!message.isRead) {
      markAsRead(message.id)
    }
    
    // 处理 URL，将 /locations/ 转换为 /location/
    let targetUrl = message.linkUrl
    if (targetUrl.startsWith('/locations/')) {
      targetUrl = targetUrl.replace('/locations/', '/location/')
    }
    
    // 如果当前已经在目标页面，先跳转到消息页，再跳转回去（强制刷新）
    if (router.currentRoute.value.path === targetUrl.split('?')[0]) {
      // 当前在目标页面，直接刷新
      window.location.href = targetUrl
    } else {
      // 不在目标页面，正常跳转
      router.push(targetUrl)
    }
  }
}

// 标记为已读
const markAsRead = async (messageId: number) => {
  try {
    const token = localStorage.getItem('user_token')
    const response = await fetch(`/api/user/messages/${messageId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const message = messages.value.find(m => m.id === messageId)
      if (message) {
        message.isRead = true
      }
    }
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

// 删除消息
const deleteMessage = async (messageId: number) => {
  if (!confirm('确定要删除这条消息吗？')) return

  try {
    const token = localStorage.getItem('user_token')
    const response = await fetch(`/api/user/messages/${messageId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      messages.value = messages.value.filter(m => m.id !== messageId)
    }
  } catch (error) {
    console.error('删除消息失败:', error)
    alert('删除失败，请稍后重试')
  }
}

// 全部标记为已读
const markAllAsRead = async () => {
  try {
    const token = localStorage.getItem('user_token')
    const response = await fetch('/api/user/messages/read-all', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      messages.value.forEach(m => m.isRead = true)
    }
  } catch (error) {
    console.error('标记全部已读失败:', error)
    alert('操作失败，请稍后重试')
  }
}

// 清空所有消息
const clearAllMessages = async () => {
  if (!confirm('确定要清空所有消息吗？此操作不可恢复。')) return

  try {
    const token = localStorage.getItem('user_token')
    const response = await fetch('/api/user/messages/clear', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      messages.value = []
    }
  } catch (error) {
    console.error('清空消息失败:', error)
    alert('操作失败，请稍后重试')
  }
}

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
