<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '../../api/admin'
import { getWikiList } from '../../api/location'
import auth from '../../services/auth'

const router = useRouter()

type WikiItem = {
  wikiId: string | number
  buildingId?: number
  name: string
  description?: string
  imageUrl?: string
  address?: string
  tags?: string[]
  highlights?: string[]
}

const wikis = ref<WikiItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const keyword = ref('')
const loading = ref(false)
const error = ref('')
const selected = ref<WikiItem | null>(null)

// Wiki建议统计
const pendingSuggestions = ref(0)

// Wiki建议审核相关
const showSuggestionPanel = ref(false)
const suggestions = ref<any[]>([])
const suggestionsTotal = ref(0)
const suggestionsPage = ref(1)
const suggestionsPageSize = 10
const suggestionsStatus = ref<'pending' | 'all' | 'approved' | 'rejected'>('pending') // 默认显示待审核
const selectedSuggestion = ref<any | null>(null)
const suggestionLoading = ref(false)
const suggestionHandling = ref(false)

// 批量导入相关
const showImportDialog = ref(false)
const importFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<{ success: number; failed: number; errors: string[] } | null>(null)

const pageCount = computed(() => {
  if (!total.value) return 1
  return Math.max(1, Math.ceil(total.value / pageSize))
})

const suggestionsPageCount = computed(() => {
  if (!suggestionsTotal.value) return 1
  return Math.max(1, Math.ceil(suggestionsTotal.value / suggestionsPageSize))
})

const isWikiAdmin = computed(() => {
  const user = auth.getUser()
  return user && user.role === 'wiki_admin'
})

