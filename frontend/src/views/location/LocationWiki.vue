<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center min-h-screen">
      <div class="text-center">
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"
        ></div>
        <p class="text-gray-600">正在加载地点信息...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
      <div class="card text-center">
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
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">加载失败</h2>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button @click="fetchWikiData" class="btn btn-primary">重试</button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="wikiData" class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- Breadcrumb Navigation -->
      <nav class="mb-6">
        <ol class="flex items-center space-x-2 text-sm text-gray-600">
          <li>
            <router-link to="/wiki" class="hover:text-primary transition-colors">首页</router-link>
          </li>
          <li>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </li>
          <template v-for="(item, index) in (wikiData.categoryPath || [])" :key="index">
            <li>
              <router-link
                v-if="item.path"
                :to="item.path"
                class="hover:text-primary transition-colors"
              >
                {{ item.name }}
              </router-link>
              <span v-else>{{ item.name }}</span>
            </li>
            <li v-if="index < (wikiData.categoryPath || []).length - 1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </li>
          </template>
        </ol>
      </nav>


      <!-- Header Section with Main Image -->
      <div class="mb-8">
        <div class="relative w-full h-64 md:h-96 rounded-2xl overflow-hidden shadow-strong mb-6">
          <img
            :src="fixAvatarUrl(wikiData.mainImage) || '/placeholder-location.jpg'"
            :alt="localizedName"
            class="w-full h-full object-cover"
          />
          <div
            class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"
          ></div>
          <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
            <h1 class="text-3xl md:text-4xl font-heading font-bold mb-2">
              {{ localizedName }}
              <span class="text-sm ml-3 px-2 py-1 bg-black/50 rounded">
                状态: {{ isFavorited ? '已收藏✅' : '未收藏' }}
              </span>
            </h1>
            <div class="flex items-center text-gray-200">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>{{ localizedAddress }}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap gap-3">
          <button
            @click="handleFavorite"
            :disabled="isSubmittingFavorite"
            :class="[
              'btn', 
              isFavorited ? 'bg-secondary text-white' : 'btn-ghost',
              isSubmittingFavorite ? 'opacity-50 cursor-not-allowed' : ''
            ]"
          >
            <svg
              v-if="!isSubmittingFavorite"
              class="w-5 h-5 inline-block mr-2"
              :fill="isFavorited ? 'currentColor' : 'none'"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
            <div v-else class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-2"></div>
            {{ isSubmittingFavorite ? '处理中...' : (isFavorited ? '已收藏' : '收藏') }}
          </button>
          <button
            @click="shareLocation"
            :disabled="isGeneratingImage"
            class="btn btn-primary"
          >
            <svg
              v-if="!isGeneratingImage"
              class="w-5 h-5 inline-block mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
              />
            </svg>
            <span v-else class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
            {{ isGeneratingImage ? '生成中...' : '分享' }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Rich Text Content -->
          <div class="card">
            <div class="prose prose-lg max-w-none wiki-content" v-html="localizedRichContent || '<p>暂无内容</p>'"></div>
          </div>

          <!-- Rating Section -->
          <RatingDisplay v-if="wikiData.rating" :rating="wikiData.rating" />

          <!-- Submit Comment Section (发表评论) -->
          <CommentForm
            :location-id="locationId"
            :user-token="userToken"
            @submitted="handleCommentSubmitted"
          />

          <!-- 热门标签云（评论筛选） -->
          <div v-if="popularTags.length > 0" class="card mb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">🏷️ 热门标签</h3>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in popularTags"
                :key="tag.name"
                @click="toggleTagFilter(tag.name)"
                class="px-3 py-1.5 rounded-full text-sm transition-all hover:scale-105"
                :class="selectedTags.includes(tag.name)
                  ? 'bg-primary text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
              >
                # {{ tag.name }}
                <span class="ml-1 text-xs opacity-75">({{ tag.count }})</span>
              </button>
            </div>
            <button
              v-if="selectedTags.length > 0"
              @click="clearTagFilter"
              class="mt-3 text-sm text-gray-500 hover:text-gray-700"
            >
              清除筛选 ({{ selectedTags.length }})
            </button>
          </div>

          <!-- Comments List Section (独立评论列表) -->
          <CommentsList
            :comments-data="commentsData"
            :loading="commentsLoading"
            @page-change="handlePageChange"
          />
        </div>

        <!-- Sidebar -->
        <aside class="space-y-6">
          <!-- Structured Info Card -->
          <div class="card">
            <h2 class="text-xl font-heading font-bold text-dark-blue mb-4">地点信息</h2>
            <dl class="space-y-3">
              <div v-if="localizedStructuredInfo?.openTime">
                <dt class="text-sm font-medium text-gray-500 mb-1">开放时间</dt>
                <dd class="text-gray-900">{{ localizedStructuredInfo.openTime }}</dd>
              </div>
              <div v-if="localizedStructuredInfo?.averageCost">
                <dt class="text-sm font-medium text-gray-500 mb-1">人均消费</dt>
                <dd class="text-gray-900">{{ localizedStructuredInfo.averageCost }}</dd>
              </div>
              <div v-if="localizedStructuredInfo?.phone">
                <dt class="text-sm font-medium text-gray-500 mb-1">联系电话</dt>
                <dd class="text-gray-900">
                  <a
                    :href="`tel:${localizedStructuredInfo.phone}`"
                    class="text-primary hover:underline"
                  >
                    {{ localizedStructuredInfo.phone }}
                  </a>
                </dd>
              </div>
              <div v-if="localizedStructuredInfo?.website">
                <dt class="text-sm font-medium text-gray-500 mb-1">官方网站</dt>
                <dd class="text-gray-900">
                  <a
                    :href="localizedStructuredInfo.website"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-primary hover:underline break-all"
                  >
                    {{ localizedStructuredInfo.website }}
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          <!-- Tags（只显示，不可点击） -->
          <TagCloud
            v-if="localizedTags && localizedTags.length > 0"
            :tags="localizedTags"
            :clickable="false"
          />
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getLocationWiki,
  getLocationComments,
  type LocationWikiData,
  type ReviewListResponse,
} from '@/api/location'
import {
  getFavoriteStatus,
  addFavorite as addFavoriteApi,
  removeFavorite as removeFavoriteApi,
  addBrowsingHistory as addHistoryApi,
} from '@/api/user'
import userAuth from '../../services/userAuth'
import { getBuildingIdFromWikiId } from '../../config/buildingMapping'
import { fixAvatarUrl } from '../../config/apiConfig'
import { getLocale, setLocale, onLocaleChange, type SupportedLocale } from '../../services/locale'
import CommentForm from '../../components/location/CommentForm.vue'
import CommentsList from '../../components/location/CommentsList.vue'
import RatingDisplay from '../../components/location/RatingDisplay.vue'
import TagCloud from '../../components/location/TagCloud.vue'

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const error = ref<string | null>(null)
const wikiData = ref<LocationWikiData | null>(null)
const isFavorited = ref(false)
const isSubmittingFavorite = ref(false) // 防止重复点击
const isGeneratingImage = ref(false) // 分享图片生成状态
const userToken = ref<string | null>(userAuth.getToken())
const buildingIdRef = ref<number | null>(null)

