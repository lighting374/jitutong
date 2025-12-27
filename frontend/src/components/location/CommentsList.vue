<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-heading font-bold text-dark-blue">评论列表</h2>
      
      <!-- 排序选项 -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500">排序：</span>
        <div class="flex gap-1 bg-gray-100 rounded-lg p-1">
          <button
            @click="sortBy = 'latest'"
            :class="[
              'px-3 py-1.5 text-sm rounded-md transition-all',
              sortBy === 'latest' 
                ? 'bg-white text-primary font-semibold shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            🕒 最新
          </button>
          <button
            @click="sortBy = 'hot'"
            :class="[
              'px-3 py-1.5 text-sm rounded-md transition-all',
              sortBy === 'hot' 
                ? 'bg-white text-primary font-semibold shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            🔥 最热
          </button>
          <button
            @click="sortBy = 'rating'"
            :class="[
              'px-3 py-1.5 text-sm rounded-md transition-all',
              sortBy === 'rating' 
                ? 'bg-white text-primary font-semibold shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            ⭐ 最高分
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
        <p class="text-gray-600 text-sm">正在加载评论...</p>
      </div>
    </div>

    <!-- Comments List -->
    <div v-else-if="sortedComments.length > 0" class="space-y-6">
      <div
        v-for="comment in sortedComments"
        :key="comment.id"
        :id="`comment-${comment.id}`"
        class="border-b border-gray-100 last:border-0 pb-6 last:pb-0 transition-colors duration-300"
      >
        <div class="flex items-start space-x-4">
          <!-- User Avatar -->
          <img :src="comment.userAvatar || '/avatar.jpg'" :alt="comment.userName" class="w-12 h-12 rounded-full object-cover flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <!-- User Info & Rating -->
            <div class="flex items-center flex-wrap gap-2 mb-2">
              <span class="font-semibold text-gray-900">{{ comment.userName }}</span>
              <div class="flex items-center">
                <div class="flex mr-2">
                  <svg
                    v-for="i in 5"
                    :key="i"
                    class="w-4 h-4"
                    :class="i <= comment.rating ? 'text-yellow-400' : 'text-gray-300'"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    />
                  </svg>
                </div>
                <span class="text-sm text-gray-500">{{ formatDate(comment.createdAt) }}</span>
              </div>
            </div>

            <!-- Comment Content -->
            <p class="text-gray-700 leading-relaxed mb-3 whitespace-pre-wrap">
              {{ comment.comment }}
            </p>

            <!-- Images Grid -->
            <div v-if="comment.images && comment.images.length > 0" class="grid grid-cols-3 gap-2 mb-3">
              <div
                v-for="(image, idx) in comment.images"
                :key="idx"
                @click="openImagePreview(image, comment.images || [])"
                class="relative aspect-square rounded-lg overflow-hidden cursor-pointer group"
              >
                <img
                  :src="image"
                  :alt="`评论图片 ${idx + 1}`"
                  @error="handleImageError($event, image)"
                  class="w-full h-full object-cover transition-transform group-hover:scale-105"
                />
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors"></div>
              </div>
            </div>

            <!-- 标签 -->
            <div v-if="comment.tags && comment.tags.length > 0" class="flex flex-wrap gap-2 mb-3">
              <span
                v-for="(tag, idx) in comment.tags"
                :key="idx"
                class="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full"
              >
                # {{ tag }}
              </span>
            </div>

            <!-- Actions -->
            <div class="flex items-center space-x-4 text-sm">
              <!-- 点赞按钮 -->
              <button 
                v-if="typeof comment.likes === 'number'"
                @click="handleLike(Number(comment.id))"
                class="flex items-center transition-colors cursor-pointer"
                :class="(comment as any).isLiked ? 'text-red-500 hover:text-red-600' : 'text-gray-500 hover:text-red-500'"
                :disabled="likingCommentId === Number(comment.id)"
              >
                <svg 
                  class="w-5 h-5 mr-1" 
                  :class="(comment as any).isLiked ? 'fill-current' : 'fill-none'"
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                  />
                </svg>
                <span :class="(comment as any).isLiked ? 'font-semibold' : ''">
                  {{ comment.likes }}
                </span>
              </button>
              
              <!-- 回复按钮 -->
              <button 
                @click="toggleReply(Number(comment.id))"
                class="flex items-center text-gray-500 hover:text-primary transition-colors cursor-pointer"
              >
                <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                </svg>
                <span>回复</span>
                <span v-if="(comment as any).replyCount" class="ml-1">({{ (comment as any).replyCount }})</span>
              </button>
              
              <!-- 举报按钮 -->
              <button 
                @click="openReportModal(Number(comment.id))"
                class="flex items-center text-gray-500 hover:text-red-500 transition-colors cursor-pointer"
              >
                <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>举报</span>
              </button>
            </div>
            
            <!-- 回复输入框 -->
            <div v-if="replyingTo === Number(comment.id)" class="mt-4 pl-12">
              <div class="bg-gray-50 rounded-lg p-4">
                <textarea
                  v-model="replyContent"
                  placeholder="写下你的回复..."
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                ></textarea>
                <div class="flex justify-end space-x-2 mt-2">
                  <button
                    @click="cancelReply"
                    class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    @click="submitReply(Number(comment.id))"
                    :disabled="!replyContent.trim() || isSubmittingReply"
                    class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ isSubmittingReply ? '发送中...' : '发送回复' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 回复列表 -->
            <div v-if="(comment as any).replies && (comment as any).replies.length > 0" class="mt-4 pl-12 space-y-3">
              <div 
                v-for="reply in (comment as any).replies" 
                :key="reply.id"
                class="bg-gray-50 rounded-lg p-3"
              >
                <div class="flex items-start space-x-3">
                  <img :src="reply.userAvatar || '/avatar.jpg'" :alt="reply.userName" class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2 mb-1">
                      <span class="font-semibold text-sm text-gray-900">{{ reply.userName }}</span>
                      <span class="text-xs text-gray-500">{{ formatDate(reply.createdAt) }}</span>
                    </div>
                    <p class="text-sm text-gray-700">{{ reply.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="commentsData && commentsData.totalPages > 1" class="flex items-center justify-center space-x-2 pt-4 border-t border-gray-100">
        <button
          @click="commentsData && emitPageChange(commentsData.page - 1)"
          :disabled="!commentsData || commentsData.page <= 1"
          class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          上一页
        </button>
        <span class="px-4 py-2 text-gray-600">
          第 {{ commentsData?.page }} / {{ commentsData?.totalPages }} 页 （共 {{ commentsData?.total }} 条）
        </span>
        <button
          @click="commentsData && emitPageChange(commentsData.page + 1)"
          :disabled="!commentsData || commentsData.page >= commentsData.totalPages"
          class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
      <p class="text-gray-500 text-lg mb-2">暂无评论</p>
      <p class="text-gray-400 text-sm">快来抢沙发吧！</p>
    </div>

    <!-- Image Preview Modal -->
    <div
      v-if="imagePreview.show"
      @click="closeImagePreview"
      class="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
    >
      <button
        @click.stop="closeImagePreview"
        class="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors z-10"
      >
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <button
        v-if="imagePreview.images.length > 1 && imagePreview.currentIndex > 0"
        @click.stop="prevImage"
        class="absolute left-4 text-white hover:text-gray-300 transition-colors z-10"
      >
        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <img :src="imagePreview.currentImage" alt="预览图片" @click.stop class="max-w-full max-h-[90vh] object-contain" />

      <button
        v-if="imagePreview.images.length > 1 && imagePreview.currentIndex < imagePreview.images.length - 1"
        @click.stop="nextImage"
        class="absolute right-4 text-white hover:text-gray-300 transition-colors z-10"
      >
        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <div
        v-if="imagePreview.images.length > 1"
        class="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-white bg-black/50 px-4 py-2 rounded-lg text-sm"
      >
        {{ imagePreview.currentIndex + 1 }} / {{ imagePreview.images.length }}
      </div>
    </div>
    
    <!-- 举报弹窗 -->
    <div
      v-if="reportModal.show"
      @click="closeReportModal"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    >
      <div
        @click.stop
        class="bg-white rounded-lg max-w-md w-full p-6 shadow-xl"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">举报评论</h3>
          <button
            @click="closeReportModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- 举报类型选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">举报类型 *</label>
            <div class="space-y-2">
              <label
                v-for="type in reportTypes"
                :key="type.value"
                class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors"
                :class="reportModal.type === type.value ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-gray-300'"
              >
                <input
                  type="radio"
                  v-model="reportModal.type"
                  :value="type.value"
                  class="mr-3"
                />
                <div>
                  <div class="font-medium text-sm">{{ type.label }}</div>
                  <div class="text-xs text-gray-500">{{ type.description }}</div>
                </div>
              </label>
            </div>
          </div>
          
          <!-- 详细说明 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">详细说明（可选）</label>
            <textarea
              v-model="reportModal.description"
              placeholder="请描述您举报的具体原因..."
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            ></textarea>
          </div>
          
          <!-- 按钮 -->
          <div class="flex justify-end space-x-3">
            <button
              @click="closeReportModal"
              class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              取消
            </button>
            <button
              @click="submitReport"
              :disabled="!reportModal.type || isSubmittingReport"
              class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isSubmittingReport ? '提交中...' : '提交举报' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ReviewListResponse, ReviewComment } from '@/api/location'
import { fixAvatarUrl } from '@/config/apiConfig'

const props = defineProps<{
  commentsData: ReviewListResponse | null
  loading: boolean
}>()

// 排序状态
const sortBy = ref<'latest' | 'hot' | 'rating'>('latest')

// 排序后的评论列表
const sortedComments = computed(() => {
  if (!props.commentsData || !props.commentsData.items) {
    return []
  }
  
  const comments = [...props.commentsData.items]
  
  switch (sortBy.value) {
    case 'latest':
      // 按时间排序（最新在前）
      return comments.sort((a, b) => {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      })
    
    case 'hot':
      // 按点赞数排序（最热在前）
      return comments.sort((a, b) => {
        return (b.likes || 0) - (a.likes || 0)
      })
    
    case 'rating':
      // 按评分排序（最高分在前）
      return comments.sort((a, b) => {
        return b.rating - a.rating
      })
    
    default:
      return comments
  }
})

const emit = defineEmits<{
  (e: 'page-change', page: number): void
}>()

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

const likingCommentId = ref<number | null>(null)
const replyingTo = ref<number | null>(null)
const replyContent = ref('')
const isSubmittingReply = ref(false)

// 举报相关
const reportModal = ref<{
  show: boolean
  commentId: number | null
  type: string
  description: string
}>({
  show: false,
  commentId: null,
  type: '',
  description: ''
})

const isSubmittingReport = ref(false)

// 举报类型定义
const reportTypes = [
  { value: 'spam', label: '垃圾广告', description: '商业广告、恶意营销等' },
  { value: 'offensive', label: '不适内容', description: '辱骂、攻击、仇恨言论等' },
  { value: 'false_info', label: '虚假信息', description: '谣言、不实内容等' },
  { value: 'illegal', label: '违法内容', description: '涉及违法犯罪的内容' },
  { value: 'other', label: '其他问题', description: '其他需要处理的问题' }
]

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
      // 如果分钟数为负数，也显示“刚刚”
      if (minutes < 0) {
        return '刚刚'
      }
      return `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  }
  return date.toLocaleDateString('zh-CN')
}

const emitPageChange = (page: number) => {
  if (!props.commentsData) return
  if (page < 1 || page > props.commentsData.totalPages) return
  emit('page-change', page)
}

const openImagePreview = (image: string, images: string[]) => {
  const index = images.indexOf(image)
  imagePreview.value = {
    show: true,
    currentImage: image,
    images,
    currentIndex: index >= 0 ? index : 0,
  }
}

const closeImagePreview = () => {
  imagePreview.value.show = false
}

const prevImage = () => {
  if (imagePreview.value.currentIndex > 0) {
    imagePreview.value.currentIndex--
    const prevImg = imagePreview.value.images[imagePreview.value.currentIndex]
    if (prevImg) {
      imagePreview.value.currentImage = prevImg
    }
  }
}

const nextImage = () => {
  if (imagePreview.value.currentIndex < imagePreview.value.images.length - 1) {
    imagePreview.value.currentIndex++
    const nextImg = imagePreview.value.images[imagePreview.value.currentIndex]
    if (nextImg) {
      imagePreview.value.currentImage = nextImg
    }
  }
}

const handleImageError = (event: Event, imageUrl: string) => {
  const img = event.target as HTMLImageElement
  
  // 防止无限循环：如果已经是错误状态，不再处理
  if (img.dataset.errorHandled === 'true') {
    return
  }
  
  console.warn('图片加载失败:', imageUrl)
  
  // 标记已处理
  img.dataset.errorHandled = 'true'
  
  // 移除 error 事件监听，防止再次触发
  img.onerror = null
  
  // 隐藏图片，显示错误提示
  img.style.display = 'none'
  
  // 在父元素中显示错误提示
  const parent = img.parentElement
  if (parent && !parent.querySelector('.error-message')) {
    const errorDiv = document.createElement('div')
    errorDiv.className = 'error-message flex items-center justify-center h-full bg-gray-100 text-gray-500 text-sm'
    errorDiv.textContent = '图片加载失败'
    parent.appendChild(errorDiv)
  }
}

const handleLike = async (commentId: number) => {
  if (likingCommentId.value) return // 防止重复点击
  
  likingCommentId.value = commentId
  
  try {
    // 调用点赞 API
    const token = localStorage.getItem('user_token')
    if (!token) {
      alert('请先登录')
      return
    }
    
    const response = await fetch(`/api/reviews/${commentId}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('点赞失败')
    }
    
    const result = await response.json()
    
    console.log('点赞 API 响应:', result)
    
    // 更新本地评论数据
    if (props.commentsData && props.commentsData.items) {
      const comment = props.commentsData.items.find((c: ReviewComment) => c.id === commentId)
      if (comment) {
        // 使用后端返回的 likes 和 liked 字段
        comment.likes = result.likes
        ;(comment as any).isLiked = result.liked
        
        // 保存点赞状态到 localStorage
        const likedComments = JSON.parse(localStorage.getItem('likedComments') || '{}')
        likedComments[commentId] = result.liked
        localStorage.setItem('likedComments', JSON.stringify(likedComments))
      }
    }
  } catch (error) {
    console.error('点赞失败:', error)
    alert('点赞失败，请稍后重试')
  } finally {
    likingCommentId.value = null
  }
}

