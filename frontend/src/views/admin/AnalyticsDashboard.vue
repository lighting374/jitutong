<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { EChartsType } from 'echarts'
import adminApi from '../../api/admin'

type OverviewData = {
  dailyActive: Array<{ date: string; value: number }>
  weeklyActive: number
  monthlyActive: number
  hotspotAreas: Array<{ name: string; visits: number }>
  reviewStats: { pending: number; approved: number; rejected: number }
}

type TopLocation = {
  id: number
  name: string
  averageRating: number
  reviewCount: number
  category: string
}

type ReviewTrend = {
  date: string
  count: number
}

type SearchKeyword = {
  keyword: string
  count: number
  trend: 'up' | 'down' | 'stable'
}

const overview = reactive<OverviewData>({
  dailyActive: [],
  weeklyActive: 0,
  monthlyActive: 0,
  hotspotAreas: [],
  reviewStats: { pending: 0, approved: 0, rejected: 0 },
})

const topLocations = ref<TopLocation[]>([])
const reviewTrends = ref<ReviewTrend[]>([])
const searchKeywords = ref<SearchKeyword[]>([])

const lastUpdated = ref<string>('')
const loading = ref(false)
const error = ref('')

const dailyActiveRef = ref<HTMLDivElement | null>(null)
const hotspotRef = ref<HTMLDivElement | null>(null)
const reviewRef = ref<HTMLDivElement | null>(null)
const reviewTrendRef = ref<HTMLDivElement | null>(null)
const keywordRef = ref<HTMLDivElement | null>(null)

const charts: Record<string, EChartsType | null> = {
  daily: null,
  hotspot: null,
  review: null,
  reviewTrend: null,
  keyword: null,
}

function destroyCharts() {
  Object.keys(charts).forEach((key) => {
    const chart = charts[key]
    if (chart) {
      chart.dispose()
      charts[key] = null
    }
  })
}

function initCharts() {
  if (dailyActiveRef.value && !charts.daily) charts.daily = echarts.init(dailyActiveRef.value)
  if (hotspotRef.value && !charts.hotspot) charts.hotspot = echarts.init(hotspotRef.value)
  if (reviewRef.value && !charts.review) charts.review = echarts.init(reviewRef.value)
  if (reviewTrendRef.value && !charts.reviewTrend)
    charts.reviewTrend = echarts.init(reviewTrendRef.value)

  // 搜索热词图表：如果容器存在但图表未初始化，则初始化
  if (keywordRef.value && !charts.keyword) {
    charts.keyword = echarts.init(keywordRef.value)
  }
}

function renderCharts() {
  if (charts.daily) {
    charts.daily.setOption({
      grid: { left: 40, right: 20, top: 40, bottom: 40 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: overview.dailyActive.map((item) => item.date) },
      yAxis: { type: 'value' },
      series: [
        {
          name: '日活用户数',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          data: overview.dailyActive.map((item) => item.value),
          areaStyle: {
            opacity: 0.1,
          },
        },
      ],
    })
  }

  if (charts.hotspot) {
    charts.hotspot.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 60, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: 'value',
        name: '访问量',
      },
      yAxis: {
        type: 'category',
        data: overview.hotspotAreas.map((item) => item.name),
      },
      series: [
        {
          name: '访问量',
          type: 'bar',
          data: overview.hotspotAreas.map((item) => item.visits),
          itemStyle: {
            color: '#4F46E5',
            borderRadius: [0, 6, 6, 0],
          },
        },
      ],
    })
  }

  if (charts.review) {
    charts.review.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: ['30%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          data: [
            { name: '待审核', value: overview.reviewStats.pending },
            { name: '已通过', value: overview.reviewStats.approved },
            { name: '已拒绝', value: overview.reviewStats.rejected },
          ],
          label: { formatter: '{b}: {d}%' },
        },
      ],
    })
  }

  // 评论量趋势图
  if (charts.reviewTrend && reviewTrends.value.length > 0) {
    charts.reviewTrend.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: 'category',
        data: reviewTrends.value.map((item) => item.date),
      },
      yAxis: { type: 'value', name: '评论数' },
      series: [
        {
          name: '评论量',
          type: 'line',
          smooth: true,
          data: reviewTrends.value.map((item) => item.count),
          areaStyle: { opacity: 0.2 },
          itemStyle: { color: '#F59E0B' },
        },
      ],
    })
  }

  // 搜索热词图
  // 如果图表未初始化但容器存在，先初始化
  if (keywordRef.value && !charts.keyword) {
    charts.keyword = echarts.init(keywordRef.value)
  }

  if (charts.keyword) {
    if (searchKeywords.value.length > 0) {
      charts.keyword.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 120, right: 40, top: 30, bottom: 40 },
        xAxis: { type: 'value', name: '搜索次数' },
        yAxis: {
          type: 'category',
          data: searchKeywords.value.map((item) => item.keyword),
          axisLabel: {
            formatter: (value: string) => {
              // 确保中文完整显示，如果太长则截断
              return value.length > 10 ? value.substring(0, 10) + '...' : value
            },
          },
        },
        series: [
          {
            name: '搜索次数',
            type: 'bar',
            data: searchKeywords.value.map((item) => item.count),
            itemStyle: {
              color: (params: any) => {
                const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6']
                return colors[params.dataIndex % colors.length]
              },
              borderRadius: [0, 4, 4, 0],
            },
          },
        ],
      })
    } else {
      // 即使没有数据，也渲染一个空图表，避免完全空白
      charts.keyword.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 120, right: 40, top: 30, bottom: 40 },
        xAxis: { type: 'value', name: '搜索次数' },
        yAxis: { type: 'category', data: [] },
        series: [
          {
            name: '搜索次数',
            type: 'bar',
            data: [],
          },
        ],
      })
    }
  }

  Object.values(charts).forEach((chart) => chart?.resize())
}