// 获取地点 ID (Wiki ID)
const locationId = route.params.id as string

// 获取对应的建筑ID（用于收藏功能）
const buildingId = computed(() => {
  return getBuildingIdFromWikiId(Number(locationId))
})

const currentLang = ref<SupportedLocale>('zh')
const missingI18nFields = ref<string[]>([])

// 评论列表相关状态
const commentsLoading = ref(false)
const commentsData = ref<ReviewListResponse | null>(null)
const commentsPage = ref(1)
const commentsPageSize = ref(10)

// 标签相关状态
const popularTags = ref<Array<{ name: string; count: number }>>([])
const selectedTags = ref<string[]>([])

// 图片预览相关状态
const imagePreview = ref<{
  show: boolean
  currentImage: string
  images: string[]
  currentIndex: number
}>({
  show: false,
  currentImage: '',
  images: [],
  currentIndex: 0,
})

// 发表评论相关状态
const fileInputRef = ref<HTMLInputElement | null>(null)
const isSubmittingComment = ref(false)
const isUploading = ref(false)
const commentForm = ref<{
  rating: number
  comment: string
  images: Array<{ url: string; file?: File; status?: 'uploading' | 'success' | 'error' }>
}>({
  rating: 0,
  comment: '',
  images: [],
})

const commentErrors = ref<{
  rating?: string
  comment?: string
}>({})