function formatDate(val?: string) {
  if (!val) return '—'
  const dt = new Date(val)
  if (Number.isNaN(dt.getTime())) return val
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

async function fetchWikis() {
  loading.value = true
  error.value = ''
  try {
    console.log('📚 [Wiki列表] 请求参数:', {
      keyword: keyword.value.trim(),
      page: page.value,
      pageSize: pageSize
    })
    
    const res = await getWikiList({ 
      keyword: keyword.value.trim(),
      page: page.value,
      pageSize: pageSize
    })
    
    console.log('📚 [Wiki列表] API响应:', res)
    
    // 将所有数据映射为统一格式
    const allWikis = (res.items || []).map((item: any) => ({
      wikiId: item.wikiId || item.id,
      buildingId: item.buildingId || item.building_id,
      name: item.name || '未命名',
      description: item.description || '',
      imageUrl: item.imageUrl || item.image_url,
      address: item.address || '',
      tags: item.tags || []
    }))
    
    // 如果后端返回了 total 且数据长度等于 total，说明后端未实现分页，需要客户端分页
    const needClientPagination = !res.total || res.total === allWikis.length
    
    if (needClientPagination) {
      console.log('⚠️ [Wiki列表] 后端未实现分页，使用客户端分页')
      // 客户端分页
      total.value = allWikis.length
      const startIndex = (page.value - 1) * pageSize
      const endIndex = startIndex + pageSize
      wikis.value = allWikis.slice(startIndex, endIndex)
    } else {
      console.log('✅ [Wiki列表] 使用后端分页')
      // 后端已实现分页
      wikis.value = allWikis
      total.value = res.total || allWikis.length
    }
    
    console.log('📚 [Wiki列表] 设置后:', {
      wikis长度: wikis.value.length,
      total: total.value,
      当前页: page.value,
      总页数: pageCount.value,
      分页方式: needClientPagination ? '客户端分页' : '后端分页'
    })
    
    if (!wikis.value.length) {
      selected.value = null
    } else if (!selected.value || !wikis.value.some((item: WikiItem) => item.wikiId === selected.value?.wikiId)) {
      const firstItem = wikis.value[0]
      selected.value = firstItem || null
    }
  } catch (e: any) {
    error.value = e.message || '加载 Wiki 列表失败'
  } finally {
    loading.value = false
  }
}

async function fetchPendingCount() {
  try {
    const res = await adminApi.getContentReviews({ status: 'pending', type: 'suggestion' })
    pendingSuggestions.value = res.items?.length || 0
  } catch (e) {
    console.error('获取待审核数量失败', e)
  }
}

function onSearch() {
  page.value = 1
  fetchWikis()
}

function goPrev() {
  if (page.value <= 1) return
  page.value -= 1
  fetchWikis()
}

function goNext() {
  if (page.value >= pageCount.value) return
  page.value += 1
  fetchWikis()
}

function selectRow(item: WikiItem) {
  selected.value = item
}

function editWiki(item: WikiItem) {
  // 跳转到 Wiki 编辑页面
  router.push(`/location/${item.wikiId}/edit`)
}

function viewWiki(item: WikiItem) {
  // 跳转到 Wiki 查看页面
  router.push(`/location/${item.wikiId}`)
}

function goToReviews() {
  openSuggestionPanel()
}

function openSuggestionPanel() {
  showSuggestionPanel.value = true
  fetchSuggestions()
}

function closeSuggestionPanel() {
  showSuggestionPanel.value = false
  selectedSuggestion.value = null
}

async function fetchSuggestions() {
  suggestionLoading.value = true
  try {
    // 构建请求参数：如果状态是'all'，则不传status参数
    const params: any = {
      page: suggestionsPage.value,
      pageSize: suggestionsPageSize,
      type: 'suggestion'
    }
    
    // 只有非'all'状态才传status参数
    if (suggestionsStatus.value !== 'all') {
      params.status = suggestionsStatus.value
    }
    
    console.log('📝 [Wiki建议] 开始请求，参数:', params)
    
    const res = await adminApi.getContentReviews(params)
    
    console.log('📝 [Wiki建议] API完整响应:', res)
    console.log('📝 [Wiki建议] res.items:', res.items)
    console.log('📝 [Wiki建议] res.total:', res.total)
    
    suggestions.value = res.items || []
    suggestionsTotal.value = res.total || 0
    
    console.log('📝 [Wiki建议] 设置后的值:', {
      suggestions: suggestions.value,
      total: suggestionsTotal.value,
      length: suggestions.value.length
    })
    
    if (suggestions.value.length > 0 && !selectedSuggestion.value) {
      selectedSuggestion.value = suggestions.value[0]
      await fetchSuggestionDetail(selectedSuggestion.value.id)
    }
  } catch (e: any) {
    console.error('❌ [Wiki建议] 获取失败:', e)
    console.error('错误详情:', {
      message: e.message,
      status: e.status,
      response: e.response
    })
  } finally {
    suggestionLoading.value = false
  }
}

async function fetchSuggestionDetail(id: string) {
  try {
    const detail = await adminApi.getContentReviewDetail(id, 'suggestion')
    selectedSuggestion.value = { ...selectedSuggestion.value, ...detail }
  } catch (e: any) {
    console.error('获取建议详情失败', e)
  }
}

async function approveSuggestion() {
  if (!selectedSuggestion.value) return
  const note = prompt('请输入审核备注（可选）', '')
  if (note === null) return
  
  suggestionHandling.value = true
  try {
    await adminApi.approveContentReview(selectedSuggestion.value.id, note || undefined, 'suggestion')
    alert('审核通过')
    await fetchSuggestions()
    await fetchPendingCount()
  } catch (e: any) {
    alert(e.message || '审核失败')
  } finally {
    suggestionHandling.value = false
  }
}

async function rejectSuggestion() {
  if (!selectedSuggestion.value) return
  const reason = prompt('请输入拒绝原因', '')
  if (reason === null) return
  if (!reason.trim()) {
    alert('拒绝原因不能为空')
    return
  }
  
  suggestionHandling.value = true
  try {
    await adminApi.rejectContentReview(selectedSuggestion.value.id, reason, 'suggestion')
    alert('已拒绝该建议')
    await fetchSuggestions()
    await fetchPendingCount()
  } catch (e: any) {
    alert(e.message || '操作失败')
  } finally {
    suggestionHandling.value = false
  }
}

function selectSuggestion(item: any) {
  selectedSuggestion.value = item
  fetchSuggestionDetail(item.id)
}

function statusText(status: string) {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

function createNewWiki() {
  router.push('/location/create')
}

// 批量导入功能
function openImportDialog() {
  showImportDialog.value = true
  importFile.value = null
  importResult.value = null
}

function closeImportDialog() {
  showImportDialog.value = false
  importFile.value = null
  importResult.value = null
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file) {
      importFile.value = file
      importResult.value = null
    }
  }
}

