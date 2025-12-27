<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
    <!-- Page Header -->
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
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">消息通知</h1>
          <p class="text-gray-600">
            查看您的最新通知
            <span v-if="unreadCount > 0" class="text-secondary font-medium ml-2"
              >({{ unreadCount }} 条未读)</span
            >
          </p>
        </div>
        <button v-if="unreadCount > 0" @click="handleMarkAllAsRead" class="btn btn-outline text-sm">
          <svg
            class="w-4 h-4 inline-block mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          全部已读
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="card border border-red-100 bg-red-50 text-red-600 mb-6">
      {{ errorMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"
        ></div>
        <p class="text-gray-600">正在加载消息...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="messages.length === 0" class="card text-center py-16">
      <svg
        class="w-16 h-16 text-gray-300 mx-auto mb-4"
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
      <p class="text-gray-500 text-lg">你还没有收到任何消息</p>
      <p class="text-gray-400 text-sm mt-2">有新通知时会显示在这里</p>
    </div>

    <!-- Messages List -->
    <div v-else class="space-y-2">
      <div
        v-for="message in messages"
        :key="message.id"
        @click="handleMessageClick(message)"
        class="card cursor-pointer hover:shadow-medium transition-all group relative"
        :class="{ 'bg-blue-50 border-l-4 border-l-primary': !message.read }"
      >
        <div class="flex items-start space-x-4">
          <!-- Icon -->
          <div
            class="w-12 h-12 flex-shrink-0 rounded-full flex items-center justify-center"
            :class="{
              'bg-blue-100': message.type === 'comment_reply',
              'bg-red-100': message.type === 'like',
              'bg-gray-100': message.type === 'system',
            }"
          >
            <svg
              v-if="message.type === 'comment_reply'"
              class="w-6 h-6 text-primary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <svg
              v-else-if="message.type === 'like'"
              class="w-6 h-6 text-secondary"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
              />
            </svg>
            <svg
              v-else
              class="w-6 h-6 text-gray-600"
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
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p class="text-gray-900 leading-relaxed" :class="{ 'font-medium': !message.read }">
              {{ message.content }}
            </p>
            <div class="flex items-center mt-2 text-sm text-gray-500">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {{ message.date }}
            </div>
          </div>

          <!-- Unread Indicator -->
          <div v-if="!message.read" class="flex-shrink-0">
            <div class="w-3 h-3 bg-secondary rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { getUserMessages, markMessageRead, markAllMessagesRead } from '../../api/user'

const isLoading = ref(true)
const messages = ref([])
const router = useRouter()
const errorMessage = ref('')

const loadMessages = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await getUserMessages()
    console.log('📨 后端返回的消息数据:', res)
    console.log('📨 res.items:', res.items)
    console.log('📨 res.messages:', res.messages)
    // 后端返回的是 messages 字段，不是 items
    messages.value = res.messages || res.items || []
    console.log('📨 最终 messages 数量:', messages.value.length)
  } catch (error) {
    console.error('获取消息失败', error)
    errorMessage.value = error?.message || '获取消息失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadMessages()
})

const unreadCount = computed(() => {
  return messages.value.filter((m) => !m.read).length
})

const handleMessageClick = async (message) => {
  if (!message.read) {
    message.read = true
    try {
      await markMessageRead(message.id)
    } catch (error) {
      console.error('标记消息失败', error)
    }
  }

  if (message.link) {
    router.push(message.link)
  }
}

const handleMarkAllAsRead = async () => {
  try {
    await markAllMessagesRead()
    messages.value.forEach((m) => {
      m.read = true
    })
  } catch (error) {
    console.error('全部已读失败', error)
    alert(error?.message || '操作失败，请稍后重试')
  }
}
</script>