async function fetchOverview() {
  loading.value = true
  error.value = ''
  try {
    // 获取基础概览数据
    const res = await adminApi.getAnalyticsOverview()
    overview.dailyActive = res.dailyActive || []
    overview.weeklyActive = res.weeklyActive || 0
    overview.monthlyActive = res.monthlyActive || 0
    overview.hotspotAreas = res.hotspotAreas || []
    overview.reviewStats = res.reviewStats || { pending: 0, approved: 0, rejected: 0 }

    // 获取用户活跃度数据
    try {
      const activityRes = await adminApi.getAnalyticsUserActivity()
      if (activityRes.dailyActive) overview.dailyActive = activityRes.dailyActive
      if (activityRes.weeklyActive !== undefined) overview.weeklyActive = activityRes.weeklyActive
      if (activityRes.monthlyActive !== undefined)
        overview.monthlyActive = activityRes.monthlyActive
    } catch (e) {
      console.warn('Failed to fetch user activity:', e)
    }

    // 获取高分地点排行
    try {
      const topLocsRes = await adminApi.getAnalyticsTopLocations()
      topLocations.value = topLocsRes.items || []
    } catch (e) {
      console.warn('Failed to fetch top locations:', e)
      topLocations.value = []
    }

    // 获取评论量趋势
    try {
      const reviewTrendRes = await adminApi.getAnalyticsReviewTrends()
      reviewTrends.value = reviewTrendRes.trends || []
    } catch (e) {
      console.warn('Failed to fetch review trends:', e)
      reviewTrends.value = []
    }

    // 获取搜索热词
    try {
      const keywordsRes = await adminApi.getAnalyticsSearchKeywords()
      searchKeywords.value = keywordsRes.keywords || []
    } catch (e) {
      console.warn('Failed to fetch search keywords:', e)
      searchKeywords.value = []
    }

    lastUpdated.value = new Date().toLocaleString()

    // 等待DOM更新完成后再初始化图表
    await nextTick()
    initCharts()

    // 再次等待确保图表容器已渲染
    await nextTick()
    renderCharts()
  } catch (e: any) {
    error.value = e.message || '获取数据失败'
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchOverview()
}

function handleResize() {
  Object.values(charts).forEach((chart) => chart?.resize())
}

onMounted(() => {
  fetchOverview()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  destroyCharts()
})
</script>

<template>
  <div class="space-y-6">
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between space-y-3 md:space-y-0"
    >
      <div>
        <h1 class="text-2xl font-bold">数据看板</h1>
        <p class="text-sm text-gray-500">总览校园热点与运营指标，掌握用户趋势。</p>
      </div>
      <div class="flex items-center space-x-3">
        <div class="text-sm text-gray-500">最近更新：{{ lastUpdated || '—' }}</div>
        <button
          @click="refresh"
          class="px-4 py-2 bg-indigo-600 text-white rounded"
          :disabled="loading"
        >
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="p-4 bg-red-100 text-red-600 rounded border border-red-200">
      {{ error }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="text-sm text-gray-500">日活峰值</div>
        <div class="text-2xl font-semibold mt-2">
          {{
            overview.dailyActive.length > 0
              ? Math.max(...overview.dailyActive.map((d) => d.value))
              : 0
          }}
        </div>
        <div class="text-xs text-gray-400 mt-1">近 14 天最高日活</div>
      </div>
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="text-sm text-gray-500">周活跃用户</div>
        <div class="text-2xl font-semibold mt-2 text-blue-600">{{ overview.weeklyActive }}</div>
        <div class="text-xs text-gray-400 mt-1">最近 7 天活跃用户数</div>
      </div>
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="text-sm text-gray-500">月活跃用户</div>
        <div class="text-2xl font-semibold mt-2 text-green-600">{{ overview.monthlyActive }}</div>
        <div class="text-xs text-gray-400 mt-1">最近 30 天活跃用户数</div>
      </div>
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="text-sm text-gray-500">待审核</div>
        <div class="text-2xl font-semibold mt-2 text-yellow-600">
          {{ overview.reviewStats.pending }}
        </div>
        <div class="text-xs text-gray-400 mt-1">当前待处理的审核条目</div>
      </div>
    </div>

    <!-- 新增高分地点排行榜 -->
    <div class="bg-white border rounded shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold">🏆 高分地点排行榜</h2>
          <p class="text-xs text-gray-500">根据用户评分和评论数综合排名</p>
        </div>
      </div>
      <div v-if="topLocations.length === 0" class="text-center text-gray-400 py-8">暂无数据</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">排名</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">地点名称</th>
              <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">分类</th>
              <th class="px-4 py-3 text-center text-sm font-semibold text-gray-600">平均评分</th>
              <th class="px-4 py-3 text-center text-sm font-semibold text-gray-600">评论数</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="(loc, idx) in topLocations" :key="loc.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm">
                <span v-if="idx === 0" class="text-2xl">🥇</span>
                <span v-else-if="idx === 1" class="text-2xl">🥈</span>
                <span v-else-if="idx === 2" class="text-2xl">🥉</span>
                <span v-else class="text-gray-500 font-medium">{{ idx + 1 }}</span>
              </td>
              <td class="px-4 py-3 text-sm font-medium text-gray-800">{{ loc.name }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ loc.category || '未分类' }}</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center space-x-1">
                  <span class="text-yellow-500">⭐</span>
                  <span class="text-sm font-semibold">{{ loc.averageRating.toFixed(1) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center text-sm text-gray-600">{{ loc.reviewCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold">近 14 天日活趋势</h2>
            <p class="text-xs text-gray-500">追踪学生使用校园通的活跃波动</p>
          </div>
        </div>
        <div ref="dailyActiveRef" class="h-[320px]"></div>
      </div>

      <div class="bg-white border rounded shadow-sm p-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold">校园热点区域</h2>
            <p class="text-xs text-gray-500">最近一周访问量最高的地点</p>
          </div>
        </div>
        <div ref="hotspotRef" class="h-[320px]"></div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="bg-white border rounded shadow-sm p-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold">内容审核进度</h2>
            <p class="text-xs text-gray-500">待审核、已通过、已拒绝的占比</p>
          </div>
        </div>
        <div ref="reviewRef" class="h-[320px]"></div>
      </div>

      <div class="bg-white border rounded shadow-sm p-4 relative">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold">🔥 搜索热词统计</h2>
            <p class="text-xs text-gray-500">用户最常搜索的关键词 TOP 10</p>
          </div>
        </div>
        <div ref="keywordRef" class="h-[320px]"></div>
        <div
          v-if="searchKeywords.length === 0 && !loading"
          class="absolute inset-0 flex items-center justify-center text-gray-400 pointer-events-none"
          style="top: 60px"
        >
          暂无数据
        </div>
      </div>
    </div>

    <!-- 评论量趋势 -->
    <div class="bg-white border rounded shadow-sm p-4">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold">📈 评论量趋势</h2>
          <p class="text-xs text-gray-500">最近 30 天评论数量变化</p>
        </div>
      </div>
      <div
        v-if="reviewTrends.length === 0"
        class="h-[320px] flex items-center justify-center text-gray-400"
      >
        暂无数据
      </div>
      <div v-else ref="reviewTrendRef" class="h-[320px]"></div>
    </div>
  </div>
</template>