async function performImport() {
  if (!importFile.value) {
    alert('请选择要导入的文件')
    return
  }

  // 检查文件类型
  const fileName = importFile.value.name.toLowerCase()
  if (!fileName.endsWith('.json') && !fileName.endsWith('.csv')) {
    alert('仅支持 JSON 或 CSV 格式文件')
    return
  }

  importing.value = true
  importResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', importFile.value)

    // 使用 auth.getToken() 获取当前角色的 token
    const token = auth.getToken()
    if (!token) {
      alert('请先登录')
      router.push('/admin/login')
      return
    }

    console.log('📤 [批量导入] 开始上传文件:', importFile.value.name)
    console.log('📤 [批量导入] Token:', token ? token.substring(0, 20) + '...' : 'null')

    const response = await fetch('/api/admin/wikis/batch-import', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    console.log('📥 [批量导入] 响应状态:', response.status, response.statusText)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('❌ [批量导入] 错误响应:', errorData)
      throw new Error(errorData.message || `请求失败 (${response.status})`)
    }

    const result = await response.json()
    console.log('✅ [批量导入] 成功响应:', result)
    
    importResult.value = {
      success: result.success || 0,
      failed: result.failed || 0,
      errors: result.errors || []
    }

    if (result.success > 0) {
      alert(`成功导入 ${result.success} 条 Wiki${result.failed > 0 ? `，失败 ${result.failed} 条` : ''}`)
      await fetchWikis()
      await fetchPendingCount()
    } else {
      alert('导入失败：' + (result.errors?.[0] || '未知错误'))
    }
  } catch (e: any) {
    alert('导入失败：' + (e.message || '未知错误'))
    console.error('批量导入失败', e)
  } finally {
    importing.value = false
  }
}

