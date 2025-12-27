<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import adminApi from '../../api/admin'
import auth from '../../services/auth'

type ReviewSummary = {
  id: string
  title: string
  status: string
  submittedAt: string
  submittedBy: string
  type?: string
  reason?: string
  reportedContent?: string
  contentAuthor?: string
  locationName?: string
}

const reviews = ref<ReviewSummary[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const statusFilter = ref<'all' | 'pending' | 'approved' | 'rejected' | 'resolved' | 'dismissed'>(
  'all',
)
const contentType = ref<'review' | 'review_report'>('review') // 内容类型切换：评论审核或评论举报
const keyword = ref('')
const loading = ref(false)
const error = ref('')

const selectedId = ref<string | null>(null)
const detail = ref<any | null>(null)
const detailLoading = ref(false)
const detailError = ref('')
const handling = ref(false)

// 批量操作
const selectedIds = ref<Set<string>>(new Set())
const batchProcessing = ref(false)
const showBatchDialog = ref(false)
const batchAction = ref<'approve' | 'reject' | 'delete'>('approve')
const batchReason = ref('')

// 根据内容类型动态生成状态选项
const statusOptions = computed(() => {
  if (contentType.value === 'review_report') {
    // 评论举报审核：只保留 全部状态、待审核、已处理、已驳回
    return [
      { value: 'all', label: '全部状态' },
      { value: 'pending', label: '待审核' },
      { value: 'resolved', label: '已处理' },
      { value: 'dismissed', label: '已驳回' },
    ]
  } else {
    // 评论审核（review）：只保留 全部状态、待审核、已通过
    return [
      { value: 'all', label: '全部状态' },
      { value: 'pending', label: '待审核' },
      { value: 'approved', label: '已通过' },
    ]
  }
})

const contentTypeOptions = [
  { value: 'review', label: '评论审核' },
  { value: 'review_report', label: '评论举报审核' },
]

const selectedSummary = computed(
  () => reviews.value.find((item) => item.id === selectedId.value) || null,
)
const pageCount = computed(() => {
  if (!total.value) return 1
  return Math.max(1, Math.ceil(total.value / pageSize))
})

// 批量操作相关计算属性
const allSelected = computed(() => {
  if (!reviews.value.length) return false
  return reviews.value.every((r) => selectedIds.value.has(r.id))
})

const selectedCount = computed(() => selectedIds.value.size)

const canBatchProcess = computed(() => {
  return selectedCount.value > 0 && !batchProcessing.value
})

// 切换全选
function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value.clear()
  } else {
    reviews.value.forEach((r) => selectedIds.value.add(r.id))
  }
}