// 切换回复输入框
const toggleReply = (commentId: number) => {
  if (replyingTo.value === commentId) {
    replyingTo.value = null
    replyContent.value = ''
  } else {
    replyingTo.value = commentId
    replyContent.value = ''
  }
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

// 提交回复
const submitReply = async (commentId: number) => {
  if (!replyContent.value.trim()) return
  
  const token = localStorage.getItem('user_token')
  if (!token) {
    alert('请先登录')
    return
  }
  
  isSubmittingReply.value = true
  
  try {
    const response = await fetch(`/api/reviews/${commentId}/replies`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: replyContent.value.trim()
      })
    })
    
    if (!response.ok) {
      throw new Error('回复失败')
    }
    
    const result = await response.json()
    console.log('回复成功:', result)
    
    // 更新本地评论数据
    if (props.commentsData && props.commentsData.items) {
      const comment = props.commentsData.items.find((c: ReviewComment) => c.id === commentId)
      if (comment) {
        // 添加新回复到列表
        if (!(comment as any).replies) {
          ;(comment as any).replies = []
        }
        
        // 修复回复的头像 URL
        const reply = result.reply
        if (reply) {
          if (reply.userAvatar) {
            reply.userAvatar = fixAvatarUrl(reply.userAvatar)
          } else {
            // 如果没有头像，使用当前用户的头像
            const currentUser = JSON.parse(localStorage.getItem('user_info') || '{}')
            reply.userAvatar = currentUser.avatar || '/avatar.jpg'
          }
        }
        
        ;(comment as any).replies.push(reply)
        ;(comment as any).replyCount = ((comment as any).replyCount || 0) + 1
      }
    }
    
    // 清空输入框
    replyContent.value = ''
    replyingTo.value = null
    
  } catch (error) {
    console.error('回复失败:', error)
    alert('回复失败，请稍后重试')
  } finally {
    isSubmittingReply.value = false
  }
}

