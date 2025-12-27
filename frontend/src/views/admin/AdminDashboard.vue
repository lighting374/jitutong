<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import adminApi from '../../api/admin'
import auth from '../../services/auth'
import { useRouter } from 'vue-router'

// Chart.js 集成
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js'
Chart.register(DoughnutController, ArcElement, Tooltip, Legend)

const router = useRouter()
const info = ref<any>(null)
const stats = ref<any>(null)
const loading = ref(false)
const error = ref('')
const lastRefresh = ref<string | null>(null)

// Chart refs
const chartRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

// 自动刷新定时器 id
let refreshTimer: number | null = null

function formatDate(val: string | undefined) {
  if (!val) return '-'
  try {
    return new Date(val).toLocaleString()
  } catch {
    return String(val)
  }
}

function totalPercent(s: any) {
  if (!s || !s.totalUsers) return 0
  const p = Math.round((Number(s.activeUsers || 0) / Number(s.totalUsers || 1)) * 100)
  return p
}

function getDisplayName(info: any) {
  if (!info) return '管理员'
  // 优先使用 nickname（从 users 表关联查询）
  if (info.nickname) return info.nickname
  // 其次使用 displayName（如果后端添加了这个字段）
  if (info.displayName) return info.displayName
  // 如果有name字段，使用name
  if (info.name) return info.name
  // 根据角色显示友好名称
  if (info.role === 'admin') return '系统管理员'
  if (info.role === 'wiki_admin') return 'Wiki管理员'
  return '管理员'
}

async function fetchData() {
  loading.value = true
  try {
    // 若未认证或 token 过期，跳转登录
    if (!auth.isAuthenticated() || (auth as any).isTokenExpired && (auth as any).isTokenExpired()) {
      auth.logout()
      router.push('/admin/login')
      return
    }

    info.value = await adminApi.getAdminInfo()
    stats.value = await adminApi.getStats()
    console.log('📊 Stats 数据:', JSON.stringify(stats.value, null, 2))
    lastRefresh.value = new Date().toISOString()
    error.value = ''
  } catch (e: any) {
    error.value = e.message || '加载失败'
    // 若 401/403，强制登出
    const msg = (e && (e.message || e.toString())).toLowerCase()
    if (msg.includes('401') || msg.includes('403')) {
      auth.logout()
      router.push('/admin/login')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  // 每 60s 自动刷新
  refreshTimer = window.setInterval(() => {
    fetchData()
  }, 60 * 1000)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

// Chart rendering
function renderChart() {
  if (!chartRef.value || !stats.value) return
  const data = {
    labels: ['活跃', '封禁'],
    datasets: [
      {
        data: [stats.value.activeUsers || 0, stats.value.bannedUsers || 0],
        backgroundColor: ['#34d399', '#fb7185'],
      },
    ],
  }

  if (chartInstance) {
    chartInstance.data = data as any
    chartInstance.update()
  } else {
    chartInstance = new Chart(chartRef.value as HTMLCanvasElement, {
      type: 'doughnut',
      data: data as any,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
        },
      },
    })
  }
}

watch(stats, () => {
  nextTick(() => renderChart())
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">管理员主页</h1>
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold">欢迎，{{ getDisplayName(info) }}</h2>
        <div class="text-sm text-gray-500">角色: {{ info ? (info.role === 'admin' ? '系统管理员' : info.role === 'wiki_admin' ? 'Wiki管理员' : info.role) : '-' }}</div>
      </div>
      <div class="space-x-2">
        <button @click="fetchData" class="px-3 py-1 bg-yellow-500 text-white rounded">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="space-y-3">
      <div class="h-6 bg-gray-200 rounded w-1/3 animate-pulse"></div>
      <div class="grid grid-cols-3 gap-4">
        <div class="h-20 bg-gray-200 rounded animate-pulse"></div>
        <div class="h-20 bg-gray-200 rounded animate-pulse"></div>
        <div class="h-20 bg-gray-200 rounded animate-pulse"></div>
      </div>
    </div>

    <div v-if="error" class="text-red-500">{{ error }}</div>

    <section v-if="!loading && info">
      <h2 class="text-lg font-semibold">个人信息</h2>
      <div class="mt-2">
        <p>管理员: {{ getDisplayName(info) }}</p>
        <p>角色: {{ info.role === 'admin' ? '系统管理员' : info.role === 'wiki_admin' ? 'Wiki管理员' : info.role }}</p>
        <p>登录账号: {{ info.username }}</p>
        <p>上次登录: {{ formatDate(info.lastLogin) }}</p>
      </div>
    </section>
    <section class="mt-6" v-if="!loading && stats">
      <h2 class="text-lg font-semibold">系统概况</h2>
      <div class="mt-3 p-4 bg-white shadow rounded">
        <div class="flex items-center justify-between mb-3">
          <div>
            <div class="text-sm text-gray-500">总用户</div>
            <div class="text-xl font-bold">{{ stats.totalUsers || 0 }}</div>
          </div>
          <div class="text-sm text-gray-500">最后刷新: {{ lastRefresh ? new Date(lastRefresh).toLocaleString() : '-' }}</div>
        </div>

        <div class="grid grid-cols-2 gap-4 items-center">
          <div class="h-48">
            <canvas ref="chartRef" class="w-full h-full"></canvas>
          </div>
          <div>
            <div class="grid grid-cols-1 gap-3">
              <div class="p-3 bg-gray-50 rounded">
                <div class="text-sm text-gray-500">活跃用户</div>
                <div class="text-2xl font-semibold">{{ stats.activeUsers || 0 }}</div>
              </div>
              <div class="p-3 bg-gray-50 rounded">
                <div class="text-sm text-gray-500">封禁用户</div>
                <div class="text-2xl font-semibold">{{ stats.bannedUsers || 0 }}</div>
              </div>
              <div class="p-3 bg-gray-50 rounded">
                <div class="text-sm text-gray-500">活跃占比</div>
                <div class="text-2xl font-semibold">{{ totalPercent(stats) }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* 仪表盘样式可扩展 */
</style>
