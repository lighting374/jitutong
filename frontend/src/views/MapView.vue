<template>
  <div class="map-page">
    <iframe ref="mapIframe" src="/campus-map.html" class="map-iframe" frameborder="0"></iframe>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { buildingToWikiMap, getBuildingIdFromWikiId } from '../config/buildingMapping'
import {
  addFavorite as addFavoriteApi,
  removeFavorite as removeFavoriteApi,
  getFavorites as getFavoritesApi,
} from '../api/user'
import userAuth from '../services/userAuth'

const router = useRouter()
const mapIframe = ref(null)

const postToIframe = (payload) => {
  if (mapIframe.value?.contentWindow) {
    mapIframe.value.contentWindow.postMessage(payload, '*')
  }
}

const fetchFavorites = async () => {
  if (!userAuth.isAuthenticated()) {
    postToIframe({ type: 'FAVORITES_DATA', favorites: [] })
    return
  }
  try {
    const res = await getFavoritesApi()
    const ids =
      res?.items?.map((item) => {
        const wikiId = item.wikiId
        if (wikiId) {
          return getBuildingIdFromWikiId(Number(wikiId))
        }
        return Number(item.buildingId)
      }) || []
    const buildingIds = ids.filter((id) => typeof id === 'number' && !Number.isNaN(id))
    postToIframe({
      type: 'FAVORITES_DATA',
      favorites: buildingIds,
    })
  } catch (error) {
    console.error('获取收藏失败:', error)
    postToIframe({ type: 'FAVORITES_DATA', favorites: [], error: error?.message })
  }
}

const handleToggleFavorite = async (buildingId) => {
  if (!userAuth.isAuthenticated()) {
    postToIframe({ type: 'FAVORITE_RESULT', success: false, message: '请先登录' })
    return
  }
  // 获取对应的 wikiId
  const wikiId = buildingToWikiMap[buildingId] ?? buildingId
  
  try {
    const res = await getFavoritesApi()
    const current = new Set(
      res?.items?.map((item) =>
        item.wikiId ? getBuildingIdFromWikiId(Number(item.wikiId)) : Number(item.buildingId),
      ) || [],
    )
    const isFavorited = current.has(buildingId)
    // 收藏 API 需要同时传递 buildingId 和 wikiId
    if (isFavorited) {
      await removeFavoriteApi({ buildingId, wikiId })
    } else {
      await addFavoriteApi({ buildingId, wikiId })
    }
    // 不需要调用 fetchFavorites()，通过 FAVORITE_RESULT 消息更新本地状态即可
    // await fetchFavorites() // 移除，避免 FAVORITES_DATA 覆盖本地状态
    postToIframe({
      type: 'FAVORITE_RESULT',
      success: true,
      buildingId,
      action: isFavorited ? 'removed' : 'added',
    })
  } catch (error) {
    console.error('更新收藏失败:', error)
    postToIframe({
      type: 'FAVORITE_RESULT',
      success: false,
      buildingId,
      message: error?.message || '收藏失败',
    })
  }
}

const handleMessage = (event) => {
  if (!event.data) return
  if (event.data.type === 'NAVIGATE_TO_LOCATION') {
    const locationId = event.data.locationId
    
    // Building ID = Wiki ID，直接跳转
    if (locationId) {
      router.push(`/location/${locationId}`)
    } else {
      console.warn('缺少 locationId')
    }
  } else if (event.data.type === 'REQUEST_FAVORITES') {
    fetchFavorites()
  } else if (event.data.type === 'TOGGLE_FAVORITE') {
    const buildingId = Number(event.data.buildingId)
    if (!Number.isNaN(buildingId)) {
      handleToggleFavorite(buildingId)
    }
  }
}

// 监听来自 Wiki 页面的收藏变化事件
const handleFavoriteChanged = (event) => {
  console.log('收到收藏变化事件:', event.detail)
  // 刷新地图的收藏数据
  fetchFavorites()
}

onMounted(() => {
  window.addEventListener('message', handleMessage)
  window.addEventListener('favoriteChanged', handleFavoriteChanged)
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
  window.removeEventListener('favoriteChanged', handleFavoriteChanged)
})
</script>

<style scoped>
.map-page {
  height: calc(100vh - 73px);
  width: 100%;
  overflow: hidden;
}

.map-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
