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
      <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">我的评论与评分</h1>
      <p class="text-gray-600">查看您发表的所有评论和评分</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"
        ></div>
        <p class="text-gray-600">正在加载评论...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="comments.length === 0" class="card text-center py-16">
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
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
      <p class="text-gray-500 text-lg">你还没有发表过任何评论</p>
      <p class="text-gray-400 text-sm mt-2">去探索并分享您的观点吧！</p>
    </div>

    <!-- Comments List -->
    <div v-else class="space-y-4">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="card hover:shadow-medium transition-shadow"
      >
        <!-- Comment Header -->
        <div class="flex justify-between items-start mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ comment.locationName }}</h3>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-500">{{ comment.createdAt }}</span>
            </div>
          </div>
        </div>

        <!-- Rating or Parent Comment Info -->
        <div v-if="comment.parentId" class="mb-3 p-3 bg-gray-50 rounded-lg border-l-4 border-primary">
          <div class="flex items-start space-x-2">
            <svg class="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
            <div class="flex-1">
              <p class="text-xs text-gray-500 mb-1">回复 @{{ comment.parentUserName || '某用户' }}</p>
              <p class="text-sm text-gray-700">{{ comment.parentComment || '原评论已被删除' }}</p>
            </div>
          </div>
        </div>
        <div v-else-if="comment.rating && comment.rating > 0" class="flex items-center mb-3">
          <span class="text-sm text-gray-600 mr-2">评分：</span>
          <div class="flex items-center">
            <svg
              v-for="i in 5"
              :key="i"
              class="w-5 h-5"
              :class="i <= comment.rating ? 'text-yellow-400' : 'text-gray-300'"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
            <span class="ml-2 text-sm font-medium text-gray-700">{{ comment.rating }}.0</span>
          </div>
        </div>

        <!-- Comment Text -->
          <p class="text-gray-700 leading-relaxed mb-4">{{ comment.comment }}</p>

        <!-- Actions -->
        <div class="flex justify-end">
          <router-link
            :to="`/location/${comment.locationId}`"
            class="inline-flex items-center text-primary hover:text-primary/80 font-medium text-sm transition-colors"
          >
            查看地点详情
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import userAuth from '../../services/userAuth'
import { getMyReviews } from '../../api/user'

const router = useRouter()

const isLoading = ref(true)
const comments = ref<
  Array<{
    id: string | number
    locationId: string | number
    locationName: string
    rating: number
    comment: string
    createdAt: string
    wikiId?: number
    parentId?: number | null
    parentUserName?: string
    parentComment?: string
  }>
>([])

const fetchMyComments = async () => {
  isLoading.value = true
  try {
    const res = await getMyReviews()
    comments.value =
      res?.items?.map((item) => ({
        id: item.id,
        locationId: item.wikiId || item.locationId,
        locationName: item.locationName,
        rating: item.rating || 0,
        comment: item.comment,
        createdAt: item.createdAt?.split('T')[0] || item.createdAt,
        wikiId: item.wikiId,
        parentId: item.parentId || null,
        parentUserName: item.parentUserName || '',
        parentComment: item.parentComment || '',
      })) || []
  } catch (error: any) {
    console.error('获取我的评论失败:', error)
    alert(error?.message || '加载评论失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (!userAuth.isAuthenticated()) {
    router.push({ name: 'Login' })
    return
  }
  await fetchMyComments()
})
</script>
