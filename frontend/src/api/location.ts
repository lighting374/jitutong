import userAuth from '../services/userAuth'
import auth from '../services/auth'

// 地点相关 API

// 评论数据类型
export interface ReviewComment {
  id: string | number
  userId: string
  userName: string
  userAvatar?: string
  locationId: string
  rating: number // 1-5
  comment: string
  tags?: Array<string>
  images?: Array<string> // 最多9张
  createdAt: string
  updatedAt?: string
  likes?: number
}

// 评论列表响应
export interface ReviewListResponse {
  items: Array<ReviewComment>
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface MyReviewResponse {
  id: string | number
  locationId: string | number
  locationName: string
  rating: number
  comment: string
  createdAt: string
  updatedAt?: string
  wikiId?: number
}

/**
 * 获取当前用户提交的所有评论
 */
export async function getMyReviews(): Promise<MyReviewResponse[]> {
  return request('/my-comments', { method: 'GET' })
}

export interface LocationWikiData {
  id: number
  buildingId?: number // 建筑 ID（后端返回）
  name: string
  address: string
  mainImage: string
  category: string
  latitude?: number // 纬度
  longitude?: number // 经度
  categoryPath: Array<{ name: string; path?: string }>
  richContent: string // HTML 格式的富文本内容
  structuredInfo: {
    openTime?: string
    averageCost?: string
    phone?: string
    website?: string
    building_id?: number // structuredInfo 中也可能包含 building_id
    coordinates?: {
      lat: number
      lng: number
    }
    [key: string]: any
  }
  rating: {
    average: number
    count: number
    distribution: Array<{ stars: number; count: number }>
  }
  comments?: Array<ReviewComment> // 使用新的评论类型（可选，因为评论可能单独获取）
  tags: Array<{
    id: number
    name: string
    color?: string
    count?: number // 热度/使用次数，用于标签云显示
  }>
  canEdit?: boolean // 当前用户是否有编辑权限
}

export interface WikiListItem {
  buildingId: number
  wikiId: number
  name: string
  description: string
  imageUrl: string
  address?: string
  type?: string
  tags?: string[]
  highlights?: string[]
}

export interface WikiListResponse {
  items: WikiListItem[]
  total?: number
  page?: number
  pageSize?: number
}

async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }

  // 🔧 智能 token 选择：
  // - 对于 Wiki 编辑操作（POST/PUT /wiki），优先使用 admin token（Wiki 管理员）
  // - 对于 Wiki 查看（GET），使用普通用户 token 或访客访问
  const method = options.method || 'GET'
  const isWriteOperation = method === 'POST' || method === 'PUT' || method === 'DELETE'
  const isWikiEdit = path.includes('/wiki') && isWriteOperation
  
  let token = null
  if (isWikiEdit) {
    // Wiki 编辑操作：优先使用 admin token
    token = auth.getToken() || userAuth.getToken()
    if (token) {
      console.log('[Location API] Wiki编辑操作，使用管理员 token:', token.substring(0, 20) + '...')
    }
  } else {
    // 查看操作：只使用普通用户 token
    token = userAuth.getToken()
    if (token) {
      console.log('[Location API] 查看操作，使用用户 token:', token.substring(0, 20) + '...')
    }
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  } else {
    console.log('[Location API] 无 token，作为访客访问')
  }

  console.log(`[Location API] ${method} /api/location${path}`)
  const res = await fetch(`/api/location${path}`, { headers, ...options })
  
  console.log(`[Location API] 响应状态: ${res.status} ${res.statusText}`)
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    console.error('[Location API] 请求失败:', { status: res.status, message, error: err })
    const error = new Error(message)
    ;(error as any).status = res.status
    throw error
  }
  return res.json()
}

/**
 * 获取地点 Wiki 详情
 * @param locationId 地点 ID
 */
export async function getLocationWiki(locationId: string | number): Promise<LocationWikiData> {
  return request(`/${locationId}/wiki`, { method: 'GET' })
}

/**
 * 获取 wiki 展示列表
 * @param params 关键字 / 标签过滤
 */
export async function getWikiList(params?: {
  keyword?: string
  tag?: string
  page?: number
  pageSize?: number
}): Promise<WikiListResponse> {
  const search = new URLSearchParams()
  if (params?.keyword) {
    search.set('keyword', params.keyword)
  }
  if (params?.tag) {
    search.set('tag', params.tag)
  }
  if (params?.page) {
    search.set('page', String(params.page))
  }
  if (params?.pageSize) {
    search.set('pageSize', String(params.pageSize))
  }
  const query = search.toString()
  const suffix = query ? `?${query}` : ''
  return request(`/wiki-list${suffix}`, { method: 'GET' })
}

/**
 * 获取地点评论列表
 * @param locationId 地点 ID
 * @param page 页码
 * @param pageSize 每页数量
 * @param tag 可选的标签筛选
 */
