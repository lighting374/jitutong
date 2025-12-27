<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import adminApi from '../../api/admin'
import auth from '../../services/auth'

type LocationRecord = {
  id: string
  name: string
  category?: string
  status?: string
  address?: string
  description?: string
  longitude?: number
  latitude?: number
  tags?: string[]
  updatedAt?: string
}

const list = ref<LocationRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const keyword = ref('')
const statusFilter = ref<'all' | 'draft' | 'published' | 'archived'>('all')
const categoryFilter = ref<'all' | string>('all')
const loading = ref(false)
const error = ref('')

const selected = ref<LocationRecord | null>(null)

// 存储所有已知的分类（不会因为筛选而减少） - 与地图分类对应
const allCategories = ref<Set<string>>(new Set())

const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'archived', label: '已归档' },
]

const categoryOptions = computed(() => {
  return [{ value: 'all', label: '全部分类' }, ...Array.from(allCategories.value).map((c) => ({ value: c, label: c }))]
})

// 检查当前管理员是否为 wiki_admin
const isWikiAdmin = computed(() => {
  const user = auth.getUser()
  return user && user.role === 'wiki_admin'
})

const pageCount = computed(() => {
  if (!total.value) return 1
  return Math.max(1, Math.ceil(total.value / pageSize))
})

// 批量操作计算属性
const allSelected = computed(() => {
  return list.value.length > 0 && list.value.every(item => selectedIds.value.has(item.id))
})

const selectedCount = computed(() => selectedIds.value.size)

const canBatchDelete = computed(() => selectedCount.value > 0 && isWikiAdmin.value)

const formVisible = ref(false)
const form = reactive({
  id: '' as string | null,
  name: '',
  category: '',
  status: 'draft',
  address: '',
  description: '',
  longitude: '',
  latitude: '',
})
const tagsInput = ref('')
const saving = ref(false)
const importing = ref(false)
const exporting = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// 批量操作相关
const selectedIds = ref<Set<string>>(new Set())
const batchDeleting = ref(false)

function statusClass(val?: string) {
  if (val === 'published') return 'bg-green-100 text-green-700'
  if (val === 'archived') return 'bg-gray-200 text-gray-600'
  if (val === 'draft') return 'bg-yellow-100 text-yellow-700'
  return 'bg-blue-100 text-blue-700'
}