const addMissingField = (field: string) => {
  if (!missingI18nFields.value.includes(field)) {
    missingI18nFields.value.push(field)
  }
}

const resolveWikiField = (field: string, fallback: any = '', trackMissing = true) => {
  const data: any = wikiData.value
  const lang = currentLang.value
  if (!data) return fallback ?? ''

  const translations = data.translations?.[lang] || data.i18n?.[lang]
  let value =
    translations?.[field] ??
    data[`${field}_${lang}`] ??
    (lang === 'en' ? data[`${field}En`] ?? data[`${field}_en`] : undefined)

  if (value === undefined || value === null || value === '') {
    value = data[field] ?? fallback ?? ''
    if (trackMissing && lang !== 'zh' && (value === undefined || value === null || value === '')) {
      addMissingField(field)
    }
  }
  return value
}

const localizedName = computed(() => resolveWikiField('name', wikiData.value?.name))
const localizedAddress = computed(() => resolveWikiField('address', wikiData.value?.address))
const localizedRichContent = computed(() => resolveWikiField('richContent', wikiData.value?.richContent))

// 结构化信息：现在直接使用后端返回的 structuredInfo
// 后端会根据当前语言返回合适的字段，不再依赖前端的 translations 合并逻辑
const localizedStructuredInfo = computed(() => {
  return wikiData.value?.structuredInfo || {}
})

const localizedTags = computed(() => {
  const tags = wikiData.value?.tags || []
  if (!tags.length) return tags
  const lang = currentLang.value
  if (lang === 'zh') return tags

  return tags.map((tag: any) => {
    const translated =
      tag?.translations?.[lang]?.name ??
      tag?.[`name_${lang}`] ??
      (lang === 'en' ? tag?.nameEn ?? tag?.name_en : undefined) ??
      tag?.name
    if (!translated) {
      addMissingField('tags')
    }
    return { ...tag, name: translated || tag?.name }
  })
})


