import auth from '../services/auth'

/**
 * 统一的后台管理端请求封装。
 * 会自动附带 `Authorization` header，并在响应异常时抛出带 status 的 Error。
 */
async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = auth.getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`/api/admin${path}`, { headers, ...options })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `请求失败 ${res.status}`
    const error = new Error(message)
    // attach status for caller
    ;(error as any).status = res.status
    throw error
  }
  return res.json()
}

/**
 * GET /api/admin/info
 * 获取当前登录的管理员信息（名称、角色、最近登录时间等）。
 */
export async function getAdminInfo() {
  return request('/info', { method: 'GET' })
}

/**
 * GET /api/admin/stats
 * 仪表盘统计：用户总数、活跃数、封禁数等基础指标。
 */
export async function getStats() {
  return request('/stats', { method: 'GET' })
}

/**
 * GET /api/admin/account/list
 * 查询前台用户账号列表，支持分页与关键字筛选。
 * @param page 页码，默认 1
 * @param pageSize 每页条数，默认 20
 * @param q 模糊搜索关键词
 */
export async function getAccountsList(page = 1, pageSize = 20, q = '') {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  if (q) params.set('q', q)
  return request(`/account/list?${params.toString()}`, { method: 'GET' })
}

/**
 * PUT /api/admin/account/update
 * 更新某个账号的基础资料（昵称、备注、角色等）。
 */
export async function updateAccount(payload: any) {
  return request('/account/update', { method: 'PUT', body: JSON.stringify(payload) })
}

/**
 * POST /api/admin/account/delete
 * 删除指定账号，可携带 hard=true 触发硬删除。
 */
export async function deleteAccount(accountId: string, hard = false) {
  return request('/account/delete', {
    method: 'POST',
    body: JSON.stringify({ id: accountId, hard }),
  })
}

/**
 * POST /api/admin/account/ban
 * 封禁账号，并可附带原因与结束时间。
 */
export async function banAccount(accountId: string, reason?: string, until?: string) {
  return request('/account/ban', {
    method: 'POST',
    body: JSON.stringify({ id: accountId, reason, until }),
  })
}

/**
 * POST /api/admin/account/unban
 * 解除账号封禁。
 */
export async function unbanAccount(accountId: string) {
  return request('/account/unban', { method: 'POST', body: JSON.stringify({ id: accountId }) })
}

/**
 * PUT /api/admin/account/permission
 * 为账号设置角色/权限。
 */
export async function updatePermission(accountId: string, role: string) {
  return request('/account/permission', {
    method: 'PUT',
    body: JSON.stringify({ id: accountId, role }),
  })
}

/**
 * GET /api/admin/account/log
 * 查询账号操作日志（登录、敏感操作等），支持分页。
 */
export async function getAccountLogs(accountId: string, page = 1, pageSize = 50) {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  return request(`/account/log?${params.toString()}&id=${encodeURIComponent(accountId)}`, {
    method: 'GET',
  })
}

// Content review APIs
export async function getContentReviews(
  params: { page?: number; pageSize?: number; status?: string; q?: string; type?: string } = {},
) {
  const { page = 1, pageSize = 20, status = '', q = '', type = 'suggestion' } = params
  const search = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  if (status) search.set('status', status)
  if (q) search.set('keyword', q)
  if (type) search.set('type', type)
  return request(`/content/reviews?${search.toString()}`, { method: 'GET' })
}

export async function getContentReviewDetail(id: string, type = 'suggestion') {
  const params = new URLSearchParams()
  if (type) params.set('type', type)
  return request(`/content/reviews/${id}?${params.toString()}`, { method: 'GET' })
}