export async function getLocationComments(
  locationId: string | number,
  page = 1,
  pageSize = 10,
  tag?: string | null,
): Promise<ReviewListResponse> {
  const params = new URLSearchParams({
    locationId: String(locationId),
    page: String(page),
    pageSize: String(pageSize),
  })
  
  // 如果有标签筛选，添加到参数中
  if (tag) {
    params.append('tag', tag)
  }
  // 使用 /api/reviews 接口
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = userAuth.getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`/api/reviews?${params.toString()}`, { headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    const error = new Error(message)
    ;(error as any).status = res.status
    throw error
  }
  return res.json()
}

/**
 * Wiki 建议提交接口参数
 */
export interface WikiSuggestionData {
  content: string // 建议内容（必填）
  title?: string // 建议标题（可选）
  reason?: string // 修改原因（可选）
}

/**
 * Wiki 建议提交响应
 */
export interface WikiSuggestionResponse {
  success: boolean
  message: string
  suggestionId?: number | string
}

/**
 * 提交 Wiki 建议
 * @param locationId 地点 ID
 * @param suggestion 建议数据
 */
export async function submitWikiSuggestion(
  locationId: string | number,
  suggestion: WikiSuggestionData,
): Promise<WikiSuggestionResponse> {
  return request(`/${locationId}/wiki/suggestion`, {
    method: 'POST',
    body: JSON.stringify(suggestion),
  })
}

/**
 * 创建 Wiki 的数据
 */
export interface CreateWikiData {
  name: string
  address: string
  category?: string
  mainImage?: string
  richContent: string
  structuredInfo?: {
    openTime?: string
    averageCost?: string
    phone?: string
    website?: string
    [key: string]: any
  }
}

/**
 * 更新 Wiki 的数据
 */
export type UpdateWikiData = Partial<CreateWikiData>

/**
 * 创建地点 Wiki
 * @param data Wiki 数据
 */
export async function createLocationWiki(data: CreateWikiData): Promise<LocationWikiData> {
  return request('/wiki', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * 更新地点 Wiki
 * @param locationId 地点 ID
 * @param data Wiki 数据
 */
export async function updateLocationWiki(
  locationId: string | number,
  data: UpdateWikiData,
): Promise<LocationWikiData> {
  return request(`/${locationId}/wiki`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/**
 * 发布评分与评论
 */
export interface SubmitReviewData {
  locationId: number
  rating: number // 1-5
  comment: string
  tags?: Array<string>
  images?: Array<File> // 最多9张
}

export interface SubmitReviewResponse {
  success: boolean
  message: string
  reviewId?: string | number
}

/**
 * 发布评分与评论
 * @param data 评论数据
 */
export async function submitReview(data: SubmitReviewData): Promise<SubmitReviewResponse> {
  // 使用 FormData 来支持文件上传
  const formData = new FormData()
  
  // 添加文本数据
  formData.append('locationId', String(data.locationId))
  formData.append('rating', String(data.rating))
  formData.append('comment', data.comment)
  
  // 添加标签（如果有）
  if (data.tags && data.tags.length > 0) {
    data.tags.forEach(tag => {
      formData.append('tags[]', tag)
    })
  }
  
  // 添加图片文件（如果有）
  if (data.images && data.images.length > 0) {
    data.images.forEach(file => {
      formData.append('images', file)
    })
  }
  
  const headers: Record<string, string> = {}
  const token = userAuth.getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  // 注意：不要设置 Content-Type，让浏览器自动设置 multipart/form-data

  const res = await fetch('/api/reviews', {
    method: 'POST',
    headers,
    body: formData, // 使用 FormData 而不是 JSON.stringify
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    const error = new Error(message)
    ;(error as any).status = res.status
    throw error
  }

  return res.json()
}

/**
 * 获取热门搜索词
 */
export async function getHotSearches(): Promise<string[]> {
  try {
    const response = await fetch('/api/search/hot', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error('获取热门搜索词失败')
    }
    
    const data = await response.json()
    return data.keywords || []
  } catch (error) {
    console.error('获取热门搜索词失败:', error)
    // 返回默认热门搜索词
    return ['图书馆', '食堂', '体育馆', '教学楼', '宿舍', '游泳馆', '艺嘉楼', '智信馆']
  }
}

/**
 * 记录搜索行为
 */
export async function recordSearch(keyword: string): Promise<void> {
  try {
    const token = localStorage.getItem('user_token')
    
    await fetch('/api/search/record', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ keyword }),
    })
    
    // 不需要处理响应，静默记录即可
  } catch (error) {
    // 静默失败，不影响用户体验
    console.debug('记录搜索失败:', error)
  }
}

export default {
  getLocationWiki,
  getWikiList,
  getLocationComments,
  submitWikiSuggestion,
  createLocationWiki,
  updateLocationWiki,
  submitReview,
  getHotSearches,
  recordSearch,
}