// 获取 Wiki 数据
const fetchWikiData = async () => {
  isLoading.value = true
  error.value = null
  missingI18nFields.value = []

  try {
    // 调用 API 获取数据（后端根据语言返回对应内容）
    wikiData.value = await getLocationWiki(locationId)
    
    console.log('后端返回的 Wiki 数据:', {
      id: wikiData.value?.id,
      buildingId: wikiData.value?.buildingId,
      structuredInfo: wikiData.value?.structuredInfo
    })

    // Building ID = Wiki ID，直接使用 locationId
    const wikiNumericId = Number(locationId)
    buildingIdRef.value = wikiNumericId
    
    console.log('Wiki 页面加载 - buildingId:', buildingIdRef.value, 'wikiId:', wikiNumericId)

    await fetchFavoriteStatus()
    await recordBrowsingHistory()
  } catch (err: any) {
    // API 调用失败，显示错误信息
    console.error('获取 Wiki 数据失败:', err)
    error.value = err.message || '加载失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

// 保留备用模拟数据函数（仅用于开发调试，实际应该删除）
const getMockWikiData = (id: number): LocationWikiData => {
  return {
    id,
    name: '嘉定校区图书馆',
    address: '上海市嘉定区曹安公路4800号同济大学嘉定校区',
    mainImage: '/图书馆材料学院.jpg',
    category: '学习场所',
    categoryPath: [
      { name: '首页', path: '/' },
      { name: '学习场所', path: '/category/study' },
      { name: '图书馆' },
    ],
    richContent: `
      <h2>图书馆简介</h2>
      <p>同济大学嘉定校区图书馆是一座现代化的学术建筑，为师生提供了丰富的学习资源和舒适的学习环境。</p>
      
      <h3>馆藏资源</h3>
      <ul>
        <li>纸质图书：超过100万册</li>
        <li>电子资源：包含各类数据库和电子期刊</li>
        <li>特殊馆藏：建筑、土木、材料等相关专业资料</li>
      </ul>
      
      <h3>开放区域</h3>
      <p>图书馆共分为多个区域：</p>
      <ul>
        <li><strong>阅览区</strong>：提供安静的阅读环境，配有舒适的座椅</li>
        <li><strong>自习区</strong>：适合小组讨论和自主学习</li>
        <li><strong>电子阅览室</strong>：配备电脑，可访问各类电子资源</li>
        <li><strong>讨论室</strong>：可预约用于小组讨论</li>
      </ul>
      
      <h3>服务设施</h3>
      <p>图书馆提供以下服务：</p>
      <ul>
        <li>图书借还服务</li>
        <li>参考咨询服务</li>
        <li>打印复印服务</li>
        <li>WIFI全覆盖</li>
        <li>充电插座</li>
      </ul>
      
      <h3>使用建议</h3>
      <p>建议在考试周提前到达，座位较为紧张。可通过图书馆官网或APP提前预约座位。</p>
    `,
    structuredInfo: {
      openTime: '周一至周日 8:00 - 22:00',
      averageCost: '免费',
      phone: '021-69585000',
      website: 'https://lib.tongji.edu.cn',
      coordinates: {
        lat: 31.2857,
        lng: 121.2088,
      },
    },
    rating: {
      average: 4.5,
      count: 128,
      distribution: [
        { stars: 5, count: 80 },
        { stars: 4, count: 32 },
        { stars: 3, count: 12 },
        { stars: 2, count: 3 },
        { stars: 1, count: 1 },
      ],
    },
    comments: [],
    tags: [
      { id: 1, name: '图书馆', color: '#5368df' },
      { id: 2, name: '学习', color: '#34c759' },
      { id: 3, name: '安静', color: '#fa5757' },
      { id: 4, name: '免费', color: '#ff9500' },
    ],
    canEdit: false,
  }
}

// 处理编辑
const handleEdit = () => {
  router.push(`/location/${locationId}/edit`)
}

// 分享地点
const shareLocation = async () => {
  if (!wikiData.value) return
  
  isGeneratingImage.value = true
  
  try {
    // 获取当前页面URL
    const url = window.location.href
    
    // 复制到剪贴板
    await navigator.clipboard.writeText(url)
    
    // 提示成功
    alert(`链接已复制到剪贴板！\n${url}`)
    console.log('✅ 链接已复制:', url)
    
  } catch (error) {
    console.error('复制链接失败:', error)
    // 降级方案：使用传统方法
    try {
      const textArea = document.createElement('textarea')
      textArea.value = window.location.href
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      alert(`链接已复制到剪贴板！\n${window.location.href}`)
    } catch (fallbackError) {
      console.error('降级复制也失败:', fallbackError)
      alert('复制失败，请手动复制链接')
    }
  } finally {
    isGeneratingImage.value = false
  }
}

const fetchFavoriteStatus = async () => {
  if (!userAuth.isAuthenticated()) {
    isFavorited.value = false
    console.log('⚠️ 未登录，收藏状态为 false')
    return
  }
  
  const wikiNumericId = Number(locationId)
  const buildingId = buildingIdRef.value
  
  console.log('🔍 查询收藏状态 - wikiId:', wikiNumericId, 'buildingId:', buildingId)
  
  try {
    const response = await getFavoriteStatus({
      wikiId: wikiNumericId,
      buildingId: buildingId ?? undefined,
    })
    
    console.log('📥 收藏状态 API 响应:', response)
    
    const newStatus = !!response?.favorited
    console.log('🎯 更新收藏状态: 旧值=', isFavorited.value, '新值=', newStatus)
    
    isFavorited.value = newStatus
    
    console.log('✅ 收藏状态已更新为:', isFavorited.value)
  } catch (error) {
    console.error('❌ 获取收藏状态失败:', error)
    isFavorited.value = false
  }
}

const recordBrowsingHistory = async () => {
  if (!userAuth.isAuthenticated() || !wikiData.value || !buildingIdRef.value) {
    return
  }

  try {
    await addHistoryApi({
      buildingId: buildingIdRef.value,
      wikiId: Number(locationId),
      name: wikiData.value.name,
      imageUrl: wikiData.value.mainImage,
      address: wikiData.value.address,
    })
  } catch (error) {
    console.error('记录浏览历史失败:', error)
  }
}

// 处理收藏
const handleFavorite = async () => {
  // 防止重复点击
  if (isSubmittingFavorite.value) {
    console.log('正在提交中，忽略重复点击')
    return
  }

  if (!userAuth.isAuthenticated()) {
    alert('请先登录后再收藏地点。')
    router.push({ name: 'Login' })
    return
  }

  // Building ID = Wiki ID
  const buildingId = buildingIdRef.value
  const wikiId = Number(locationId)
  
  console.log('收藏操作 - buildingId:', buildingId, 'wikiId:', wikiId, 'current:', isFavorited.value)
  
  if (!buildingId) {
    alert('当前地点缺少建筑标识，无法收藏。')
    return
  }

  isSubmittingFavorite.value = true
  const action = isFavorited.value ? 'removed' : 'added'

  try {
    if (isFavorited.value) {
      console.log('取消收藏...')
      await removeFavoriteApi({ buildingId, wikiId })
      console.log('取消收藏成功')
    } else {
      console.log('添加收藏...')
      await addFavoriteApi({ buildingId, wikiId })
      console.log('添加收藏成功')
    }
    
    console.log('收藏操作成功，重新获取状态...')
    // 操作成功后，重新获取收藏状态确保同步
    await fetchFavoriteStatus()
    
    // 触发全局事件，通知其他页面（如地图）更新收藏状态
    window.dispatchEvent(new CustomEvent('favoriteChanged', { 
      detail: { buildingId, wikiId, action }
    }))
    
    // 显示成功提示
    const message = action === 'added' ? '收藏成功！' : '已取消收藏'
    // 可以用一个简单的提示替代 alert
    setTimeout(() => {
      // 这里可以显示一个 toast 提示，暂时先用 alert
      console.log('✅', message, 'isFavorited:', isFavorited.value)
    }, 100)
  } catch (error: any) {
    console.error('更新收藏状态失败:', error)
    alert(error?.message || '操作失败，请稍后重试')
  } finally {
    isSubmittingFavorite.value = false
  }
}

// 加载评论列表
const loadComments = async (page = 1) => {
  commentsLoading.value = true
  commentsPage.value = page

  try {
    console.log('开始加载评论列表，locationId:', locationId, 'page:', page, 'tags:', selectedTags.value)
    
    // TODO: 后端支持多标签筛选后，传递 selectedTags.value 参数
    // 目前先在前端进行筛选
    let data = await getLocationComments(locationId, page, commentsPageSize.value)
    console.log('评论列表加载成功:', data)
    
    // 过滤掉 blob URL，只保留真实的图片URL
    if (data.items && data.items.length > 0) {
      // 获取当前用户信息，用于填充缺失的头像
      const currentUser = userAuth.getUser()
      const currentUserId = currentUser?.id || currentUser?.user_id
      
      data.items.forEach((comment) => {
        if (comment.images && comment.images.length > 0) {
          // 过滤掉 blob: 开头的 URL
          comment.images = comment.images.filter((url: string) => {
            const isBlob = url.startsWith('blob:')
            if (isBlob) {
              console.warn('过滤掉 blob URL:', url)
            }
            return !isBlob
          })
        }
        
        // 修复头像 URL
        if (comment.userAvatar) {
          comment.userAvatar = fixAvatarUrl(comment.userAvatar)
        } else if (comment.userId === currentUserId) {
          // 如果是当前用户的评论，使用当前用户的头像
          comment.userAvatar = currentUser?.avatar || '/avatar.jpg'
        }
        
        // 修复回复的头像 URL
        if ((comment as any).replies && Array.isArray((comment as any).replies)) {
          (comment as any).replies.forEach((reply: any) => {
            if (reply.userAvatar) {
              reply.userAvatar = fixAvatarUrl(reply.userAvatar)
            } else if (reply.userId === currentUserId) {
              // 如果是当前用户的回复，使用当前用户的头像
              reply.userAvatar = currentUser?.avatar || '/avatar.jpg'
            }
          })
        }
        
        // 初始化 isLiked 状态
        // 优先从 localStorage 读取，如果没有则使用后端返回的 liked 字段
        const likedComments = JSON.parse(localStorage.getItem('likedComments') || '{}')
        ;(comment as any).isLiked = likedComments[comment.id] !== undefined 
          ? likedComments[comment.id] 
          : ((comment as any).liked || false)
      })
    }
    
    // 前端多标签筛选：如果有选中的标签，只显示包含至少一个选中标签的评论
    if (selectedTags.value.length > 0 && data.items) {
      const filteredItems = data.items.filter((comment: any) => {
        // 检查评论是否包含任意一个选中的标签
        return selectedTags.value.some(tag => comment.tags?.includes(tag))
      })
      
      data = {
        ...data,
        items: filteredItems,
        total: filteredItems.length,
        totalPages: Math.ceil(filteredItems.length / commentsPageSize.value)
      }
      
      console.log(`筛选后的评论数量: ${filteredItems.length}/${data.items.length}`)
    }
    
    commentsData.value = data
  } catch (err: any) {
    console.error('获取评论列表失败:', err)
    // 如果 API 失败，使用空数据
    commentsData.value = {
      items: [],
      total: 0,
      page: 1,
      pageSize: commentsPageSize.value,
      totalPages: 0,
    }
  } finally {
    commentsLoading.value = false
  }
}

// 处理评论提交成功
const handleCommentSubmitted = () => {
  // 刷新评论列表（重新加载第一页）
  loadComments(1)
  // 刷新热门标签
  loadPopularTags()
  // 刷新 Wiki 数据（包括评分星级）
  fetchWikiData()
}

// 加载热门标签
const loadPopularTags = async () => {
  try {
    const response = await fetch(`/api/location/${locationId}/tags/popular`)
    if (response.ok) {
      const data = await response.json()
      popularTags.value = data.tags || []
    }
  } catch (error) {
    console.error('加载热门标签失败:', error)
  }
}

// 切换标签筛选（支持多选）
const toggleTagFilter = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    // 已选中，移除
    selectedTags.value.splice(index, 1)
  } else {
    // 未选中，添加
    selectedTags.value.push(tag)
  }
  // 重新加载评论（带标签筛选）
  loadComments(1)
}