export async function approveContentReview(id: string, note?: string, type = 'suggestion') {
  const body = note ? { note } : {}
  const params = new URLSearchParams()
  if (type) params.set('type', type)
  return request(`/content/reviews/${id}/approve?${params.toString()}`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function rejectContentReview(id: string, reason: string, type = 'suggestion') {
  const trimmed = (reason || '').trim()
  const body = trimmed ? { note: trimmed } : {}
  const params = new URLSearchParams()
  if (type) params.set('type', type)
  return request(`/content/reviews/${id}/reject?${params.toString()}`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

// Location management APIs
export async function getLocations(page = 1, pageSize = 20, q = '', status = '', category = '') {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  if (q) params.set('keyword', q)
  if (status) params.set('status', status)
  if (category) params.set('category', category)
  return request(`/locations?${params.toString()}`, { method: 'GET' })
}

export async function createLocation(payload: any) {
  return request('/locations', { method: 'POST', body: JSON.stringify(payload) })
}

export async function updateLocation(id: string, payload: any) {
  return request(`/locations/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
}

export async function deleteLocationRecord(id: string) {
  return request(`/locations/${id}`, { method: 'DELETE' })
}

export async function batchDeleteLocations(ids: string[]) {
  return request('/locations/batch-delete', { method: 'POST', body: JSON.stringify({ ids }) })
}

export async function importLocations(data: any) {
  return request('/locations/import', { method: 'POST', body: JSON.stringify(data) })
}

export async function exportLocations() {
  return request('/locations/export', { method: 'GET' })
}

export async function importLocationsFromFile(file: File) {
  const text = await file.text()
  let payload
  try {
    payload = JSON.parse(text)
  } catch (err) {
    throw new Error('导入文件必须是 JSON 格式')
  }
  if (!payload || typeof payload !== 'object') {
    throw new Error('导入数据结构不正确')
  }
  if (!Array.isArray(payload.items)) {
    throw new Error('JSON 中需要包含 items 数组')
  }
  return importLocations(payload)
}

// System settings
export async function getSystemSettings() {
  return request('/settings/system', { method: 'GET' })
}

export async function updateSystemSettings(payload: any) {
  return request('/settings/system', { method: 'PUT', body: JSON.stringify(payload) })
}

// Analytics
export async function getAnalyticsOverview() {
  return request('/analytics/overview', { method: 'GET' })
}

export async function getAnalyticsUserActivity() {
  return request('/analytics/user-activity', { method: 'GET' })
}

export async function getAnalyticsTopLocations() {
  return request('/analytics/top-locations', { method: 'GET' })
}

export async function getAnalyticsReviewTrends() {
  return request('/analytics/review-trends', { method: 'GET' })
}

export async function getAnalyticsSearchKeywords() {
  return request('/analytics/search-keywords', { method: 'GET' })
}

// Report management APIs
/**
 * GET /api/admin/reports
 * 获取举报列表，支持分页和筛选
 * @param page 页码
 * @param pageSize 每页条数
 * @param status 状态筛选: pending, resolved, dismissed
 * @param type 举报类型: review, reply
 */
export async function getReports(page = 1, pageSize = 20, status = '', type = 'review') {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  if (status) params.set('status', status)
  if (type) params.set('type', type)
  return request(`/reports?${params.toString()}`, { method: 'GET' })
}

/**
 * GET /api/admin/reports/<id>
 * 获取举报详情
 * @param id 举报ID
 * @param type 举报类型: review, reply
 */
export async function getReportDetail(id: string, type = 'review') {
  const params = new URLSearchParams({ type })
  return request(`/reports/${id}?${params.toString()}`, { method: 'GET' })
}

/**
 * POST /api/admin/reports/<id>/resolve
 * 处理举报（认定违规）
 * @param id 举报ID
 * @param type 举报类型: review, reply
 * @param action 处理动作: delete（删除内容）, ban（封禁用户）
 */
export async function resolveReport(id: string, type = 'review', action = 'delete') {
  return request(`/reports/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ type, action }),
  })
}

/**
 * POST /api/admin/account/<id>/avatar
 * 上传用户头像
 * @param userId 用户ID
 * @param file 头像文件
 * @returns 返回头像URL
 */
export async function uploadAvatar(userId: string, file: File) {
  const formData = new FormData()
  formData.append('avatar', file)
  
  const token = auth.getToken()
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  
  const res = await fetch(`/api/admin/account/${userId}/avatar`, {
    method: 'POST',
    headers,
    body: formData,
  })
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const message = err.message || `上传失败 ${res.status}`
    throw new Error(message)
  }
  
  const data = await res.json()
  return data.avatarUrl || data.avatar_url
}

/**
 * POST /api/admin/reports/<id>/dismiss
 * 驳回举报（认定无问题）
 * @param id 举报ID
 * @param type 举报类型: review, reply
 */
export async function dismissReport(id: string, type = 'review') {
  return request(`/reports/${id}/dismiss`, {
    method: 'POST',
    body: JSON.stringify({ type }),
  })
}

// === 评论举报审核 APIs ===
export async function getReviewReports(
  params: { page?: number; pageSize?: number; status?: string } = {},
) {
  const { page = 1, pageSize = 20, status = 'pending' } = params
  const search = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  if (status && status !== 'all') search.set('status', status)
  return request(`/content/review-reports?${search.toString()}`, { method: 'GET' })
}

export async function getReviewReportDetail(id: string) {
  return request(`/content/review-reports/${id}`, { method: 'GET' })
}

export async function resolveReviewReport(id: string, action: string, note?: string) {
  return request(`/content/review-reports/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ action, note }),
  })
}

export async function dismissReviewReport(id: string, reason?: string) {
  return request(`/content/review-reports/${id}/dismiss`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  })
}

export default {
  getAdminInfo,
  getStats,
  getAccountsList,
  updateAccount,
  deleteAccount,
  banAccount,
  unbanAccount,
  updatePermission,
  getAccountLogs,
  uploadAvatar,
  getContentReviews,
  getContentReviewDetail,
  approveContentReview,
  rejectContentReview,
  getLocations,
  createLocation,
  updateLocation,
  deleteLocationRecord,
  batchDeleteLocations,
  importLocations,
  importLocationsFromFile,
  exportLocations,
  getSystemSettings,
  updateSystemSettings,
  getAnalyticsOverview,
  getAnalyticsUserActivity,
  getAnalyticsTopLocations,
  getAnalyticsReviewTrends,
  getAnalyticsSearchKeywords,
  getReports,
  getReportDetail,
  resolveReport,
  dismissReport,
  getReviewReports,
  getReviewReportDetail,
  resolveReviewReport,
  dismissReviewReport,
}
