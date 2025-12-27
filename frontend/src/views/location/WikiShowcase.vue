<template>
  <div class="bg-gray-50 min-h-screen">
    <section class="bg-white shadow-sm border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <p class="text-primary font-semibold uppercase tracking-wide text-sm mb-3">Wiki 展示</p>
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div class="flex-1">
            <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">探索同济地点百科</h1>
            <p class="text-gray-600 max-w-2xl">
              精选校园地点的故事、亮点与实用信息，点击卡片即可进入对应的 Wiki 详情。
            </p>
          </div>
          <div class="w-full md:w-96 flex flex-col gap-4">
            <div class="relative">
              <svg
                class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 z-10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-4.35-4.35M5 11a6 6 0 1112 0 6 6 0 01-12 0z"
                />
              </svg>
              <input
                v-model.trim="keyword"
                type="text"
                class="input-field pl-10"
                placeholder="搜索地点、类型或地址"
                @input="handleSearch"
                @focus="showSearchPanel = true"
                @blur="handleBlur"
                @keydown.down.prevent="navigateSuggestions('down')"
                @keydown.up.prevent="navigateSuggestions('up')"
                @keydown.enter="selectSuggestion(selectedSuggestionIndex)"
              />
              <button
                v-if="keyword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 z-10"
                @click="clearKeyword"
                aria-label="清空搜索"
              >
                ✕
              </button>
              
              <!-- 搜索建议下拉面板 -->
              <div
                v-if="showSearchPanel && (searchSuggestions.length > 0 || searchHistory.length > 0 || hotSearches.length > 0)"
                class="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto"
              >
                <!-- 搜索建议 -->
                <div v-if="keyword && searchSuggestions.length > 0" class="p-2">
                  <div class="text-xs text-gray-500 px-3 py-2 font-medium">搜索建议</div>
                  <button
                    v-for="(suggestion, index) in searchSuggestions"
                    :key="'suggestion-' + index"
                    @mousedown.prevent="selectSuggestion(index)"
                    :class="[
                      'w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors flex items-center gap-2',
                      selectedSuggestionIndex === index ? 'bg-gray-50' : ''
                    ]"
                  >
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M5 11a6 6 0 1112 0 6 6 0 01-12 0z" />
                    </svg>
                    <span v-html="highlightSuggestion(suggestion)"></span>
                  </button>
                </div>
                
                <!-- 历史搜索 -->
                <div v-if="!keyword && searchHistory.length > 0" class="p-2">
                  <div class="flex items-center justify-between px-3 py-2">
                    <span class="text-xs text-gray-500 font-medium">历史搜索</span>
                    <button
                      @mousedown.prevent="clearHistory"
                      class="text-xs text-gray-400 hover:text-gray-600"
                    >
                      清空
                    </button>
                  </div>
                  <button
                    v-for="(item, index) in searchHistory"
                    :key="'history-' + index"
                    @mousedown.prevent="selectHistory(item)"
                    class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors flex items-center justify-between gap-2 group"
                  >
                    <div class="flex items-center gap-2 flex-1">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="text-gray-700">{{ item }}</span>
                    </div>
                    <span
                      role="button"
                      tabindex="0"
                      @mousedown.prevent.stop="removeHistory(index)"
                      class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </span>
                  </button>
                </div>
                
                <!-- 热门搜索 -->
                <div v-if="!keyword && hotSearches.length > 0" class="p-2" :class="searchHistory.length > 0 ? 'border-t border-gray-100' : ''">
                  <div class="text-xs text-gray-500 px-3 py-2 font-medium">🔥 热门搜索</div>
                  <button
                    v-for="(item, index) in hotSearches"
                    :key="'hot-' + index"
                    @mousedown.prevent="selectHotSearch(item)"
                    class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors flex items-center gap-2"
                  >
                    <span
                      :class="[
                        'w-5 h-5 flex items-center justify-center text-xs font-bold rounded',
                        index < 3 ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-600'
                      ]"
                    >
                      {{ index + 1 }}
                    </span>
                    <span class="text-gray-700">{{ item }}</span>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 热门搜索词（独立显示区域） -->
            <div v-if="hotSearches.length > 0" class="mt-4">
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm font-medium text-gray-500">🔥 热门搜索：</span>
                <button
                  v-for="(item, index) in hotSearches.slice(0, 8)"
                  :key="'hot-' + index"
                  @click="selectHotSearch(item)"
                  class="px-3 py-1 rounded-full text-sm bg-white text-gray-600 border border-gray-200 hover:border-primary hover:text-primary transition-colors"
                >
                  {{ item }}
                </button>
              </div>
            </div>
            
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4">
              <p class="text-sm text-gray-500">有建议或意见？点击提交 Wiki 建议。</p>
              <button
                @click="showSuggestionDialog = true"
                class="btn btn-primary text-center whitespace-nowrap"
              >
                💡 Wiki 建议
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div v-if="errorMessage" class="card border border-red-100 bg-red-50 text-red-600 mb-6">
        {{ errorMessage }}
        <button class="btn btn-link text-primary ml-2" @click="loadWikiList">重试</button>
      </div>

      <div v-if="isLoading" class="flex justify-center py-16">
        <div class="text-center text-gray-500">
          <div
            class="inline-block h-12 w-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mb-3"
          ></div>
          <p>正在加载 Wiki 列表...</p>
        </div>
      </div>

      <div v-else>
        <div v-if="allTags.length > 0" class="flex flex-wrap items-center gap-2 mb-8">
          <span class="text-sm font-medium text-gray-500 mr-2">热门标签：</span>
          <button
            v-for="tag in allTags"
            :key="tag"
            @click="toggleTag(tag)"
            class="px-3 py-1 rounded-full border text-sm transition-all"
            :class="activeTags.includes(tag)
              ? 'bg-primary text-white border-primary'
              : 'bg-white text-gray-600 border-gray-200 hover:border-primary hover:text-primary'"
          >
            #{{ tag }}
          </button>
          <button
            v-if="activeTags.length > 0"
            @click="clearTags"
            class="px-3 py-1 rounded-full text-sm text-gray-500 hover:text-gray-700 underline"
          >
            清除筛选 ({{ activeTags.length }})
          </button>
        </div>

        <div v-if="filteredItems.length === 0" class="card text-center py-16">
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
              d="M9 14l2 2 4-4m5-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">没有匹配的地点</h3>
          <p class="text-gray-500">尝试更换关键词或清除标签筛选。</p>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <router-link
            v-for="item in filteredItems"
            :key="item.wikiId"
            class="card group hover:shadow-medium transition-all border border-transparent hover:border-primary/10 flex flex-col"
            :to="`/location/${item.wikiId}`"
          >
            <div class="relative h-48 rounded-xl overflow-hidden mb-4">
              <img
                :src="item.imageUrl || '/placeholder-location.png'"
                :alt="item.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div
                class="absolute top-3 left-3 bg-white/90 text-primary text-xs font-semibold px-3 py-1 rounded-full"
              >
                {{ item.type || '校园地点' }}
              </div>
            </div>
            <h3
              class="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary transition-colors"
              v-html="highlightText(item.name, keyword)"
            >
            </h3>
            <p 
              class="text-gray-600 line-clamp-2 mb-3"
              v-html="highlightText(item.description, keyword)"
            ></p>
            <div class="flex items-center text-sm text-gray-500 mb-4">
              <svg class="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span 
                class="line-clamp-1"
                v-html="highlightText(item.address || '嘉定校区', keyword)"
              ></span>
            </div>
            <div class="flex flex-wrap gap-2 mt-auto">
              <span
                v-for="highlight in (item.highlights || []).slice(0, 3)"
                :key="highlight"
                class="text-xs bg-primary/5 text-primary px-2 py-1 rounded-full"
              >
                {{ highlight }}
              </span>
            </div>
          </router-link>
        </div>
      </div>
    </main>

    <!-- Wiki 建议对话框 -->
    <div
      v-if="showSuggestionDialog"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="showSuggestionDialog = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">💡 提交 Wiki 建议</h2>
            <button
              @click="showSuggestionDialog = false"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <p class="text-gray-600 mb-6">
            欢迎提出你的建议！无论是新地点的添加、内容的修正，还是功能的改进，我们都很乐意倾听。
          </p>

          <form @submit.prevent="submitSuggestion">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                建议类型
              </label>
              <select
                v-model="suggestionType"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="general">通用建议（新地点、功能改进等）</option>
                <option value="location">针对具体地点的建议</option>
              </select>
            </div>

            <div v-if="suggestionType === 'location'" class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择地点 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="selectedLocationId"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                :class="{ 'border-red-500': locationError }"
              >
                <option value="">请选择地点</option>
                <option v-for="item in wikiItems" :key="item.wikiId" :value="item.wikiId">
                  {{ item.name }}
                </option>
              </select>
              <p v-if="locationError" class="mt-1 text-sm text-red-600">
                {{ locationError }}
              </p>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                建议内容 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="suggestionContent"
                rows="6"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                :placeholder="suggestionType === 'location' ? '请描述对该地点的建议...' : '请详细描述你的建议...'"
                :class="{ 'border-red-500': suggestionError }"
              ></textarea>
              <p v-if="suggestionError" class="mt-1 text-sm text-red-600">
                {{ suggestionError }}
              </p>
            </div>

            <div class="flex justify-end gap-3">
              <button
                type="button"
                @click="showSuggestionDialog = false"
                class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="isSubmittingSuggestion"
                class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isSubmittingSuggestion">提交中...</span>
                <span v-else">提交建议</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getWikiList, getHotSearches, recordSearch, type WikiListItem } from '../../api/location'