// 清除所有标签筛选
const clearTagFilter = () => {
  selectedTags.value = []
  loadComments(1)
}

// 处理分页变化
const handlePageChange = (page: number) => {
  loadComments(page)
}

// 滚动到指定评论并高亮
const scrollToComment = async (reviewId: string | number) => {
  console.log(`🔍 开始滚动到评论 ID: ${reviewId}`)
  
  // 等待 DOM 更新
  await nextTick()
  
  // 增加延迟时间，确保评论列表完全渲染
  setTimeout(() => {
    console.log(`🔍 尝试查找评论元素: comment-${reviewId}`)
    const commentElement = document.getElementById(`comment-${reviewId}`)
    
    if (commentElement) {
      console.log(`✅ 找到评论元素，开始滚动`)
      
      // 滚动到评论位置（居中显示）
      commentElement.scrollIntoView({ 
        behavior: 'smooth',
        block: 'center'
      })
      
      // 添加高亮效果
      commentElement.classList.add('highlight-comment')
      
      // 2秒后移除高亮
      setTimeout(() => {
        commentElement.classList.remove('highlight-comment')
      }, 2000)
      
      console.log(`✅ 已滚动到评论 ID: ${reviewId}`)
    } else {
      console.warn(`⚠️ 未找到评论 ID: ${reviewId}`)
      console.log(`🔍 当前页面所有评论 ID:`, 
        Array.from(document.querySelectorAll('[id^="comment-"]')).map(el => el.id))
    }
  }, 800)
}

