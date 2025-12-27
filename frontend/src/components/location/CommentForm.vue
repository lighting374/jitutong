<template>
  <div class="card">
    <template v-if="userToken">
      <h2 class="text-2xl font-heading font-bold text-dark-blue mb-6">发表评论</h2>

      <form @submit.prevent="handleSubmitComment" class="space-y-4">
        <!-- Rating Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            评分 <span class="text-red-500">*</span>
          </label>
          <div class="flex items-center space-x-2">
            <button
              v-for="i in 5"
              :key="i"
              type="button"
              @click="commentForm.rating = i"
              class="transition-transform hover:scale-110"
            >
              <svg
                class="w-8 h-8"
                :class="i <= commentForm.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                />
              </svg>
            </button>
            <span class="text-sm text-gray-500 ml-2">
              {{ commentForm.rating > 0 ? `${commentForm.rating}星` : '请选择评分' }}
            </span>
          </div>
          <p v-if="commentErrors.rating" class="mt-1 text-sm text-red-600">
            {{ commentErrors.rating }}
          </p>
        </div>

        <!-- Comment Text -->
        <div>
          <label for="comment-text" class="block text-sm font-medium text-gray-700 mb-2">
            评论内容 <span class="text-red-500">*</span>
          </label>
          <textarea
            id="comment-text"
            v-model="commentForm.comment"
            rows="4"
            placeholder="分享你的体验和看法..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            :class="{ 'border-red-500': commentErrors.comment }"
          ></textarea>
          <p v-if="commentErrors.comment" class="mt-1 text-sm text-red-600">
            {{ commentErrors.comment }}
          </p>
        </div>

        <!-- Image Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"> 上传图片（最多9张） </label>
          <div class="flex items-center space-x-4">
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              multiple
              @change="handleImageSelect"
              class="hidden"
            />
            <button
              type="button"
              @click="fileInputRef?.click()"
              :disabled="commentForm.images.length >= 9 || isUploading"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {{ isUploading ? '上传中...' : '选择图片' }}
            </button>
            <span class="text-sm text-gray-500">
              已选择 {{ commentForm.images.length }} / 9 张
            </span>
          </div>

          <!-- Image Preview Grid -->
          <div v-if="commentForm.images.length > 0" class="mt-4 grid grid-cols-3 gap-4">
            <div
              v-for="(image, index) in commentForm.images"
              :key="index"
              class="relative group aspect-square rounded-lg overflow-hidden border border-gray-200"
            >
              <img
                :src="image.url"
                :alt="`预览图片 ${index + 1}`"
                class="w-full h-full object-cover"
              />
              <!-- Upload Status Overlay -->
              <div
                v-if="image.status === 'uploading'"
                class="absolute inset-0 bg-black/50 flex items-center justify-center"
              >
                <div class="text-center text-white">
                  <div
                    class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-white mb-2"
                  ></div>
                  <p class="text-xs">上传中...</p>
                </div>
              </div>
              <div
                v-else-if="image.status === 'error'"
                class="absolute inset-0 bg-red-500/80 flex items-center justify-center"
              >
                <div class="text-center text-white">
                  <svg
                    class="w-6 h-6 mx-auto mb-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  <p class="text-xs">上传失败</p>
                </div>
              </div>
              <!-- Delete Button -->
              <button
                type="button"
                @click="removeImage(index)"
                class="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 标签选择 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            添加标签（可选）
          </label>
          
          <!-- 预设标签 -->
          <div class="mb-3">
            <p class="text-xs text-gray-500 mb-2">预设标签：</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in presetTags"
                :key="tag"
                type="button"
                @click="toggleTag(tag)"
                class="px-3 py-1.5 rounded-full text-sm transition-all"
                :class="commentForm.tags.includes(tag)
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
              >
                {{ tag }}
              </button>
            </div>
          </div>
          
          <!-- 自定义标签 -->
          <div>
            <div class="flex items-center space-x-2">
              <input
                v-model="customTagInput"
                type="text"
                placeholder="输入自定义标签"
                maxlength="10"
                @keypress.enter.prevent="addCustomTag"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <button
                type="button"
                @click="addCustomTag"
                :disabled="!customTagInput.trim()"
                class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                添加
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-1">按 Enter 键快速添加，最多10个字</p>
          </div>
          
          <!-- 已选标签 -->
          <div v-if="commentForm.tags.length > 0" class="mt-3">
            <p class="text-xs text-gray-500 mb-2">已选标签：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(tag, index) in commentForm.tags"
                :key="index"
                class="inline-flex items-center px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm"
              >
                {{ tag }}
                <button
                  type="button"
                  @click="removeTag(index)"
                  class="ml-2 hover:text-red-500 transition-colors"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center justify-end space-x-4">
          <button
            type="button"
            @click="resetCommentForm"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            清空
          </button>
          <button
            type="submit"
            :disabled="isSubmittingComment"
            class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmittingComment ? '发表中...' : '发表评论' }}
          </button>
        </div>
      </form>
    </template>

    <template v-else>
      <div
        class="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-xl p-4"
      >
        <div>
          <p class="text-gray-700 font-medium mb-1">想要发表评论？</p>
          <p class="text-sm text-gray-600">请先登录以分享您的体验和看法</p>
        </div>
        <button
          @click="goLogin"
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        >
          立即登录
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { submitReview, type SubmitReviewData } from '../../api/location'