import { getWikiIdFromBuildingId } from '../../config/buildingMapping'
import { API_CONFIG } from '../../config/apiConfig'

const BACKEND_HOST = API_CONFIG.BACKEND_URL

const isLoading = ref(false)
const errorMessage = ref('')

// 处理图片 URL，与 MyFavorites 保持一致
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
const wikiItems = ref<WikiListItem[]>([])
const keyword = ref('')
const activeTags = ref<string[]>([])

// 搜索建议相关
const showSearchPanel = ref(false)
const selectedSuggestionIndex = ref(-1)
const searchHistory = ref<string[]>([])
const hotSearches = ref<string[]>([])

// Wiki 建议相关
const showSuggestionDialog = ref(false)
const suggestionType = ref('general') // 'general' 或 'location'
const selectedLocationId = ref('')
const suggestionContent = ref('')
const suggestionError = ref('')
const locationError = ref('')
const isSubmittingSuggestion = ref(false)

// 搜索建议（基于当前关键词匹配）
const searchSuggestions = computed(() => {
  if (!keyword.value) return []
  
  const kw = keyword.value.toLowerCase()
  const suggestions = new Set<string>()
  
  // 从地点名称中提取建议
  wikiItems.value.forEach(item => {
    if (item.name.toLowerCase().includes(kw)) {
      suggestions.add(item.name)
    }
    // 从类型中提取
    if (item.type && item.type.toLowerCase().includes(kw)) {
      suggestions.add(item.type)
    }
    // 从地址中提取
    if (item.address && item.address.toLowerCase().includes(kw)) {
      suggestions.add(item.address)
    }
  })
  
  return Array.from(suggestions).slice(0, 5)
})