function formatDate(val?: string) {
  if (!val) return '—'
  const dt = new Date(val)
  if (Number.isNaN(dt.getTime())) return val
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

async function fetchLocations() {
  loading.value = true
  error.value = ''
  try {
    const res = await adminApi.getLocations(
      page.value,
      pageSize,
      keyword.value.trim(),
      statusFilter.value === 'all' ? '' : statusFilter.value,
      categoryFilter.value === 'all' ? '' : categoryFilter.value,
    )
    list.value = res.items || []
    total.value = res.total || list.value.length
    
    // 收集所有分类到 allCategories（不会被筛选影响）
    list.value.forEach((item) => {
      if (item.category && !allCategories.value.has(item.category)) {
        allCategories.value.add(item.category)
      }
    })
    
    if (!list.value.length) {
      selected.value = null
    } else if (!selected.value || !list.value.some((item) => item.id === selected.value?.id)) {
      selected.value = list.value[0] || null
    }
  } catch (e: any) {
    error.value = e.message || '加载地点列表失败'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchLocations()
}

function changeStatus() {
  page.value = 1
  fetchLocations()
}

function changeCategory() {
  page.value = 1
  fetchLocations()
}

function goPrev() {
  if (page.value <= 1) return
  page.value -= 1
  fetchLocations()
}

function goNext() {
  if (page.value >= pageCount.value) return
  page.value += 1
  fetchLocations()
}

function selectRow(item: LocationRecord) {
  selected.value = item
}

function openCreate() {
  form.id = null
  form.name = ''
  form.category = ''
  form.status = 'online'
  form.address = ''
  form.description = ''
  form.longitude = ''
  form.latitude = ''
  tagsInput.value = ''
  formVisible.value = true
}

function openEdit(item: LocationRecord) {
  form.id = item.id
  form.name = item.name || ''
  form.category = item.category || ''
  form.status = item.status || 'online'
  form.address = item.address || ''
  form.description = item.description || ''
  form.longitude = item.longitude != null ? String(item.longitude) : ''
  form.latitude = item.latitude != null ? String(item.latitude) : ''
  tagsInput.value = (item.tags || []).join(', ')
  formVisible.value = true
}

function closeForm() {
  formVisible.value = false
}

function parseNumber(val: string) {
  if (!val.trim()) return undefined
  const num = Number(val)
  if (Number.isNaN(num)) return null
  return num
}

async function submitForm() {
  if (!form.name.trim()) {
    alert('地点名称不能为空')
    return
  }
  const lng = parseNumber(form.longitude)
  if (lng === null) {
    alert('经度必须是数字')
    return
  }
  const lat = parseNumber(form.latitude)
  if (lat === null) {
    alert('纬度必须是数字')
    return
  }

  const payload = {
    name: form.name.trim(),
    category: form.category.trim(),
    status: form.status,
    address: form.address.trim(),
    description: form.description.trim(),
    longitude: lng,
    latitude: lat,
    tags: tagsInput.value
      .split(',')
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0),
  }

  saving.value = true
  try {
    if (form.id) {
      await adminApi.updateLocation(form.id, payload)
      alert('地点信息已更新')
    } else {
      await adminApi.createLocation(payload)
      alert('地点已创建')
    }
    closeForm()
    await fetchLocations()
  } catch (e: any) {
    alert(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function remove(item: LocationRecord) {
  if (!confirm(`确认删除地点“${item.name}”吗？`)) return
  try {
    await adminApi.deleteLocationRecord(item.id)
    alert('已删除')
    await fetchLocations()
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

function triggerImport() {
  fileInput.value?.click()
}

async function handleImportChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files && input.files[0]
  input.value = ''
  if (!file) return
  importing.value = true
  try {
    await adminApi.importLocationsFromFile(file)
    alert('导入完成')
    await fetchLocations()
  } catch (err: any) {
    alert(err.message || '导入失败，请检查文件格式')
  } finally {
    importing.value = false
  }
}

async function exportAll() {
  exporting.value = true
  try {
    const res = await adminApi.exportLocations()
    const json = JSON.stringify(res, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `locations-export-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    alert('导出成功，已下载 JSON 文件')
  } catch (err: any) {
    alert(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 批量操作函数
function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value.clear()
  } else {
    list.value.forEach(item => selectedIds.value.add(item.id))
  }
}

function toggleSelect(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

async function batchDelete() {
  if (selectedCount.value === 0) return
  
  if (!confirm(`确认删除选中的 ${selectedCount.value} 个地点吗?此操作不可撤销!`)) return
  
  batchDeleting.value = true
  try {
    await adminApi.batchDeleteLocations(Array.from(selectedIds.value))
    alert(`成功删除 ${selectedCount.value} 个地点`)
    selectedIds.value.clear()
    await fetchLocations()
  } catch (err: any) {
    alert(err.message || '批量删除失败')
  } finally {
    batchDeleting.value = false
  }
}

// 初始化时获取所有分类
async function initializeCategories() {
  try {
    // 获取所有地点（不带分类筛选）以收集所有分类
    const res = await adminApi.getLocations(1, 100, '', '', '')
    const items = res.items || []
    items.forEach((item: LocationRecord) => {
      if (item.category && !allCategories.value.has(item.category)) {
        allCategories.value.add(item.category)
      }
    })
  } catch (e) {
    console.error('初始化分类失败:', e)
  }
}

onMounted(async () => {
  await initializeCategories()
  fetchLocations()
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">地点管理</h1>

    <div class="flex flex-col xl:flex-row xl:items-center xl:space-x-4 space-y-3 xl:space-y-0 mb-6">
      <div class="flex items-center space-x-2">
        <input
          v-model="keyword"
          @keyup.enter="onSearch"
          placeholder="搜索名称 / 地址 / 描述"
          class="border px-3 py-2 rounded w-72"
        />
        <button @click="onSearch" class="px-3 py-2 bg-blue-500 text-white rounded">搜索</button>
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-500">状态</label>
        <select v-model="statusFilter" @change="changeStatus" class="border px-3 py-2 rounded">
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-500">分类</label>
        <select v-model="categoryFilter" @change="changeCategory" class="border px-3 py-2 rounded">
          <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <div class="flex-1"></div>
      <div v-if="isWikiAdmin" class="flex items-center space-x-2">
        <button @click="triggerImport" :disabled="importing" class="px-4 py-2 bg-gray-200 text-gray-700 rounded disabled:opacity-60">
          {{ importing ? '导入中...' : '批量导入' }}
        </button>
        <button @click="exportAll" :disabled="exporting" class="px-4 py-2 bg-indigo-500 text-white rounded disabled:opacity-60">
          {{ exporting ? '导出中...' : '导出数据' }}
        </button>
        <button
          v-if="selectedCount > 0"
          @click="batchDelete"
          :disabled="batchDeleting"
          class="px-4 py-2 bg-red-600 text-white rounded disabled:opacity-60"
        >
          {{ batchDeleting ? '删除中...' : `批量删除 (${selectedCount})` }}
        </button>
        <button @click="openCreate" class="px-4 py-2 bg-green-600 text-white rounded">新增地点</button>
      </div>
      <div v-else class="flex items-center space-x-2">
        <button @click="exportAll" :disabled="exporting" class="px-4 py-2 bg-indigo-500 text-white rounded disabled:opacity-60">
          {{ exporting ? '导出中...' : '导出数据' }}
        </button>
        <span class="text-sm text-gray-500">（仅 Wiki 管理员可编辑）</span>
      </div>
    </div>

    <input ref="fileInput" type="file" accept="application/json" class="hidden" @change="handleImportChange" />

    <div class="bg-white border rounded shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y">
          <thead class="bg-gray-50">
            <tr>
              <th v-if="isWikiAdmin" class="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                  class="w-4 h-4 text-blue-600 rounded"
                />
              </th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">名称</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">分类</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">状态</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">地址</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">更新时间</th>
              <th class="px-4 py-3 text-right text-sm font-semibold text-gray-600">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="isWikiAdmin ? 7 : 6" class="px-4 py-6 text-center text-gray-500">数据加载中...</td>
            </tr>
            <tr v-else-if="error">
              <td :colspan="isWikiAdmin ? 7 : 6" class="px-4 py-6 text-center text-red-500">{{ error }}</td>
            </tr>
            <tr v-else-if="!list.length">
              <td :colspan="isWikiAdmin ? 7 : 6" class="px-4 py-6 text-center text-gray-500">暂无地点数据</td>
            </tr>
            <tr
              v-for="item in list"
              :key="item.id"
              class="border-t hover:bg-blue-50"
              :class="{ 'bg-blue-50': selected?.id === item.id }"
            >
              <td v-if="isWikiAdmin" class="px-4 py-3">
                <input
                  type="checkbox"
                  :checked="selectedIds.has(item.id)"
                  @change="toggleSelect(item.id)"
                  @click.stop
                  class="w-4 h-4 text-blue-600 rounded"
                />
              </td>
              <td @click="selectRow(item)" class="px-4 py-3 text-sm text-gray-800 cursor-pointer">
                <div class="font-medium">{{ item.name }}</div>
                <div v-if="item.description" class="text-xs text-gray-400 truncate max-w-xs">{{ item.description }}</div>
              </td>
              <td @click="selectRow(item)" class="px-4 py-3 text-sm text-gray-600 cursor-pointer">{{ item.category || '—' }}</td>
              <td @click="selectRow(item)" class="px-4 py-3 text-sm cursor-pointer">
                <span class="px-2 py-1 text-xs rounded" :class="statusClass(item.status)">{{ item.status || '待定' }}</span>
              </td>
              <td @click="selectRow(item)" class="px-4 py-3 text-sm text-gray-600 cursor-pointer">{{ item.address || '—' }}</td>
              <td @click="selectRow(item)" class="px-4 py-3 text-sm text-gray-500 cursor-pointer">{{ formatDate(item.updatedAt) }}</td>
              <td class="px-4 py-3 text-sm text-right space-x-2">
                <button v-if="isWikiAdmin" @click.stop="openEdit(item)" class="px-3 py-1 bg-blue-500 text-white rounded">编辑</button>
                <button v-if="isWikiAdmin" @click.stop="remove(item)" class="px-3 py-1 bg-red-500 text-white rounded">删除</button>
                <span v-if="!isWikiAdmin" class="text-sm text-gray-400">仅查看</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-4 py-3 flex items-center justify-between text-sm text-gray-600">
        <div>共 {{ total }} 条 · 第 {{ page }} / {{ pageCount }} 页</div>
        <div class="space-x-2">
          <button @click="goPrev" :disabled="page <= 1" class="px-3 py-1 border rounded disabled:opacity-50">上一页</button>
          <button @click="goNext" :disabled="page >= pageCount" class="px-3 py-1 border rounded disabled:opacity-50">下一页</button>
        </div>
      </div>
    </div>

    <div v-if="selected" class="mt-6 bg-white border rounded shadow-sm p-6">
      <h2 class="text-lg font-semibold mb-4">地点详情</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
        <div><span class="text-gray-500">名称：</span>{{ selected.name }}</div>
        <div><span class="text-gray-500">分类：</span>{{ selected.category || '—' }}</div>
        <div><span class="text-gray-500">状态：</span>{{ selected.status || '—' }}</div>
        <div><span class="text-gray-500">地址：</span>{{ selected.address || '—' }}</div>
        <div><span class="text-gray-500">经度：</span>{{ selected.longitude ?? '—' }}</div>
        <div><span class="text-gray-500">纬度：</span>{{ selected.latitude ?? '—' }}</div>
        <div class="md:col-span-2"><span class="text-gray-500">标签：</span>{{ (selected.tags || []).join(', ') || '—' }}</div>
        <div class="md:col-span-2">
          <span class="text-gray-500">描述：</span>
          <span>{{ selected.description || '—' }}</span>
        </div>
        <div class="md:col-span-2 text-gray-500">最近更新时间：{{ formatDate(selected.updatedAt) }}</div>
      </div>
    </div>

    <div v-if="formVisible" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white w-full max-w-2xl rounded shadow-lg">
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <h3 class="text-lg font-semibold">{{ form.id ? '编辑地点' : '新增地点' }}</h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="p-6 space-y-4 text-sm">
          <div>
            <label class="block text-gray-600 mb-1">名称 *</label>
            <input v-model="form.name" class="w-full border px-3 py-2 rounded" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-600 mb-1">分类</label>
              <input v-model="form.category" placeholder="例如：学习" class="w-full border px-3 py-2 rounded" />
            </div>
            <div>
              <label class="block text-gray-600 mb-1">状态</label>
              <select v-model="form.status" class="w-full border px-3 py-2 rounded">
                <option value="draft">草稿</option>
                <option value="published">已发布</option>
                <option value="archived">已归档</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-gray-600 mb-1">地址</label>
            <input v-model="form.address" class="w-full border px-3 py-2 rounded" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-600 mb-1">经度</label>
              <input v-model="form.longitude" placeholder="121.20" class="w-full border px-3 py-2 rounded" />
            </div>
            <div>
              <label class="block text-gray-600 mb-1">纬度</label>
              <input v-model="form.latitude" placeholder="31.20" class="w-full border px-3 py-2 rounded" />
            </div>
          </div>
          <div>
            <label class="block text-gray-600 mb-1">标签（用逗号分隔）</label>
            <input v-model="tagsInput" placeholder="热门, 推荐" class="w-full border px-3 py-2 rounded" />
          </div>
          <div>
            <label class="block text-gray-600 mb-1">描述</label>
            <textarea v-model="form.description" rows="3" class="w-full border px-3 py-2 rounded"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t flex justify-end space-x-3">
          <button @click="closeForm" class="px-4 py-2 border rounded">取消</button>
          <button @click="submitForm" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