const props = defineProps<{
  locationId: string | number
  userToken: string | null
}>()

const emit = defineEmits<{
  (e: 'submitted'): void
}>()

const router = useRouter()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isSubmittingComment = ref(false)
const isUploading = ref(false)
const commentForm = ref<{
  rating: number
  comment: string
  images: Array<{ url: string; file?: File; status?: 'uploading' | 'success' | 'error' }>
  tags: string[]
}>({
  rating: 0,
  comment: '',
  images: [],
  tags: [],
})

// 标签相关
const customTagInput = ref('')
const presetTags = [
  '安静',
  '人少',
  '设施新',
  '服务好',
  '环境好',
  '交通便利',
  '有WiFi',
  '有空调',
  '适合学习',
  '适合聚会',
  '价格实惠',
  '味道好',
]

const commentErrors = ref<{
  rating?: string
  comment?: string
}>({})

const handleImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (!files || files.length === 0) return

  const remainingSlots = 9 - commentForm.value.images.length
  if (remainingSlots <= 0) {
    alert('最多只能上传9张图片')
    return
  }

  const filesToProcess = Array.from(files).slice(0, remainingSlots)

  filesToProcess.forEach((file) => {
    if (!file.type.startsWith('image/')) {
      alert(`${file.name} 不是有效的图片文件`)
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      alert(`${file.name} 文件大小超过5MB限制`)
      return
    }
    const previewUrl = URL.createObjectURL(file)
    commentForm.value.images.push({
      url: previewUrl,
      file,
      status: 'success',
    })
  })

  if (target) {
    target.value = ''
  }
}

const removeImage = (index: number) => {
  const image = commentForm.value.images[index]
  if (!image) return
  if (image.url.startsWith('blob:')) {
    URL.revokeObjectURL(image.url)
  }
  commentForm.value.images.splice(index, 1)
}

const validateCommentForm = (): boolean => {
  commentErrors.value = {}

  if (commentForm.value.rating === 0) {
    commentErrors.value.rating = '请选择评分'
  }

  const hasComment = commentForm.value.comment.trim().length > 0
  const hasImages = commentForm.value.images.length > 0

  if (!hasComment && !hasImages) {
    commentErrors.value.comment = '评论内容或图片至少需要填写一项'
  }

  return Object.keys(commentErrors.value).length === 0
}

// 切换预设标签
const toggleTag = (tag: string) => {
  const index = commentForm.value.tags.indexOf(tag)
  if (index > -1) {
    commentForm.value.tags.splice(index, 1)
  } else {
    if (commentForm.value.tags.length >= 10) {
      alert('最多只能选择10个标签')
      return
    }
    commentForm.value.tags.push(tag)
  }
}

// 添加自定义标签
const addCustomTag = () => {
  const tag = customTagInput.value.trim()
  if (!tag) return
  
  if (commentForm.value.tags.length >= 10) {
    alert('最多只能选择10个标签')
    return
  }
  
  if (commentForm.value.tags.includes(tag)) {
    alert('该标签已存在')
    return
  }
  
  commentForm.value.tags.push(tag)
  customTagInput.value = ''
}

// 移除标签
const removeTag = (index: number) => {
  commentForm.value.tags.splice(index, 1)
}

const resetCommentForm = () => {
  commentForm.value.images.forEach((image) => {
    if (image.url.startsWith('blob:')) {
      URL.revokeObjectURL(image.url)
    }
  })

  commentForm.value = {
    rating: 0,
    comment: '',
    images: [],
    tags: [],
  }
  customTagInput.value = ''
  commentErrors.value = {}
}

const handleSubmitComment = async () => {
  if (!validateCommentForm()) return

  if (!props.userToken) {
    alert('请先登录')
    router.push('/user/login')
    return
  }

  isSubmittingComment.value = true

  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const userId = userInfo.id || userInfo.userId || '1'

    // 收集 File 对象（而不是 URL）
    const imageFiles: File[] = []
    if (commentForm.value.images.length > 0) {
      for (const image of commentForm.value.images) {
        if (image.file) {
          imageFiles.push(image.file)
        }
      }
    }

    const reviewData: SubmitReviewData = {
      locationId: Number(props.locationId),
      rating: commentForm.value.rating,
      comment: commentForm.value.comment.trim(),
      images: imageFiles.length > 0 ? imageFiles : undefined,
      tags: commentForm.value.tags.length > 0 ? commentForm.value.tags : undefined,
    }

    await submitReview(reviewData)
    resetCommentForm()
    emit('submitted')
    alert('评论发表成功！')
  } catch (error: any) {
    console.error('提交评论失败:', error)
    alert(error.message || '评论发表失败，请稍后重试')
  } finally {
    isSubmittingComment.value = false
  }
}

const goLogin = () => {
  router.push('/user/login')
}

onBeforeUnmount(() => {
  commentForm.value.images.forEach((image) => {
    if (image.url.startsWith('blob:')) {
      URL.revokeObjectURL(image.url)
    }
  })
})
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}
</style>
