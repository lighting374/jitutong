<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">📍 我的收藏路线</h1>
            <p class="text-sm text-gray-500 mt-1">管理你收藏的常用路线</p>
          </div>
          <router-link
            to="/map"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            返回地图
          </router-link>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-16">
        <div class="text-center">
          <div class="inline-block h-12 w-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mb-3"></div>
          <p class="text-gray-500">加载中...</p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="card border border-red-100 bg-red-50 text-red-600">
        {{ error }}
        <button @click="loadRoutes" class="ml-2 text-primary hover:underline">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="routes.length === 0" class="card text-center py-16">
        <div class="text-6xl mb-4">🗺️</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">还没有收藏路线</h3>
        <p class="text-gray-500 mb-6">在地图页面规划路线后，点击"收藏路线"即可保存</p>
        <router-link
          to="/map"
          class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          前往地图
        </router-link>
      </div>

      <!-- 路线列表 -->
      <div v-else>
        <div class="mb-4 text-sm text-gray-500">
          共 {{ routes.length }} 条收藏路线
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="route in routes"
            :key="route.id"
            class="card hover:shadow-lg transition-all group"
          >
            <!-- 路线信息 -->
            <div class="mb-4">
              <div class="flex items-start justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900 flex-1">
                  {{ route.name || `${route.startName} → ${route.endName}` }}
                </h3>
                <button
                  @click="deleteRoute(route.id)"
                  class="text-gray-400 hover:text-red-500 transition-colors"
                  title="删除路线"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              
              <div class="text-sm text-gray-600 space-y-1">
                <div class="flex items-center">
                  <span class="text-primary mr-2">📍</span>
                  <span>起点：{{ route.startName }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-primary mr-2">🎯</span>
                  <span>终点：{{ route.endName }}</span>
                </div>
              </div>
            </div>

            <!-- 路线详情 -->
            <div class="flex items-center gap-4 text-sm text-gray-500 mb-4 pb-4 border-b border-gray-100">
              <div class="flex items-center">
                <span class="mr-1">📍</span>
                {{ route.distance }}
              </div>
              <div class="flex items-center">
                <span class="mr-1">🚶</span>
                {{ route.walkTime }}
              </div>
              <div class="flex items-center">
                <span class="mr-1">🚴</span>
                {{ route.bikeTime }}
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <button
                @click="loadRoute(route)"
                class="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                加载路线
              </button>
              <button
                v-if="route.name"
                @click="editRouteName(route)"
                class="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                title="编辑名称"
              >
                ✏️
              </button>
            </div>

            <!-- 创建时间 -->
            <div class="mt-3 text-xs text-gray-400">
              创建于 {{ formatDate(route.createdAt) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑名称对话框 -->
    <div v-if="showEditDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="closeEditDialog">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4" @click.stop>
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">编辑路线名称</h3>
          <input
            v-model="editingName"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            placeholder="输入路线名称"
            maxlength="50"
            @keypress.enter="saveRouteName"
          />
          <p class="text-xs text-gray-400 mt-2">{{ editingName.length }}/50</p>
        </div>
        <div class="flex gap-2 px-6 pb-6">
          <button
            @click="closeEditDialog"
            class="flex-1 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="saveRouteName"
            class="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
            :disabled="!editingName.trim()"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Route {
  id: number
  name?: string
  startId: number | null
  endId: number | null
  startName: string
  endName: string
  startPosition: [number, number] | null
  endPosition: [number, number] | null
  distance: string
  walkTime: string
  bikeTime: string
  createdAt: string
}

const loading = ref(false)
const error = ref('')
const routes = ref<Route[]>([])

// 编辑对话框
const showEditDialog = ref(false)
const editingRoute = ref<Route | null>(null)
const editingName = ref('')

// 加载收藏路线
const loadRoutes = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('user_token')
    if (!token) {
      error.value = '请先登录'
      return
    }

    const response = await fetch('/api/routes', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('加载失败')
    }

    const data = await response.json()
    routes.value = data.routes || []
  } catch (err: any) {
    console.error('加载收藏路线失败:', err)
    error.value = err.message || '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 删除路线
const deleteRoute = async (routeId: number) => {
  if (!confirm('确定要删除这条路线吗？')) return

  try {
    const token = localStorage.getItem('token') || localStorage.getItem('user_token')
    const response = await fetch(`/api/routes/${routeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      routes.value = routes.value.filter(r => r.id !== routeId)
    } else {
      alert('删除失败')
    }
  } catch (error) {
    console.error('删除路线失败:', error)
    alert('删除失败')
  }
}

// 加载路线到地图
const loadRoute = (route: Route) => {
  // 将路线信息存储到 sessionStorage
  sessionStorage.setItem('loadRoute', JSON.stringify(route))
  // 跳转到地图页面
  router.push('/map')
}

// 编辑路线名称
const editRouteName = (route: Route) => {
  editingRoute.value = route
  editingName.value = route.name || `${route.startName} → ${route.endName}`
  showEditDialog.value = true
}

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditDialog.value = false
  editingRoute.value = null
  editingName.value = ''
}

// 保存路线名称
const saveRouteName = async () => {
  if (!editingRoute.value || !editingName.value.trim()) return

  try {
    const token = localStorage.getItem('token') || localStorage.getItem('user_token')
    const response = await fetch(`/api/routes/${editingRoute.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: editingName.value.trim()
      })
    })

    if (response.ok) {
      // 更新本地数据
      const route = routes.value.find(r => r.id === editingRoute.value!.id)
      if (route) {
        route.name = editingName.value.trim()
      }
      closeEditDialog()
    } else {
      alert('保存失败')
    }
  } catch (error) {
    console.error('保存路线名称失败:', error)
    alert('保存失败')
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  loadRoutes()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
