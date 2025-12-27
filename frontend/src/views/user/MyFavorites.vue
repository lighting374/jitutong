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
      <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">我的收藏地点</h1>
      <p class="text-gray-600">管理您收藏的所有地点</p>
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
        <p class="text-gray-600">正在加载收藏列表...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="favorites.length === 0" class="card text-center py-16">
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
          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
        />
      </svg>
      <p class="text-gray-500 text-lg">你还没有收藏任何地点</p>
      <p class="text-gray-400 text-sm mt-2">发现喜欢的地点就收藏起来吧！</p>
    </div>

    <!-- Favorites Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="fav in favorites"
        :key="fav.buildingId"
        class="card group hover:shadow-medium transition-all"
      >
        <div class="relative mb-4 overflow-hidden rounded-lg">
          <img
            :src="fav.imageUrl"
            alt="地点图片"
            class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
          />
          <div class="absolute top-3 right-3">
            <button
              @click="handleUnfavorite(fav.buildingId)"
              class="w-10 h-10 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-md transition-all"
              title="取消收藏"
            >
              <svg class="w-5 h-5 text-secondary" fill="currentColor" viewBox="0 0 24 24">
                <path
                  d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                />
              </svg>
            </button>
          </div>
        </div>

        <h3
          class="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary transition-colors"
        >
          {{ fav.name }}
        </h3>

        <p class="text-gray-600 mb-4 line-clamp-2">{{ fav.description }}</p>

        <div class="flex gap-3">
          <router-link
            :to="`/location/${fav.wikiId}`"
            class="inline-flex items-center text-primary hover:text-primary/80 font-medium text-sm transition-colors"
          >
            查看详情
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </router-link>
          <router-link
            to="/map"
            class="inline-flex items-center text-gray-600 hover:text-primary font-medium text-sm transition-colors"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            地图
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFavorites, removeFavorite } from '../../api/user'
import { buildingsInfo } from '../../config/buildingMapping'
import { API_CONFIG } from '../../config/apiConfig'

const BACKEND_HOST = API_CONFIG.BACKEND_URL

const isLoading = ref(true)
const errorMessage = ref('')

type FavoriteItem = {
  imageUrl: string
  buildingId: string | number
  wikiId: string | number
  name: string
  description: string
  type?: string
}

const favorites = ref<FavoriteItem[]>([])

const resolveImageUrl = (url: string | undefined | null): string => {
  if (!url) return '/placeholder-location.png'

  // 如果已经是完整的 URL，直接返回
  if (/^https?:\/\//i.test(url)) {
    return url
  }

  // 处理 Windows 本地路径（如 F:\jitutong_wiki_backend\A楼.png）
  // 提取文件名（最后一个反斜杠或正斜杠后的部分）
  if (/^[A-Z]:\\/i.test(url) || url.includes('\\')) {
    const fileName = url.replace(/^.*[\\/]/, '')
    // 后端图片在 /uploads/ 目录下
    return `${BACKEND_HOST}/uploads/${fileName}`
  }

  // 处理相对路径
  if (url.startsWith('//')) {
    return `http:${url}`
  }
  if (url.startsWith('/')) {
    return `${BACKEND_HOST}${url}`
  }
  return `${BACKEND_HOST}/${url}`
}

const loadFavorites = async (): Promise<void> => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res: { items?: any[] } = await getFavorites()
    favorites.value =
      res.items?.map(
        (item): FavoriteItem => {
          // 兼容后端可能返回的字段名
          const buildingId = item.buildingId ?? item.building_id ?? item.id ?? ''
          const wikiId = item.wikiId ?? item.wiki_id ?? item.id ?? ''
          
          // 尝试从本地 buildingMapping 获取地点信息
          const localInfo = buildingsInfo[Number(buildingId)]
          
          return {
            ...item,
            // 后端返回的是 image 字段，转换为 imageUrl
            imageUrl: resolveImageUrl(item.image || item.imageUrl || localInfo?.imageUrl),
            buildingId: buildingId,
            wikiId: wikiId,
            // 优先使用本地映射的名称，避免显示"地点X"这样的占位符
            name: localInfo?.name || item.name || item.buildingName || '未命名地点',
            description: localInfo?.description || item.description || '',
            type: localInfo?.type || item.type || '',
          }
        },
      ) || []
  } catch (error: unknown) {
    console.error('获取收藏列表失败', error)
    errorMessage.value = error instanceof Error ? error.message : '加载收藏列表失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadFavorites()
})

const handleUnfavorite = async (buildingId: string | number | undefined) => {
  if (!buildingId) return
  if (!confirm('确定要取消收藏该地点吗？')) return
  
  // 找到对应的收藏项，获取 wikiId
  const favoriteItem = favorites.value.find((fav) => fav.buildingId === buildingId)
  if (!favoriteItem) {
    alert('未找到该收藏项')
    return
  }
  
  try {
    // removeFavorite API 需要同时传递 buildingId 和 wikiId
    await removeFavorite({ 
      buildingId: Number(buildingId), 
      wikiId: Number(favoriteItem.wikiId) 
    })
    favorites.value = favorites.value.filter((fav) => fav.buildingId !== buildingId)
  } catch (error: unknown) {
    console.error('取消收藏失败', error)
    alert(error instanceof Error ? error.message : '取消收藏失败，请稍后重试')
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}
</style>
