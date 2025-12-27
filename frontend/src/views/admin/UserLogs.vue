<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import adminApi from '../../api/admin'

const route = useRoute()
const userId = route.query.id as string || ''
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(5)
const loading = ref(false)
const error = ref('')

async function fetchLogs() {
  if (!userId) return
  loading.value = true
  try {
    const res = await adminApi.getAccountLogs(userId, page.value, pageSize.value)
    logs.value = res.items || []
    total.value = res.total || 0
  } catch (e: any) {
    error.value = e.message || '获取日志失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">用户行为日志</h1>
    <div v-if="!userId" class="text-gray-600">未指定用户 ID，请从用户管理中选择用户进入此页面。</div>
    <div v-else>
      <div class="mb-2 text-sm text-gray-600">当前用户 ID：{{ userId }}</div>
      <div class="flex items-center gap-2 mb-4">
        <button
          type="button"
          class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
          :disabled="loading"
          @click="fetchLogs"
        >
          刷新
        </button>
        <span v-if="total" class="text-sm text-gray-500">共 {{ total }} 条记录</span>
      </div>
      <div v-if="loading">加载中...</div>
      <div v-if="error" class="text-red-500 mb-2">{{ error }}</div>
      <ul class="space-y-2 mb-4">
        <li v-for="(l, idx) in logs" :key="idx" class="p-2 bg-white border rounded">
          <div class="text-sm text-gray-600">{{ l.timestamp }}</div>
          <div class="font-medium">{{ l.action }}</div>
          <div class="text-sm text-gray-700">{{ l.detail }}</div>
        </li>
        <li v-if="!loading && logs.length === 0" class="text-sm text-gray-500">暂无日志记录</li>
      </ul>
      <div v-if="total > pageSize" class="flex items-center gap-2 text-sm">
        <button
          type="button"
          class="px-3 py-1 bg-gray-200 rounded disabled:bg-gray-100"
          :disabled="page === 1 || loading"
          @click="page > 1 && (page--, fetchLogs())"
        >
          上一页
        </button>
        <button
          type="button"
          class="px-3 py-1 bg-gray-200 rounded disabled:bg-gray-100"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          @click="page < Math.ceil(total / pageSize) && (page++, fetchLogs())"
        >
          下一页
        </button>
        <span>第 {{ page }} / {{ Math.ceil(total / pageSize) }} 页</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