function downloadTemplate() {
  // 创建 JSON 模板
  const template = [
    {
      name: "示例地点A",
      buildingId: 1,
      address: "教学区A区",
      latitude: 31.289549,
      longitude: 121.501123,
      category: "教学楼",
      mainImage: "/images/buildings/example-a.jpg",
      richContent: "<h2>示例地点简介</h2><p>这是一个示例地点的描述内容。</p>",
      structuredInfo: {
        openTime: "7:00-22:00",
        facilities: ["多媒体教室", "研讨室"],
        capacity: "500人"
      },
      tags: ["教学", "多媒体"]
    },
    {
      name: "示例地点B",
      buildingId: 2,
      address: "生活区B区",
      latitude: 31.290123,
      longitude: 121.502456,
      category: "食堂",
      mainImage: "/images/buildings/example-b.jpg",
      richContent: "<h2>示例食堂简介</h2><p>这是一个示例食堂的描述内容。</p>",
      structuredInfo: {
        openTime: "6:30-20:00",
        cuisine: ["中餐", "西餐", "快餐"],
        capacity: "1000人"
      },
      tags: ["餐饮", "生活"]
    }
  ]

  const dataStr = JSON.stringify(template, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'wiki-import-template.json'
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  if (!isWikiAdmin.value) {
    alert('您没有权限访问此页面')
    router.push('/admin/dashboard')
    return
  }
  fetchWikis()
  fetchPendingCount()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Wiki 内容管理</h1>
      <div class="flex items-center space-x-3">
        <button @click="openImportDialog" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          📥 批量导入
        </button>
        <button @click="createNewWiki" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
          新建 Wiki
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="flex items-center space-x-3 mb-6">
      <input
        v-model="keyword"
        @keyup.enter="onSearch"
        placeholder="搜索 Wiki 名称或地址..."
        class="flex-1 border px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button @click="onSearch" class="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        搜索
      </button>
    </div>

    <!-- Wiki 列表表格 -->
    <div class="bg-white border rounded shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Wiki 名称</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Building ID</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">地址</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">状态</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">更新时间</th>
              <th class="px-4 py-3 text-right text-sm font-semibold text-gray-600">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  <span class="ml-3">加载中...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="error">
              <td colspan="6" class="px-4 py-6 text-center text-red-500">{{ error }}</td>
            </tr>
            <tr v-else-if="!wikis.length">
              <td colspan="6" class="px-4 py-6 text-center text-gray-500">暂无 Wiki 数据</td>
            </tr>
            <tr
              v-for="item in wikis"
              :key="item.wikiId"
              @click="selectRow(item)"
              class="border-t hover:bg-blue-50 cursor-pointer transition-colors"
              :class="{ 'bg-blue-50': selected?.wikiId === item.wikiId }"
            >
              <td class="px-4 py-3 text-sm">
                <div class="font-medium text-gray-800">{{ item.name }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">
                {{ item.buildingId || '—' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">
                {{ item.address || '—' }}
              </td>
              <td class="px-4 py-3 text-sm">
                <span class="px-2 py-1 text-xs rounded bg-green-100 text-green-700">
                  published
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500">
                —
              </td>
              <td class="px-4 py-3 text-sm text-right space-x-2">
                <button
                  @click.stop="viewWiki(item)"
                  class="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                >
                  查看
                </button>
                <button
                  @click.stop="editWiki(item)"
                  class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  编辑
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="px-4 py-3 flex items-center justify-between text-sm text-gray-600 border-t bg-gray-50">
        <div>共 {{ total }} 条 Wiki · 第 {{ page }} / {{ pageCount }} 页</div>
        <div class="space-x-2">
          <button
            @click="goPrev"
            :disabled="page <= 1"
            class="px-4 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <button
            @click="goNext"
            :disabled="page >= pageCount"
            class="px-4 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- Wiki 详情预览 -->
    <div v-if="selected" class="mt-6 bg-white border rounded shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Wiki 详情预览</h2>
        <div class="space-x-2">
          <button
            @click="viewWiki(selected)"
            class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            完整查看
          </button>
          <button
            @click="editWiki(selected)"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            编辑内容
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700 mb-4">
        <div><span class="text-gray-500 font-medium">名称：</span>{{ selected.name }}</div>
        <div><span class="text-gray-500 font-medium">Building ID：</span>{{ selected.buildingId || '—' }}</div>
        <div><span class="text-gray-500 font-medium">状态：</span>published</div>
        <div><span class="text-gray-500 font-medium">地址：</span>{{ selected.address || '—' }}</div>
        <div class="md:col-span-2">
          <span class="text-gray-500 font-medium">标签：</span>
          <span v-if="selected.tags && selected.tags.length" class="inline-flex gap-1 ml-2">
            <span v-for="tag in selected.tags" :key="tag" class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
              #{{ tag }}
            </span>
          </span>
          <span v-else class="text-gray-400">暂无标签</span>
        </div>
      </div>

      <div class="border-t pt-4">
        <h3 class="text-sm font-medium text-gray-700 mb-2">内容预览：</h3>
        <div
          v-if="selected.description"
          class="prose prose-sm max-w-none text-gray-600 bg-gray-50 p-4 rounded border max-h-64 overflow-y-auto"
        >
          <p>{{ selected.description }}</p>
        </div>
        <div v-else class="text-gray-400 italic">暂无内容</div>
      </div>
    </div>

    <!-- 快捷功能卡片 -->
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border rounded shadow-sm p-6">
        <h3 class="text-lg font-semibold mb-2">📝 Wiki 统计</h3>
        <p class="text-3xl font-bold text-blue-600">{{ total }}</p>
        <p class="text-sm text-gray-500 mt-1">已发布的 Wiki 条目</p>
      </div>

      <div class="bg-white border rounded shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow" @click="goToReviews">
        <h3 class="text-lg font-semibold mb-2">⏳ 待审核建议</h3>
        <p class="text-3xl font-bold text-yellow-600">{{ pendingSuggestions }}</p>
        <p class="text-sm text-gray-500 mt-1">点击前往审核</p>
      </div>

      <div class="bg-white border rounded shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow" @click="createNewWiki">
        <h3 class="text-lg font-semibold mb-2">➕ 创建新 Wiki</h3>
        <p class="text-sm text-gray-600 mt-4">快速创建新的 Wiki 词条</p>
        <button class="mt-2 w-full py-2 bg-green-600 text-white rounded hover:bg-green-700">
          立即创建
        </button>
      </div>
    </div>

    <!-- Wiki建议审核面板 -->
    <div v-if="showSuggestionPanel" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeSuggestionPanel">
      <div class="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- 头部 -->
        <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
          <h2 class="text-xl font-bold">Wiki建议审核</h2>
          <button @click="closeSuggestionPanel" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <!-- 主体 -->
        <div class="flex-1 overflow-hidden flex">
          <!-- 左侧列表 -->
          <div class="w-1/3 border-r flex flex-col">
            <div class="p-4 border-b bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <div class="text-sm text-gray-600">共 {{ suggestionsTotal }} 条建议</div>
                <select 
                  v-model="suggestionsStatus" 
                  @change="suggestionsPage = 1; fetchSuggestions()"
                  class="text-sm border rounded px-2 py-1"
                >
                  <option value="pending">待审核</option>
                  <option value="approved">已通过</option>
                  <option value="rejected">已拒绝</option>
                  <option value="all">全部</option>
                </select>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto">
              <div v-if="suggestionLoading" class="p-8 text-center text-gray-500">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                加载中...
              </div>
              <div v-else-if="!suggestions.length" class="p-8 text-center text-gray-500">
                暂无Wiki建议
              </div>
              <div
                v-else
                v-for="item in suggestions"
                :key="item.id"
                @click="selectSuggestion(item)"
                class="p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors"
                :class="{ 'bg-blue-50': selectedSuggestion?.id === item.id }"
              >
                <div class="font-medium text-sm mb-1">{{ item.title || `建议 #${item.id}` }}</div>
                <div class="text-xs text-gray-500 flex items-center justify-between">
                  <span>{{ item.author?.nickname || item.submittedBy || '匿名' }}</span>
                  <span
                    class="px-2 py-0.5 rounded text-xs"
                    :class="{
                      'bg-yellow-100 text-yellow-700': item.status === 'pending',
                      'bg-green-100 text-green-700': item.status === 'approved',
                      'bg-red-100 text-red-700': item.status === 'rejected'
                    }"
                  >
                    {{ statusText(item.status) }}
                  </span>
                </div>
                <div class="text-xs text-gray-400 mt-1">{{ formatDate(item.createdAt || item.submittedAt) }}</div>
              </div>
            </div>

            <!-- 分页 -->
            <div class="p-3 border-t bg-gray-50 flex items-center justify-between text-sm">
              <span class="text-gray-600">第 {{ suggestionsPage }} / {{ suggestionsPageCount }} 页</span>
              <div class="space-x-2">
                <button
                  @click="suggestionsPage--; fetchSuggestions()"
                  :disabled="suggestionsPage <= 1"
                  class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  上一页
                </button>
                <button
                  @click="suggestionsPage++; fetchSuggestions()"
                  :disabled="suggestionsPage >= suggestionsPageCount"
                  class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧详情 -->
          <div class="flex-1 overflow-y-auto p-6">
            <div v-if="!selectedSuggestion" class="text-center text-gray-500 py-12">
              请从左侧选择一个建议查看详情
            </div>
            <div v-else class="space-y-6">
              <section>
                <h3 class="text-lg font-semibold mb-3">提交信息</h3>
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div><span class="text-gray-500">提交人：</span>{{ selectedSuggestion.author?.nickname || '未知' }}</div>
                  <div><span class="text-gray-500">提交时间：</span>{{ formatDate(selectedSuggestion.createdAt) }}</div>
                  <div><span class="text-gray-500">关联地点：</span>{{ selectedSuggestion.location?.name || '—' }}</div>
                  <div><span class="text-gray-500">修改原因：</span>{{ selectedSuggestion.reason || '—' }}</div>
                </div>
              </section>

              <section>
                <h3 class="text-lg font-semibold mb-3">建议内容</h3>
                <div class="bg-gray-50 border rounded p-4 text-sm whitespace-pre-wrap">
                  {{ selectedSuggestion.content || '无内容' }}
                </div>
              </section>

              <section v-if="selectedSuggestion.status === 'pending'" class="flex space-x-3 pt-4 border-t">
                <button
                  @click="approveSuggestion"
                  :disabled="suggestionHandling"
                  class="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  通过并应用
                </button>
                <button
                  @click="rejectSuggestion"
                  :disabled="suggestionHandling"
                  class="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                >
                  拒绝
                </button>
              </section>
              <div v-else class="text-sm text-gray-500 pt-4 border-t">
                该建议已处理：{{ statusText(selectedSuggestion.status) }}
                <div v-if="selectedSuggestion.reviewerNote" class="mt-2 bg-gray-50 p-3 rounded">
                  <span class="font-medium">审核备注：</span>{{ selectedSuggestion.reviewerNote }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量导入弹窗 -->
    <div v-if="showImportDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold">批量导入 Wiki</h2>
          <button @click="closeImportDialog" class="text-gray-500 hover:text-gray-700">
            <span class="text-2xl">&times;</span>
          </button>
        </div>

        <div class="p-6">
          <!-- 说明 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 class="font-semibold text-blue-900 mb-2">📋 导入说明</h3>
            <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>支持 JSON 和 CSV 格式文件</li>
              <li>请先下载模板文件，按照模板格式填写数据</li>
              <li>必填字段：name（地点名称）、address（地址）</li>
              <li>buildingId 必须是有效的数字</li>
              <li>导入前请确保数据格式正确</li>
            </ul>
          </div>

          <!-- 下载模板 -->
          <div class="mb-6">
            <button
              @click="downloadTemplate"
              class="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 border border-gray-300 flex items-center justify-center space-x-2"
            >
              <span class="text-xl">📄</span>
              <span class="font-medium">下载 JSON 模板文件</span>
            </button>
          </div>

          <!-- 文件选择 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择导入文件</label>
            <input
              type="file"
              @change="handleFileSelect"
              accept=".json,.csv"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p v-if="importFile" class="mt-2 text-sm text-gray-600">
              已选择：<span class="font-medium">{{ importFile.name }}</span>
              （{{ (importFile.size / 1024).toFixed(2) }} KB）
            </p>
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="mb-6 p-4 rounded-lg" :class="importResult.success > 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
            <h3 class="font-semibold mb-2" :class="importResult.success > 0 ? 'text-green-900' : 'text-red-900'">
              导入结果
            </h3>
            <div class="text-sm space-y-1" :class="importResult.success > 0 ? 'text-green-800' : 'text-red-800'">
              <p>✅ 成功：{{ importResult.success }} 条</p>
              <p v-if="importResult.failed > 0">❌ 失败：{{ importResult.failed }} 条</p>
              <div v-if="importResult.errors && importResult.errors.length > 0" class="mt-2">
                <p class="font-medium">错误详情：</p>
                <ul class="list-disc list-inside ml-2 max-h-40 overflow-y-auto">
                  <li v-for="(error, idx) in importResult.errors" :key="idx" class="text-xs">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex items-center justify-end space-x-3">
            <button
              @click="closeImportDialog"
              class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              取消
            </button>
            <button
              @click="performImport"
              :disabled="!importFile || importing"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ importing ? '导入中...' : '开始导入' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prose {
  color: #4b5563;
}
</style>