// 处理标签点击
const handleTagClick = (tag: any) => {
  console.log('标签点击:', tag)
  // 可以根据需要实现标签点击的逻辑，比如跳转到搜索结果页面
}

// 监听来自其他页面的收藏变化事件
const handleFavoriteChanged = (event: CustomEvent) => {
  console.log('Wiki 页面收到收藏变化事件:', event.detail)
  const { buildingId: changedBuildingId } = event.detail
  // 如果变化的是当前页面的建筑，刷新收藏状态
  if (changedBuildingId === buildingIdRef.value) {
    fetchFavoriteStatus()
  }
}

watch(
  () => [wikiData.value, currentLang.value],
  () => {
    missingI18nFields.value = []
    // 触发计算，顺便记录缺失字段
    void localizedName.value
    void localizedAddress.value
    void localizedRichContent.value
    void localizedStructuredInfo.value
    void localizedTags.value
  },
)

onMounted(() => {
  // 获取用户 token
  userToken.value = userAuth.getToken()
  currentLang.value = 'zh'

  // 获取 Wiki 数据
  fetchWikiData()

  // 获取评论列表
  loadComments().then(() => {
    // 检查 URL 中是否有 reviewId 参数
    const reviewIdParam = route.query.reviewId
    if (reviewIdParam) {
      // 处理数组情况，只取第一个值
      const reviewId = Array.isArray(reviewIdParam) ? reviewIdParam[0] : reviewIdParam
      if (reviewId) {
        console.log(`🔍 检测到 reviewId 参数: ${reviewId}，准备滚动到评论`)
        scrollToComment(reviewId)
      }
    }
  })
  
  // 加载热门标签
  loadPopularTags()
  
  // 监听收藏变化事件
  window.addEventListener('favoriteChanged', handleFavoriteChanged as EventListener)
})