// 打开举报弹窗
const openReportModal = (commentId: number) => {
  reportModal.value = {
    show: true,
    commentId,
    type: '',
    description: ''
  }
}

// 关闭举报弹窗
const closeReportModal = () => {
  reportModal.value = {
    show: false,
    commentId: null,
    type: '',
    description: ''
  }
}

// 提交举报
const submitReport = async () => {
  if (!reportModal.value.type || !reportModal.value.commentId) return
  
  const token = localStorage.getItem('user_token')
  if (!token) {
    alert('请先登录')
    return
  }
  
  isSubmittingReport.value = true
  
  try {
    const response = await fetch(`/api/reviews/${reportModal.value.commentId}/report`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        type: reportModal.value.type,
        description: reportModal.value.description.trim()
      })
    })
    
    if (!response.ok) {
      throw new Error('举报失败')
    }
    
    const result = await response.json()
    console.log('举报成功:', result)
    
    alert('举报已提交，我们会尽快处理')
    closeReportModal()
    
  } catch (error) {
    console.error('举报失败:', error)
    alert('举报失败，请稍后重试')
  } finally {
    isSubmittingReport.value = false
  }
}
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

/* 评论高亮动画 */
@keyframes highlight-comment {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: #fef3c7; /* 黄色高亮 */
  }
}

.highlight-comment {
  animation: highlight-comment 2s ease-in-out;
  border-radius: 0.5rem;
}
</style>