const loadWikiList = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await getWikiList()
    // 数据转换和兼容处理
    wikiItems.value = (res?.items || []).map((item: any) => {
      // 后端可能返回的字段名不一致，做兼容处理
      const id = item.id || item.wikiId || item.buildingId
      const buildingId = item.buildingId || item.building_id || item.id
      
      // 尝试从 structured_info 中提取 building_id
      const structuredBuildingId = item.structuredInfo?.building_id || item.structured_info?.building_id
      const finalBuildingId = structuredBuildingId || buildingId
      
      // 判断 ID 映射：检查当前 ID 是否是 buildingId，如果是则需要映射到 wikiId
      let wikiId = item.wikiId || item.wiki_id || id
      
      // 关键修复：即使有 wikiId，也要检查是否需要映射
      // 对于 buildingId 为 10, 11, 12 的地点，强制使用映射表
      const numericId = Number(wikiId)
      if (numericId === 10 || numericId === 11 || numericId === 12 || finalBuildingId) {
        const mappedWikiId = getWikiIdFromBuildingId(Number(finalBuildingId || numericId))
        if (mappedWikiId) {
          wikiId = mappedWikiId
        }
      }
      
      // 处理图片 URL
      const rawImageUrl = item.imageUrl || item.image_url || item.mainImage || item.main_image
      
      return {
        buildingId: finalBuildingId || numericId,
        wikiId: wikiId,
        name: item.name || '未命名地点',
        description: item.description || '',
        imageUrl: resolveImageUrl(rawImageUrl),
        address: item.address || '',
        type: item.type || item.structuredInfo?.type || item.structured_info?.type || '',
        tags: item.tags || [],
        highlights: item.highlights || []
      } as WikiListItem
    })
  } catch (error: any) {
    console.error('加载 Wiki 列表失败:', error)
    errorMessage.value = error?.message || '加载失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

const allTags = computed(() => {
  const tagSet = new Set<string>()
  wikiItems.value.forEach((item) => {
    item.tags?.forEach((tag) => tagSet.add(tag))
  })
  return Array.from(tagSet)
})

const filteredItems = computed(() => {
  return wikiItems.value.filter((item) => {
    const matchesKeyword = keyword.value
      ? `${item.name}${item.description}${item.address || ''}${item.type || ''}`
          .toLowerCase()
          .includes(keyword.value.toLowerCase())
      : true
    
    // 多标签筛选（交集）：如果有选中的标签，建筑必须同时包含所有选中的标签
    const matchesTag = activeTags.value.length > 0
      ? activeTags.value.every(tag => item.tags?.includes(tag))
      : true
    
    return matchesKeyword && matchesTag
  })
})

// 高亮显示搜索关键词
const highlightText = (text: string, keyword: string): string => {
  if (!keyword || !text) return text
  
  const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark class="bg-yellow-200 text-gray-900 px-0.5 rounded">$1</mark>')
}

// 高亮显示搜索建议（关键词部分高亮）
const highlightSuggestion = (suggestion: string): string => {
  if (!keyword.value) return suggestion
  return highlightText(suggestion, keyword.value)
}

const handleSearch = () => {
  selectedSuggestionIndex.value = -1
  // 计算属性已处理过滤，这里保留以便后续扩展远程搜索
}

// 处理失去焦点
const handleBlur = () => {
  // 延迟关闭，给点击事件时间
  setTimeout(() => {
    showSearchPanel.value = false
    selectedSuggestionIndex.value = -1
  }, 200)
}

// 键盘导航建议
const navigateSuggestions = (direction: 'up' | 'down') => {
  const suggestions = searchSuggestions.value
  if (suggestions.length === 0) return
  
  if (direction === 'down') {
    selectedSuggestionIndex.value = (selectedSuggestionIndex.value + 1) % suggestions.length
  } else {
    selectedSuggestionIndex.value = selectedSuggestionIndex.value <= 0 
      ? suggestions.length - 1 
      : selectedSuggestionIndex.value - 1
  }
}

// 选择搜索建议
const selectSuggestion = (index: number) => {
  const suggestions = searchSuggestions.value
  if (index >= 0 && index < suggestions.length) {
    const selected = suggestions[index]
    if (selected) {
      keyword.value = selected
      addToHistory(selected)
      showSearchPanel.value = false
      selectedSuggestionIndex.value = -1
    }
  }
}

// 选择历史搜索
const selectHistory = (item: string) => {
  keyword.value = item
  showSearchPanel.value = false
}

// 选择热门搜索
const selectHotSearch = (item: string) => {
  keyword.value = item
  addToHistory(item)
  showSearchPanel.value = false
}

// 添加到历史记录
const addToHistory = (term: string) => {
  if (!term) return
  
  // 移除重复项
  const index = searchHistory.value.indexOf(term)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
  }
  
  // 添加到开头
  searchHistory.value.unshift(term)
  
  // 保持最多10条
  if (searchHistory.value.length > 10) {
    searchHistory.value = searchHistory.value.slice(0, 10)
  }
  
  // 保存到 localStorage
  localStorage.setItem('wiki_search_history', JSON.stringify(searchHistory.value))
  
  // 记录到后端（静默记录）
  recordSearch(term)
}

