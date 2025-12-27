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
          <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">浏览历史</h1>
          <p class="text-gray-600">查看您最近浏览过的地点</p>
        </div>
        <button
          v-if="history.length > 0"
          @click="handleClearHistory"
          class="btn bg-gray-100 text-gray-700 hover:bg-secondary hover:text-white transition-all"
          :disabled="history.length === 0"
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
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
          清空历史
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
        <p class="text-gray-600">正在加载浏览历史...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="history.length === 0" class="card text-center py-16">
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
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-gray-500 text-lg">你还没有浏览过任何地点</p>
      <p class="text-gray-400 text-sm mt-2">开始探索校园吧！</p>
    </div>

    <!-- History List -->
    <div v-else class="space-y-3">
      <router-link
        v-for="item in history"
        :key="item.id"
        :to="`/location/${item.wikiId || item.buildingId}`"
        class="card flex items-center space-x-4 hover:shadow-medium transition-all group"
      >
        <div class="relative w-20 h-20 flex-shrink-0 overflow-hidden rounded-lg bg-gray-200">
          <img
            :src="item.imageUrl || '/placeholder-location.png'"
            :alt="item.name"
            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            @error="(e) => { console.error('❌ 图片加载失败:', item.name, item.imageUrl); e.target.src = '/placeholder-location.png' }"
            @load="() => console.log('✅ 图片加载成功:', item.name, item.imageUrl)"
          />
        </div>
        <div class="flex-1 min-w-0">
          <h3
            class="text-lg font-semibold text-gray-900 group-hover:text-primary transition-colors truncate"
          >
            {{ item.name }}
          </h3>
          <div class="flex items-center text-sm text-gray-500 mt-1">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            上次浏览: {{ item.lastVisited }}
          </div>
        </div>
        <svg
          class="w-5 h-5 text-gray-400 group-hover:text-primary transition-colors flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getBrowsingHistory, clearBrowsingHistory } from '../../api/user'
import { API_CONFIG } from '../../config/apiConfig'

const BACKEND_HOST = API_CONFIG.BACKEND_URL

const isLoading = ref(true)
const history = ref([])
const errorMessage = ref('')

// 处理图片 URL，使用相对路径让浏览器通过代理访问
const resolveImageUrl = (url) => {
  if (!url) return '/placeholder-location.png'

  // 如果已经是完整的 URL，直接返回
  if (/^https?:\/\//i.test(url)) {
    return url
  }

  // 处理 Windows 本地路径（如 F:\jitutong_wiki_backend\A楼.png）
  // 提取文件名，使用相对路径
  if (/^[A-Z]:\\/i.test(url) || url.includes('\\')) {
    const fileName = url.replace(/^.*[\\/]/, '')
    return `/uploads/${fileName}`  // 使用相对路径
  }

  // 相对路径，直接返回（不拼接 BACKEND_HOST）
  if (url.startsWith('/')) {
    return url  // 直接返回相对路径
  }
  
  // 其他情况，添加 /
  return `/${url}`
}

const loadHistory = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await getBrowsingHistory()
    console.log('📡 后端返回的浏览历史数据:', res)
    
    // 处理图片 URL
    history.value = (res.items || []).map(item => {
      const rawImageUrl = item.imageUrl || item.image_url || item.mainImage || item.main_image
      const processedImageUrl = resolveImageUrl(rawImageUrl)
      
      console.log('🖼️ 图片 URL 处理:', {
        name: item.name,
        raw: rawImageUrl,
        processed: processedImageUrl
      })
      
      return {
        ...item,
        imageUrl: processedImageUrl
      }
    })
    
    console.log('✅ 处理后的历史数据:', history.value)
  } catch (error) {
    console.error('获取浏览历史失败', error)
    errorMessage.value = error?.message || '获取浏览历史失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadHistory()
})

const handleClearHistory = async () => {
  if (!history.value.length) return
  if (!confirm('确定要清空所有浏览历史吗？此操作不可撤销。')) return
  try {
    await clearBrowsingHistory()
    history.value = []
  } catch (error) {
    console.error('清空浏览历史失败', error)
    alert(error?.message || '清空失败，请稍后重试')
  }
}
</script>