// 切换单个选择
function toggleSelect(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

function formatDate(val?: string | null) {
  if (!val) return '—'
  const dt = new Date(val)
  if (Number.isNaN(dt.getTime())) return val
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

function statusText(status: string) {
  switch (status) {
    case 'approved':
      return '已通过'
    case 'rejected':
      return '已拒绝'
    case 'resolved':
      return '已处理'
    case 'dismissed':
      return '已驳回'
    case 'pending':
    default:
      return '待审核'
  }
}

function statusClass(status: string) {
  if (status === 'approved') return 'bg-green-100 text-green-700'
  if (status === 'rejected') return 'bg-red-100 text-red-600'
  if (status === 'resolved') return 'bg-blue-100 text-blue-700'
  if (status === 'dismissed') return 'bg-gray-100 text-gray-600'
  return 'bg-yellow-100 text-yellow-700'
}

async function fetchReviews() {
  loading.value = true
  error.value = ''
  try {
    let res

    if (contentType.value === 'review_report') {
      // 获取评论举报列表
      const params: { page: number; pageSize: number; status?: string } = {
        page: page.value,
        pageSize,
      }
      // 当选择"全部状态"时，明确传递 'all' 给后端
      if (statusFilter.value !== 'all') {
        params.status = statusFilter.value
      } else {
        params.status = 'all'
      }
      res = await adminApi.getReviewReports(params)
      reviews.value = (res.items || []).map((item: any) => ({
        id: item.id,
        title: item.title,
        status: item.status,
        submittedAt: item.createdAt,
        submittedBy: item.reporter?.nickname || '未知',
        type: item.type,
        reason: item.reason,
      }))
    } else {
      // 统一使用内容审核接口
      const params: { page: number; pageSize: number; status?: string; q?: string; type?: string } =
        {
          page: page.value,
          pageSize,
        }
      if (statusFilter.value !== 'all') params.status = statusFilter.value
      const query = keyword.value.trim()
      if (query) params.q = query

      // 传递内容类型 (suggestion 或 review)
      params.type = contentType.value

      res = await adminApi.getContentReviews(params)
      reviews.value = (res.items || []).map((item: any) => ({
        id: item.id,
        title: item.title,
        status: item.status,
        submittedAt: item.createdAt,
        submittedBy: item.author,
        type: item.type,
      }))
    }

    total.value = res.total || reviews.value.length

    if (!reviews.value.length) {
      selectedId.value = null
      detail.value = null
      return
    }
    if (!reviews.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = reviews.value[0]?.id || null
    }
  } catch (e: any) {
    // 如果是 404 错误且是评论举报，说明后端还没有实现该接口，显示友好提示
    if (e.status === 404 && contentType.value === 'review_report') {
      error.value = '该功能暂未部署到当前后端服务器'
      reviews.value = []
      total.value = 0
    } else {
      error.value = e.message || '获取审核列表失败'
    }
  } finally {
    loading.value = false
  }
}

async function fetchDetail(id: string) {
  detailLoading.value = true
  detailError.value = ''
  try {
    if (contentType.value === 'review_report') {
      // 获取举报详情
      detail.value = await adminApi.getReviewReportDetail(id)
    } else {
      // 统一使用内容审核详情接口，传递 type 参数
      detail.value = await adminApi.getContentReviewDetail(id, contentType.value)
    }
  } catch (e: any) {
    detailError.value = e.message || '获取审核详情失败'
    detail.value = null
  } finally {
    detailLoading.value = false
  }
}

function selectReview(id: string) {
  if (selectedId.value === id) return
  selectedId.value = id
}

// 打开图片新窗口
function openImage(url: string) {
  window.open(url, '_blank')
}

async function approveCurrent() {
  if (!selectedId.value) return
  const note = prompt('请输入审核备注（可选）', detail.value?.reviewerNote || '')
  if (note === null) return
  handling.value = true
  try {
    await adminApi.approveContentReview(selectedId.value, note || undefined, contentType.value)
    alert('审核通过')
    await fetchReviews()
    if (selectedId.value) await fetchDetail(selectedId.value)
  } catch (e: any) {
    alert(e.message || '审核失败')
  } finally {
    handling.value = false
  }
}

async function rejectCurrent() {
  if (!selectedId.value) return
  const reason = prompt('请输入拒绝原因', detail.value?.reviewerNote || '')
  if (reason === null) return
  if (!reason.trim()) {
    alert('拒绝原因不能为空')
    return
  }
  handling.value = true
  try {
    await adminApi.rejectContentReview(selectedId.value, reason, contentType.value)
    alert('已拒绝该提交')
    await fetchReviews()
    if (selectedId.value) await fetchDetail(selectedId.value)
  } catch (e: any) {
    alert(e.message || '操作失败')
  } finally {
    handling.value = false
  }
}

// ========== 举报处理函数 ==========
async function resolveReport() {
  if (!selectedId.value) return

  // 第一步：询问处理方式
  const actionConfirm = confirm(
    '确认处理此举报？\n\n点击【确定】= 删除被举报的评论\n点击【取消】= 仅标记举报为已处理，保留评论',
  )

  // 用户点击取消后不再继续，完全取消操作
  const note = prompt('请输入处理备注（可选）', '')
  if (note === null) {
    // 用户在备注输入框点击取消，完全取消操作
    return
  }

  const action = actionConfirm ? 'reject_review' : 'resolve'

  handling.value = true
  try {
    await adminApi.resolveReviewReport(selectedId.value, action, note || undefined)
    alert(actionConfirm ? '举报已处理，评论已删除' : '举报已标记为已处理')
    await fetchReviews()
    if (selectedId.value) await fetchDetail(selectedId.value)
  } catch (e: any) {
    alert(e.message || '处理失败')
  } finally {
    handling.value = false
  }
}

async function dismissReport() {
  if (!selectedId.value) return
  const reason = prompt('请输入驳回原因（可选）', '')
  if (reason === null) return

  handling.value = true
  try {
    await adminApi.dismissReviewReport(selectedId.value, reason || undefined)
    alert('举报已驳回')
    await fetchReviews()
    if (selectedId.value) await fetchDetail(selectedId.value)
  } catch (e: any) {
    alert(e.message || '驳回失败')
  } finally {
    handling.value = false
  }
}

// ========== 批量操作功能 ==========
function openBatchDialog(action: 'approve' | 'reject' | 'delete') {
  if (selectedCount.value === 0) {
    alert('请先选择要操作的项目')
    return
  }
  batchAction.value = action
  batchReason.value = ''
  showBatchDialog.value = true
}

async function confirmBatchOperation() {
  if (batchAction.value === 'reject' && !batchReason.value.trim()) {
    alert('请输入拒绝原因')
    return
  }

  const actionText = {
    approve: '批准通过',
    reject: '拒绝',
    delete: '删除',
  }[batchAction.value]

  if (!confirm(`确认${actionText} ${selectedCount.value} 项内容吗？`)) {
    return
  }

  batchProcessing.value = true
  const ids = Array.from(selectedIds.value)
  let successCount = 0
  let failCount = 0

  try {
    // Wiki建议或评论审核批量操作
    for (const id of ids) {
      try {
        if (batchAction.value === 'approve') {
          await adminApi.approveContentReview(id, batchReason.value || undefined, contentType.value)
        } else if (batchAction.value === 'reject') {
          await adminApi.rejectContentReview(id, batchReason.value, contentType.value)
        } else if (batchAction.value === 'delete') {
          // TODO: 需要后端实现删除接口
          // await adminApi.deleteContentReview(id)
          console.warn('删除功能暂未实现')
        }
        successCount++
      } catch (e) {
        console.error(`处理 ${id} 失败:`, e)
        failCount++
      }
    }

    alert(`批量操作完成！\n成功: ${successCount} 项\n失败: ${failCount} 项`)
    selectedIds.value.clear()
    showBatchDialog.value = false
    await fetchReviews()
  } catch (e: any) {
    alert(e.message || '批量操作失败')
  } finally {
    batchProcessing.value = false
  }
}

function cancelBatchOperation() {
  showBatchDialog.value = false
  batchReason.value = ''
}

function onContentTypeChange() {
  page.value = 1
  // 如果当前选中的状态不在新内容类型的选项中，重置为 'all'
  const validStatuses = statusOptions.value.map((opt) => opt.value)
  if (!validStatuses.includes(statusFilter.value)) {
    statusFilter.value = 'all'
  }
  fetchReviews()
}

// 监听 statusOptions 变化，确保当前选中的状态有效
watch(
  statusOptions,
  (newOptions) => {
    const validStatuses = newOptions.map((opt) => opt.value)
    if (!validStatuses.includes(statusFilter.value)) {
      statusFilter.value = 'all'
    }
  },
  { immediate: true },
)

function onSearch() {
  page.value = 1
  fetchReviews()
}

function changeStatus() {
  page.value = 1
  fetchReviews()
}

function goPrev() {
  if (page.value <= 1) return
  page.value -= 1
  fetchReviews()
}

function goNext() {
  if (page.value >= pageCount.value) return
  page.value += 1
  fetchReviews()
}

onMounted(() => {
  fetchReviews()
})

watch(selectedId, (newId) => {
  if (newId) {
    fetchDetail(newId)
  } else {
    detail.value = null
  }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">内容审核</h1>

    <!-- 顶部筛选栏 -->
    <div class="mb-6 flex flex-col lg:flex-row lg:items-center lg:space-x-4 space-y-3 lg:space-y-0">
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-600">审核类型</label>
        <select
          v-model="contentType"
          @change="onContentTypeChange"
          class="border px-3 py-2 rounded"
        >
          <option v-for="item in contentTypeOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-600">状态</label>
        <select v-model="statusFilter" @change="changeStatus" class="border px-3 py-2 rounded">
          <option v-for="item in statusOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
      <div class="text-sm text-gray-500">共 {{ total }} 条记录</div>
    </div>

    <!-- 批量操作栏 -->
    <div
      v-if="selectedCount > 0"
      class="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between"
    >
      <div class="flex items-center space-x-4">
        <span class="text-sm text-blue-700 font-medium">已选择 {{ selectedCount }} 项</span>
        <button
          @click="selectedIds.clear()"
          class="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          取消选择
        </button>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="openBatchDialog('reject')"
          :disabled="!canBatchProcess"
          class="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          批量拒绝
        </button>
        <button
          @click="openBatchDialog('delete')"
          :disabled="!canBatchProcess"
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          批量删除
        </button>
      </div>
    </div>
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="bg-white border rounded shadow-sm xl:col-span-1">
        <div class="border-b px-4 py-3 font-semibold flex items-center justify-between">
          <span>待处理列表</span>
          <label v-if="reviews.length > 0" class="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              :checked="allSelected"
              @change="toggleSelectAll"
              class="w-4 h-4 text-blue-600 rounded"
            />
            <span class="text-sm font-normal text-gray-600">全选</span>
          </label>
        </div>
        <div class="max-h-[70vh] overflow-y-auto">
          <div v-if="loading" class="p-4 text-gray-500">列表加载中...</div>
          <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
          <template v-else>
            <div
              v-for="item in reviews"
              :key="item.id"
              class="px-4 py-3 border-b hover:bg-gray-50"
              :class="{ 'bg-blue-50': item.id === selectedId }"
            >
              <div class="flex items-start space-x-3">
                <input
                  type="checkbox"
                  :checked="selectedIds.has(item.id)"
                  @change="toggleSelect(item.id)"
                  @click.stop
                  class="mt-1 w-4 h-4 text-blue-600 rounded"
                />
                <div @click="selectReview(item.id)" class="flex-1 cursor-pointer">
                  <div class="flex items-center justify-between">
                    <div class="font-medium text-gray-800">{{ item.title }}</div>
                    <span class="text-xs px-2 py-1 rounded" :class="statusClass(item.status)">
                      {{ statusText(item.status) }}
                    </span>
                  </div>
                  <div class="text-sm text-gray-500 mt-1">
                    提交人：{{ item.submittedBy }} · {{ formatDate(item.submittedAt) }}
                  </div>
                  <div v-if="item.type" class="text-xs text-gray-400 mt-1">
                    类型：{{ item.type }}
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!reviews.length" class="p-4 text-gray-500">暂无数据</div>
          </template>
        </div>
        <div class="px-4 py-3 flex items-center justify-between text-sm">
          <button
            @click="goPrev"
            :disabled="page <= 1"
            class="px-3 py-1 border rounded disabled:opacity-50"
          >
            上一页
          </button>
          <div>第 {{ page }} / {{ pageCount }} 页</div>
          <button
            @click="goNext"
            :disabled="page >= pageCount"
            class="px-3 py-1 border rounded disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>

      <div class="bg-white border rounded shadow-sm xl:col-span-2 h-fit">
        <div class="border-b px-6 py-4 flex items-center justify-between">
          <div>
            <div class="text-xl font-semibold">
              {{ selectedSummary?.title || '请选择审核任务' }}
            </div>
            <div v-if="selectedSummary" class="text-sm text-gray-500 mt-1">
              提交人：{{ selectedSummary.submittedBy }} · 提交时间：{{
                formatDate(selectedSummary.submittedAt)
              }}
            </div>
          </div>
          <div v-if="selectedSummary" class="space-x-2">
            <span class="px-2 py-1 text-xs rounded" :class="statusClass(selectedSummary.status)">
              {{ statusText(selectedSummary.status) }}
            </span>
          </div>
        </div>

        <div class="p-6">
          <div v-if="!selectedId" class="text-gray-500">请选择左侧的审核记录查看详情。</div>
          <div v-else-if="detailLoading" class="text-gray-500">详情加载中...</div>
          <div v-else-if="detailError" class="text-red-500">{{ detailError }}</div>

          <!-- 评论审核详情 -->
          <div v-else-if="detail && contentType === 'review'" class="space-y-6">
            <section>
              <h3 class="text-lg font-semibold mb-2">评论信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
                <div>
                  <span class="text-gray-400">评论作者：</span
                  >{{ detail.author?.nickname || '未知' }}
                </div>
                <div>
                  <span class="text-gray-400">评论时间：</span>{{ formatDate(detail.createdAt) }}
                </div>
                <div>
                  <span class="text-gray-400">关联地点：</span>{{ detail.location?.name || '未知' }}
                </div>
                <div><span class="text-gray-400">评分：</span>{{ detail.rating || '—' }} 分</div>
              </div>
            </section>

            <section>
              <h3 class="text-lg font-semibold mb-2">评论内容</h3>
              <div class="border rounded bg-gray-50 p-4 text-sm whitespace-pre-wrap">
                {{ detail.comment || '无内容' }}
              </div>
            </section>

            <section v-if="detail.images && detail.images.length">
              <h3 class="text-lg font-semibold mb-2">评论图片</h3>
              <div class="flex flex-wrap gap-2">
                <img
                  v-for="(img, idx) in detail.images"
                  :key="idx"
                  :src="img"
                  @error="
                    (e) =>
                      ((e.target as HTMLImageElement).src =
                        'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect fill=%22%23ddd%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22%3E图片加载失败%3C/text%3E%3C/svg%3E')
                  "
                  class="w-32 h-32 object-cover rounded border cursor-pointer hover:opacity-80 transition-opacity"
                  @click="openImage(img)"
                  title="点击查看原图"
                />
              </div>
            </section>

            <section v-if="detail.status === 'pending'" class="flex space-x-3">
              <button
                @click="approveCurrent"
                :disabled="handling"
                class="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
              >
                通过审核
              </button>
              <button
                @click="rejectCurrent"
                :disabled="handling"
                class="px-4 py-2 bg-red-600 text-white rounded disabled:opacity-50"
              >
                拒绝审核
              </button>
            </section>
            <div v-else class="text-sm text-gray-500">
              该评论已审核：{{ statusText(detail.status) }}
            </div>
          </div>

          <!-- 举报详情（评论或回复） -->
          <div v-else-if="detail && contentType === 'review_report'" class="space-y-6">
            <section>
              <h3 class="text-lg font-semibold mb-2">举报信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
                <div>
                  <span class="text-gray-400">举报人：</span
                  >{{ detail.reporter?.nickname || '未知' }} ({{ detail.reporter?.phone }})
                </div>
                <div>
                  <span class="text-gray-400">举报时间：</span>{{ formatDate(detail.createdAt) }}
                </div>
                <div class="md:col-span-2">
                  <span class="text-gray-400">举报原因：</span>{{ detail.reason || '—' }}
                </div>
              </div>
            </section>

            <!-- 被举报的评论 -->
            <section v-if="contentType === 'review_report' && detail.review">
              <h3 class="text-lg font-semibold mb-2">被举报的评论</h3>
              <div class="border rounded bg-red-50 p-4 space-y-2">
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">评论作者：</span
                  >{{ detail.review.author?.nickname || '未知' }}
                </div>
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">关联地点：</span
                  >{{ detail.review.location?.name || '未知' }}
                  <span v-if="detail.review.location?.address" class="ml-2 text-gray-400"
                    >({{ detail.review.location.address }})</span
                  >
                </div>
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">评分：</span>{{ detail.review.rating || '—' }} 分
                </div>
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">评论时间：</span
                  >{{ formatDate(detail.review.createdAt) }}
                </div>
                <div class="mt-3 pt-3 border-t border-red-200">
                  <div class="text-sm font-medium mb-1">评论内容：</div>
                  <div class="text-sm whitespace-pre-wrap">{{ detail.review.comment }}</div>
                </div>
                <div v-if="detail.review.images && detail.review.images.length" class="mt-2">
                  <div class="text-sm font-medium mb-1">图片：</div>
                  <div class="flex flex-wrap gap-2">
                    <img
                      v-for="(img, idx) in detail.review.images"
                      :key="idx"
                      :src="img"
                      @error="
                        (e) =>
                          ((e.target as HTMLImageElement).src =
                            'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect fill=%22%23ddd%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22%3E加载失败%3C/text%3E%3C/svg%3E')
                      "
                      class="w-20 h-20 object-cover rounded cursor-pointer hover:opacity-80 transition-opacity"
                      @click="openImage(img)"
                      title="点击查看原图"
                    />
                  </div>
                </div>
              </div>
            </section>

            <!-- 被举报的回复 -->
            <!-- 回复举报功能已移除 -->
            <section v-if="false">
              <h3 class="text-lg font-semibold mb-2">被举报的回复</h3>
              <div class="border rounded bg-red-50 p-4 space-y-2">
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">回复作者：</span
                  >{{ detail.reply.author?.nickname || '未知' }}
                </div>
                <div class="text-sm text-gray-600">
                  <span class="text-gray-400">回复时间：</span
                  >{{ formatDate(detail.reply.createdAt) }}
                </div>
                <div class="mt-3 pt-3 border-t border-red-200">
                  <div class="text-sm font-medium mb-1">回复内容：</div>
                  <div class="text-sm whitespace-pre-wrap">{{ detail.reply.content }}</div>
                </div>
                <div v-if="detail.reply.review" class="mt-3 pt-3 border-t border-red-200">
                  <div class="text-xs text-gray-500">
                    回复的评论摘要：{{ detail.reply.review.comment?.substring(0, 100) }}...
                  </div>
                  <div class="text-xs text-gray-500">
                    地点：{{ detail.reply.review.location?.name || '未知' }}
                  </div>
                </div>
              </div>
            </section>

            <!-- 举报处理操作 -->
            <section v-if="detail.status === 'pending'" class="flex space-x-3">
              <button
                @click="resolveReport"
                :disabled="handling"
                class="px-4 py-2 bg-red-600 text-white rounded disabled:opacity-50"
              >
                处理举报（删除内容）
              </button>
              <button
                @click="dismissReport"
                :disabled="handling"
                class="px-4 py-2 bg-gray-600 text-white rounded disabled:opacity-50"
              >
                驳回举报
              </button>
            </section>
            <div v-else class="text-sm text-gray-500">
              该举报已处理：{{ statusText(detail.status) }}
              <span v-if="detail.status === 'resolved'" class="ml-2 text-red-600"
                >(内容已删除)</span
              >
              <span v-if="detail.status === 'dismissed'" class="ml-2 text-green-600"
                >(内容已保留)</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作确认对话框 -->
    <div
      v-if="showBatchDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="cancelBatchOperation"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b">
          <h3 class="text-lg font-semibold">确认批量操作</h3>
        </div>
        <div class="px-6 py-4">
          <p class="text-gray-700 mb-4">
            您将对 <strong>{{ selectedCount }}</strong> 项内容执行
            <strong class="text-blue-600">
              {{
                batchAction === 'approve'
                  ? '批量通过'
                  : batchAction === 'reject'
                    ? '批量拒绝'
                    : '批量删除'
              }}
            </strong>
            操作，此操作不可撤销。
          </p>
          <div v-if="batchAction === 'reject'" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">拒绝原因</label>
            <textarea
              v-model="batchReason"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入拒绝原因（可选）"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t flex justify-end space-x-3">
          <button
            @click="cancelBatchOperation"
            :disabled="batchProcessing"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            取消
          </button>
          <button
            @click="confirmBatchOperation"
            :disabled="batchProcessing"
            class="px-4 py-2 rounded-md text-white disabled:opacity-50"
            :class="{
              'bg-green-600 hover:bg-green-700': batchAction === 'approve',
              'bg-yellow-600 hover:bg-yellow-700': batchAction === 'reject',
              'bg-red-600 hover:bg-red-700': batchAction === 'delete',
            }"
          >
            <span v-if="batchProcessing">处理中...</span>
            <span v-else>确认操作</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