onUnmounted(() => {
  // 清理事件监听
  window.removeEventListener('favoriteChanged', handleFavoriteChanged as EventListener)
})
</script>

<style scoped>
/* Wiki 内容样式 */
.wiki-content :deep(h2) {
  font-size: 1.5rem;
  line-height: 2rem;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-weight: 700;
  color: #252b46;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.wiki-content :deep(h3) {
  font-size: 1.25rem;
  line-height: 1.75rem;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-weight: 600;
  color: #111827;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.wiki-content :deep(p) {
  color: #374151;
  line-height: 1.625;
  margin-bottom: 1rem;
}

.wiki-content :deep(ul),
.wiki-content :deep(ol) {
  margin-bottom: 1rem;
  list-style-position: inside;
  padding-left: 1.5rem;
}

.wiki-content :deep(ul) {
  list-style-type: disc;
}

.wiki-content :deep(ol) {
  list-style-type: decimal;
}

.wiki-content :deep(li) {
  color: #374151;
  margin-bottom: 0.5rem;
}

.wiki-content :deep(strong) {
  font-weight: 600;
  color: #111827;
}

.wiki-content :deep(a) {
  color: #5368df;
  text-decoration: none;
  transition: text-decoration 0.2s;
}

.wiki-content :deep(a:hover) {
  text-decoration: underline;
}

.wiki-content :deep(img) {
  border-radius: 0.5rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
  max-width: 100%;
  height: auto;
}
</style>