// 移除单条历史
const removeHistory = (index: number) => {
  searchHistory.value.splice(index, 1)
  localStorage.setItem('wiki_search_history', JSON.stringify(searchHistory.value))
}

// 清空历史
const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem('wiki_search_history')
}

const clearKeyword = () => {
  keyword.value = ''
}

// 切换标签（支持多选）
const toggleTag = (tag: string) => {
  const index = activeTags.value.indexOf(tag)
  if (index > -1) {
    // 已选中，移除
    activeTags.value.splice(index, 1)
  } else {
    // 未选中，添加
    activeTags.value.push(tag)
  }
}

// 清除所有标签筛选
const clearTags = () => {
  activeTags.value = []
}

// 提交 Wiki 建议
const submitSuggestion = async () => {
  suggestionError.value = ''
  locationError.value = ''
  
  // 验证
  if (!suggestionContent.value.trim()) {
    suggestionError.value = '请输入建议内容'
    return
  }
  
  if (suggestionContent.value.trim().length < 10) {
    suggestionError.value = '建议内容至少需要10个字符'
    return
  }
  
  // 如果是针对具体地点的建议，必须选择地点
  if (suggestionType.value === 'location' && !selectedLocationId.value) {
    locationError.value = '请选择一个地点'
    return
  }
  
  isSubmittingSuggestion.value = true
  
  try {
    const token = localStorage.getItem('user_token')
    
    // 准备请求数据
    const requestData: any = {
      content: suggestionContent.value.trim(),
      type: suggestionType.value,
    }
    
    // 如果选择了地点，添加 wikiId 和 locationId
    if (suggestionType.value === 'location' && selectedLocationId.value) {
      requestData.wikiId = selectedLocationId.value
      // 查找对应的 locationId
      const selectedWiki = wikiItems.value.find(item => item.wikiId === Number(selectedLocationId.value))
      if (selectedWiki) {
        requestData.locationId = (selectedWiki as any).locationId || selectedWiki.wikiId
      }
    }
    
    const response = await fetch('/api/location/wiki/suggestion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(requestData),
    })
    
    if (!response.ok) {
      throw new Error('提交失败')
    }
    
    // 成功
    alert('感谢你的建议！我们会认真考虑。')
    suggestionContent.value = ''
    selectedLocationId.value = ''
    suggestionType.value = 'general'
    showSuggestionDialog.value = false
  } catch (error) {
    console.error('提交建议失败:', error)
    suggestionError.value = '提交失败，请稍后重试'
  } finally {
    isSubmittingSuggestion.value = false
  }
}

// 加载热门搜索词
const loadHotSearches = async () => {
  try {
    hotSearches.value = await getHotSearches()
  } catch (error) {
    console.error('加载热门搜索词失败:', error)
  }
}

onMounted(() => {
  loadWikiList()
  loadHotSearches()
  
  // 加载搜索历史
  const savedHistory = localStorage.getItem('wiki_search_history')
  if (savedHistory) {
    try {
      searchHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.error('加载搜索历史失败:', e)
    }
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
