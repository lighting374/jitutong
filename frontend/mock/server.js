// mock/server.js
import express from 'express'
import bodyParser from 'body-parser'
const app = express()

// 添加 CORS 支持
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  res.header(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept, Authorization',
  )
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200)
  }
  next()
})

// 允许较大的 JSON 负载（例如前端将头像作为 base64 一并提交的临时方案）
app.use(bodyParser.json({ limit: '10mb' }))
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }))

let adminToken = 'mock-admin-token'
let users = []
for (let i = 1; i <= 37; i++) {
  users.push({
    id: String(i),
    username: `user${i}`,
    email: `user${i}@example.com`,
    phone: `1380000${String(i).padStart(4, '0')}`,
    status: 'active',
    role: 'user',
  })
}
users[2].status = 'banned'

const clientUsers = [
  {
    id: 'u1',
    phone: '13275786780',
    password: '123456',
    nickname: '嘉定行者',
    avatar: '/avatar.jpg',
    bio: '热爱探索嘉定校区的每个角落',
    gender: 'unknown',
  },
  {
    id: 'u2',
    phone: '13800000002',
    password: '123456',
    nickname: '同济同学',
    avatar: '/avatar2.jpg',
    bio: '喜欢在校园里发现美好',
    gender: 'unknown',
  },
]

const userFavorites = {
  u1: [10, 12],
  u2: [11],
}

const userSessions = new Map()

const buildingCatalog = {
  1: {
    buildingId: 1,
    wikiId: 1001,
    name: '教学楼A楼',
    description: '教学区核心教学楼，配备多媒体教室与实验室，支撑大一大二公共课程。',
    imageUrl: '/图书馆材料学院.jpg',
    address: '嘉定校区教学区',
    type: '教学楼',
    tags: ['教学楼', '多媒体', '公共课'],
    highlights: ['多媒体教室', '课间自习空间', '靠近主干道'],
  },
  10: {
    buildingId: 10,
    wikiId: 103,
    name: '嘉定校区图书馆',
    description: '现代化学习空间，涵盖建筑、土木、材料等专业的丰富藏书与电子资源。',
    imageUrl: '/图书馆材料学院.jpg',
    address: '上海市嘉定区曹安公路4800号同济大学嘉定校区',
    type: '学习场所',
    tags: ['图书馆', '学习', '安静'],
    highlights: ['自习室全天开放', '电子阅览室', '支持线上预约座位'],
  },
  11: {
    buildingId: 11,
    wikiId: 201,
    name: '嘉定校区游泳馆',
    description: '配备标准泳池与健身设施的综合运动中心，开放教学与自由锻炼时段。',
    imageUrl: '/嘉定校区游泳馆.jpg',
    address: '上海市嘉定区曹安公路4800号同济大学嘉定校区',
    type: '运动场所',
    tags: ['运动', '游泳', '健身'],
    highlights: ['50 米标准泳池', '可预约课程', '带有更衣淋浴区'],
  },
  12: {
    buildingId: 12,
    wikiId: 305,
    name: '艺嘉楼',
    description: '集艺术展览、公共讲座与课程教学于一体的多功能教学楼。',
    imageUrl: '/艺嘉楼.jpg',
    address: '上海市嘉定区曹安公路4800号同济大学嘉定校区',
    type: '教学楼',
    tags: ['艺术', '展览', '课程'],
    highlights: ['定期艺术展览', '多媒体教室', '公共讲座空间'],
  },
}

const wikiDetailStore = {
  103: {
    structuredInfo: {
      openTime: '周一至周日 08:00-22:00',
      averageCost: '免费',
      phone: '021-69585000',
      website: 'https://lib.tongji.edu.cn',
      coordinates: { lat: 31.2857, lng: 121.2088 },
    },
    richContent: `
      <h2>图书馆简介</h2>
      <p>同济大学嘉定校区图书馆是一座现代化的学术建筑，为师生提供丰富的学习资源与舒适的学习环境。</p>
      <h3>馆藏资源</h3>
      <ul>
        <li>纸质图书：超过 100 万册</li>
        <li>电子资源：数十个数据库与电子期刊</li>
        <li>专业资料：涵盖建筑、土木、材料等热门方向</li>
      </ul>
      <h3>特色服务</h3>
      <p>提供座位预约、学术讲座、参考咨询、打印复印等服务。</p>
    `,
    rating: {
      average: 4.6,
      count: 128,
      distribution: [
        { stars: 5, count: 82 },
        { stars: 4, count: 30 },
        { stars: 3, count: 11 },
        { stars: 2, count: 3 },
        { stars: 1, count: 2 },
      ],
    },
    tags: [
      { id: 1, name: '图书馆', color: '#5368df', count: 120 },
      { id: 2, name: '学习', color: '#34c759', count: 98 },
      { id: 3, name: '安静', color: '#fa5757', count: 85 },
    ],
  },
  201: {
    structuredInfo: {
      openTime: '周二至周日 09:00-21:30（周一维护）',
      averageCost: '学生 10 元/次',
      phone: '021-69586000',
      website: 'https://sports.tongji.edu.cn',
      coordinates: { lat: 31.2842, lng: 121.2099 },
    },
    richContent: `
      <h2>游泳馆简介</h2>
      <p>泳池采用恒温系统，并配备专业救生团队，提供课程教学与自由泳时段。</p>
      <h3>设施亮点</h3>
      <ul>
        <li>50 米标准泳池与训练池</li>
        <li>专业更衣、淋浴与寄存柜</li>
        <li>配套力量训练区与康复设备</li>
      </ul>
      <h3>使用须知</h3>
      <p>入馆需携带校园卡或临时体验票，建议提前线上预约。</p>
    `,
    rating: {
      average: 4.3,
      count: 56,
      distribution: [
        { stars: 5, count: 30 },
        { stars: 4, count: 18 },
        { stars: 3, count: 6 },
        { stars: 2, count: 1 },
        { stars: 1, count: 1 },
      ],
    },
    tags: [
      { id: 4, name: '运动', color: '#34c759', count: 60 },
      { id: 5, name: '游泳', color: '#16a085', count: 52 },
    ],
  },
  305: {
    structuredInfo: {
      openTime: '周一至周五 08:30-21:00，周末 10:00-18:00',
      averageCost: '免费',
      phone: '021-69587000',
      website: 'https://art.tongji.edu.cn',
      coordinates: { lat: 31.2861, lng: 121.2065 },
    },
    richContent: `
      <h2>艺嘉楼亮点</h2>
      <p>常设多媒体展厅、公共讲座厅与实验教室，是校园艺术文化活动的核心场所。</p>
      <h3>常设空间</h3>
      <ul>
        <li>一层公共展厅：对外开放主题展览</li>
        <li>二层互动教室：开展艺术实践课程</li>
        <li>三层报告厅：举办艺术讲座与论坛</li>
      </ul>
      <h3>活动推荐</h3>
      <p>关注学院公众号即可查看最新展览及讲座安排，部分活动需提前预约。</p>
    `,
    rating: {
      average: 4.7,
      count: 64,
      distribution: [
        { stars: 5, count: 40 },
        { stars: 4, count: 20 },
        { stars: 3, count: 3 },
        { stars: 2, count: 1 },
        { stars: 1, count: 0 },
      ],
    },
    tags: [
      { id: 6, name: '艺术', color: '#9b59b6', count: 70 },
      { id: 7, name: '展览', color: '#ff9500', count: 45 },
    ],
  },
}

const locationReviewStore = {
  10: [
    {
      id: 'rv-10-1',
      userId: 'u1',
      locationId: 103,
      buildingId: 10,
      rating: 5,
      comment: '图书馆很安静，预约座位也方便，备考好去处。',
      createdAt: new Date().toISOString(),
    },
  ],
  11: [
    {
      id: 'rv-11-1',
      userId: 'u2',
      locationId: 201,
      buildingId: 11,
      rating: 4,
      comment: '水质干净，下午人较多，建议错峰。',
      createdAt: new Date().toISOString(),
    },
  ],
  12: [
    {
      id: 'rv-12-1',
      userId: 'u1',
      locationId: 305,
      buildingId: 12,
      rating: 5,
      comment: '展览很有意思，适合拍照打卡。',
      createdAt: new Date().toISOString(),
    },
  ],
}

let contentReviews = Array.from({ length: 12 }).map((_, idx) => {
  const status = idx % 3 === 0 ? 'approved' : idx % 3 === 1 ? 'pending' : 'rejected'
  return {
    id: `rv-${idx + 1}`,
    title: `地点评论审核 #${idx + 1}`,
    type: idx % 2 === 0 ? '评论' : '地点内容',
    status,
    submittedBy: `user${idx + 1}`,
    submittedAt: new Date(Date.now() - idx * 3600 * 1000).toISOString(),
    payload: {
      locationId: String((idx % 5) + 1),
      locationName: ['图书馆', '游泳馆', '体操馆', '艺嘉楼', '材料学院'][idx % 5],
      content: idx % 2 === 0 ? `这是一条待审核的评论 ${idx + 1}` : `地点描述变更申请 ${idx + 1}`,
      attachments: [],
    },
    reviewerNote: '',
    reviewedAt: status === 'pending' ? null : new Date(Date.now() - idx * 2000).toISOString(),
  }
})

let systemSettings = {
  allowRegistration: true,
  autoAssignReview: false,
  retentionDays: 90,
  enableNotification: true,
  mapDefaultCampus: '嘉定校区',
}
const userHistories = {
  u1: [
    {
      id: 'h1',
      buildingId: 10,
      wikiId: 103,
      name: '嘉定校区图书馆',
      lastVisited: '2025-10-29 10:30',
      imageUrl: '/图书馆材料学院.jpg',
    },
    {
      id: 'h2',
      buildingId: 12,
      wikiId: 305,
      name: '艺嘉楼',
      lastVisited: '2025-10-28 17:15',
      imageUrl: '/艺嘉楼.jpg',
    },
  ],
  u2: [
    {
      id: 'h3',
      buildingId: 11,
      wikiId: 201,
      name: '嘉定校区游泳馆',
      lastVisited: '2025-10-20 09:10',
      imageUrl: '/嘉定校区游泳馆.jpg',
    },
  ],
}
const userMessages = {
  u1: [
    {
      id: 'm1',
      type: 'comment_reply',
      content: 'tsy 回复了你对 “嘉定校区图书馆” 的评论。',
      date: '2小时前',
      read: false,
      link: '/location/103#comment-54',
    },
    {
      id: 'm2',
      type: 'like',
      content: '大橘点赞了你的评论 “自习室很安静...”',
      date: '5小时前',
      read: false,
      link: '/location/103#comment-50',
    },
    {
      id: 'm3',
      type: 'system',
      content: '欢迎使用“济图通”，祝你探索愉快！',
      date: '2天前',
      read: true,
      link: null,
    },
  ],
  u2: [
    {
      id: 'm4',
      type: 'system',
      content: 'Hi 嘉定行者，快去看看新增的地图打点吧。',
      date: '1天前',
      read: false,
      link: '/map',
    },
  ],
}

const sanitizeUser = (user) => {
  if (!user) return null
  const { password, ...rest } = user
  return rest
}

const createUserSession = (userId) => {
  const token = `user-mock-token-${userId}-${Date.now()}`
  const expiresAt = Date.now() + 2 * 60 * 60 * 1000 // 2 小时
  userSessions.set(token, { userId, expiresAt })
  return { token, expiresIn: 7200 }
}

const authenticateUser = (req, res, next) => {
  const authHeader = req.headers.authorization || ''
  if (!authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: '未登录或凭证缺失' })
  }
  const token = authHeader.replace('Bearer ', '')
  const session = userSessions.get(token)
  if (!session) {
    return res.status(401).json({ message: '登录状态已失效，请重新登录' })
  }
  if (session.expiresAt < Date.now()) {
    userSessions.delete(token)
    return res.status(401).json({ message: '登录状态已过期，请重新登录' })
  }
  const user = clientUsers.find((u) => u.id === session.userId)
  if (!user) {
    return res.status(401).json({ message: '用户不存在' })
  }
  req.user = user
  req.token = token
  next()
}

/**
 * @route POST /api/admin/login
 * @desc 管理后台登录（mock 固定账号 admin/password）
 * @body { username: string, password: string }
 * @returns { token, expiresIn, user }
 */
app.post('/api/admin/login', (req, res) => {
  const { username, password } = req.body
  if (username === 'admin' && password === 'password') {
    return res.json({
      token: adminToken,
      expiresIn: 3600,
      user: { id: '0', name: '管理员', role: 'admin', lastLogin: new Date().toISOString() },
    })
  }
  return res.status(401).json({ message: '用户名或密码错误' })
})

/**
 * @route GET /api/admin/info
 * @auth Authorization: Bearer <token>
 * @desc 获取当前管理员基本信息
 * @returns { id, name, role, lastLogin }
 */
app.get('/api/admin/info', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  res.json({ id: '0', name: '管理员', role: 'admin', lastLogin: new Date().toISOString() })
})
/**
 * @route GET /api/admin/stats
 * @auth Authorization: Bearer <token>
 * @desc 仪表盘概览（用户总量/活跃/封禁数）
 */
app.get('/api/admin/stats', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  res.json({
    totalUsers: users.length,
    activeUsers: users.filter((u) => u.status === 'active').length,
    bannedUsers: users.filter((u) => u.status === 'banned').length,
  })
})

/**
 * @route GET /api/admin/account/list
 * @query page=1&pageSize=10
 * @auth Authorization: Bearer <token>
 * @desc 分页查询前台账号列表
 */
app.get('/api/admin/account/list', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const page = parseInt(req.query.page || '1', 10)
  const pageSize = parseInt(req.query.pageSize || '10', 10)
  const start = (page - 1) * pageSize
  res.json({ items: users.slice(start, start + pageSize), total: users.length })
})

/**
 * @route PUT /api/admin/account/update
 * @auth Authorization: Bearer <token>
 * @body { id: string, ...fields }
 * @desc 修改账号的基础资料（昵称/备注等）
 */
app.put('/api/admin/account/update', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const payload = req.body
  const idx = users.findIndex((u) => u.id === payload.id)
  if (idx === -1) return res.status(404).json({ message: '用户不存在' })
  users[idx] = { ...users[idx], ...payload }
  res.json({ success: true, user: users[idx] })
})

/**
 * @route POST /api/admin/account/delete
 * @auth Authorization: Bearer <token>
 * @body { id: string }
 * @desc 删除（软删）指定账号
 */
app.post('/api/admin/account/delete', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const { id } = req.body
  users = users.filter((u) => u.id !== id)
  res.json({ success: true })
})

/**
 * @route POST /api/admin/account/ban
 * @auth Authorization: Bearer <token>
 * @body { id: string }
 * @desc 将账号状态置为 banned
 */
app.post('/api/admin/account/ban', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const { id } = req.body
  const u = users.find((x) => x.id === id)
  if (u) u.status = 'banned'
  res.json({ success: true })
})
/**
 * @route POST /api/admin/account/unban
 * @auth Authorization: Bearer <token>
 * @body { id: string }
 * @desc 恢复账号为 active 状态
 */
app.post('/api/admin/account/unban', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const { id } = req.body
  const u = users.find((x) => x.id === id)
  if (u) u.status = 'active'
  res.json({ success: true })
})

/**
 * @route PUT /api/admin/account/permission
 * @auth Authorization: Bearer <token>
 * @body { id: string, role: string }
 * @desc 修改账号角色/权限
 */
app.put('/api/admin/account/permission', (req, res) => {
  if (!ensureAuthorized(req, res)) return
  const { id, role } = req.body
  const u = users.find((x) => x.id === id)
  if (u) u.role = role
  res.json({ success: true })
})

// 管理员查看单个账号的行为日志，支持简单分页
app.get('/api/admin/account/log', (req, res) => {
    if (!ensureAuthorized(req, res)) return
    const id = req.query.id
    if (!id) return res.status(400).json({ message: '缺少用户 ID' })

    const page = parseInt(req.query.page || '1', 10)
    const pageSize = parseInt(req.query.pageSize || '10', 10)

    // 模拟该账号的一些典型操作日志
    const baseTime = Date.now()
    const allLogs = [{
            timestamp: new Date(baseTime - 1 * 60 * 60 * 1000).toISOString(),
            action: 'login',
            detail: `用户 ${id} 登录系统`,
        },
        {
            timestamp: new Date(baseTime - 2 * 60 * 60 * 1000).toISOString(),
            action: 'update_profile',
            detail: `用户 ${id} 修改了个人资料`,
        },
        {
            timestamp: new Date(baseTime - 3 * 60 * 60 * 1000).toISOString(),
            action: 'browse_location',
            detail: `用户 ${id} 浏览了地点详情：嘉定图书馆`,
        },
        {
            timestamp: new Date(baseTime - 4 * 60 * 60 * 1000).toISOString(),
            action: 'favorite_location',
            detail: `用户 ${id} 收藏了地点：游泳馆`,
        },
        {
            timestamp: new Date(baseTime - 5 * 60 * 60 * 1000).toISOString(),
            action: 'unfavorite_location',
            detail: `用户 ${id} 取消收藏地点：游泳馆`,
        },
        {
            timestamp: new Date(baseTime - 6 * 60 * 60 * 1000).toISOString(),
            action: 'send_feedback',
            detail: `用户 ${id} 提交了一条反馈`,
        },
        {
            timestamp: new Date(baseTime - 7 * 60 * 60 * 1000).toISOString(),
            action: 'login',
            detail: `用户 ${id} 登录系统`,
        },
        {
            timestamp: new Date(baseTime - 8 * 60 * 60 * 1000).toISOString(),
            action: 'logout',
            detail: `用户 ${id} 退出登录`,
        },
    ]

    // 按时间倒序
    allLogs.sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1))

    const start = (page - 1) * pageSize
    const items = allLogs.slice(start, start + pageSize)

    res.json({ items, total: allLogs.length })
})

/**
 * @route GET /api/user/favorites
 * @auth Authorization: Bearer <token>
 * @desc 返回收藏地点详情列表
 */
app.get('/api/user/favorites', authenticateUser, (req, res) => {
  const ids = userFavorites[req.user.id] || []
  const items = ids.map((id) => buildingCatalog[id]).filter(Boolean)
  res.json({ items })
})

/**
 * @route POST /api/user/favorites
 * @auth Authorization: Bearer <token>
 * @body { buildingId: number }
 * @desc 新增收藏，返回被收藏的地点信息
 */
app.post('/api/user/favorites', authenticateUser, (req, res) => {
  const { buildingId } = req.body || {}
  if (!buildingId) {
    return res.status(400).json({ message: 'buildingId 必填' })
  }
  const numericId = Number(buildingId)
  const info = buildingCatalog[numericId]
  if (!info) {
    return res.status(404).json({ message: '建筑不存在' })
  }
  const list = userFavorites[req.user.id] || (userFavorites[req.user.id] = [])
  if (!list.includes(numericId)) {
    list.push(numericId)
  }
  res.json({ success: true, item: info })
})

/**
 * @route DELETE /api/user/favorites/:buildingId
 * @auth Authorization: Bearer <token>
 * @desc 按地点 ID 移除收藏
 */
app.delete('/api/user/favorites/:buildingId', authenticateUser, (req, res) => {
  const numericId = Number(req.params.buildingId)
  const list = userFavorites[req.user.id] || (userFavorites[req.user.id] = [])
  const idx = list.indexOf(numericId)
  if (idx !== -1) {
    list.splice(idx, 1)
  }
  res.json({ success: true })
})

/**
 * @route GET /api/user/favorites/status
 * @auth Authorization: Bearer <token>
 * @query buildingId? | wikiId?
 * @desc 查询是否已收藏某地点
 */
app.get('/api/user/favorites/status', authenticateUser, (req, res) => {
  let targetId = req.query.buildingId ? Number(req.query.buildingId) : undefined
  if (!targetId && req.query.wikiId) {
    const matched = Object.values(buildingCatalog).find(
      (item) => String(item.wikiId) === String(req.query.wikiId),
    )
    targetId = matched ? matched.buildingId : undefined
  }
  if (!targetId) {
    return res.json({ favorited: false })
  }
  const list = userFavorites[req.user.id] || []
  res.json({ favorited: list.includes(targetId) })
})

// Location Wiki API

/**
 * @route GET /api/location/wiki-list
 * @query keyword? tag?
 * @desc 获取 Wiki 展示列表
 */
app.get('/api/location/wiki-list', (req, res) => {
  try {
    const keyword = String(req.query.keyword || '')
      .trim()
      .toLowerCase()
    const tag = String(req.query.tag || '').trim()

    let items = Object.values(buildingCatalog).map((info) => ({
      buildingId: info.buildingId,
      wikiId: info.wikiId,
      name: info.name,
      description: info.description,
      imageUrl: info.imageUrl,
      address: info.address,
      type: info.type,
      tags: info.tags,
      highlights: info.highlights,
    }))

    if (keyword) {
      items = items.filter((item) => {
        const content = `${item.name}${item.description}${item.address}`.toLowerCase()
        return content.includes(keyword)
      })
    }

    if (tag) {
      items = items.filter((item) => item.tags?.includes(tag))
    }

    res.json({ items })
  } catch (error) {
    console.error('获取 Wiki 列表错误:', error)
    res.status(500).json({ message: '获取 Wiki 列表失败', error: error.message })
  }
})

/**
 * @route GET /api/location/:id/wiki
 * @desc 获取地点 Wiki 详情（富文本、结构化信息、标签、示例评论）
 * @returns LocationWikiData mock
 */
app.get('/api/location/:id/wiki', (req, res) => {
  try {
    const wikiId = Number(req.params.id)
    const target = Object.values(buildingCatalog).find(
      (item) => item.wikiId === wikiId || item.buildingId === wikiId,
    )
    if (!target) {
      return res.status(404).json({ message: `未找到 ID 为 ${wikiId} 的 Wiki` })
    }

    const detail = wikiDetailStore[target.wikiId] || {}
    const response = {
      id: target.wikiId,
      wikiId: target.wikiId,
      name: target.name,
      address: target.address,
      mainImage: target.imageUrl,
      category: target.type || '校园地点',
      categoryPath: [
        { name: '首页', path: '/' },
        { name: target.type || '校园地点', path: '/wiki' },
        { name: target.name },
      ],
      richContent:
        detail.richContent ||
        `<p>${target.description}</p>

        <p>欢迎前往 ${target.name} 探索它的更多故事。</p>`,
      structuredInfo: detail.structuredInfo || {},
      rating: detail.rating || {
        average: 4.5,
        count: 20,
        distribution: [
          { stars: 5, count: 12 },
          { stars: 4, count: 6 },
          { stars: 3, count: 2 },
          { stars: 2, count: 0 },
          { stars: 1, count: 0 },
        ],
      },
      comments: (locationReviewStore[target.buildingId] || []).map((review) => ({
        id: review.id,
        userId: review.userId,
        userName: review.userId === 'u1' ? '嘉定行者' : '同济同学',
        userAvatar: '/avatar.jpg',
        rating: review.rating,
        content: review.comment,
        createdAt: review.createdAt,
        likes: 5,
      })),
      tags: detail.tags || target.tags?.map((name, index) => ({ id: index + 1, name })) || [],
      canEdit: true,
    }
    res.json(response)
  } catch (error) {
    console.error('获取 Wiki 数据错误:', error)
    res.status(500).json({ message: '获取 Wiki 数据失败', error: error.message })
  }
})

// 提交 Wiki 建议

/**
 * @route POST /api/location/:id/wiki/suggestion
 * @body { content: string, title?: string, reason?: string }
 * @desc 提交地点 Wiki 的修改建议
 */
app.post('/api/location/:id/wiki/suggestion', (req, res) => {
  const locationId = req.params.id
  const { content, title, reason } = req.body

  // 验证必填字段
  if (!content) {
    return res.status(400).json({ message: '建议内容不能为空' })
  }

  // 模拟保存建议
  console.log(`收到地点 ${locationId} 的 Wiki 建议:`, { content, title, reason })

  // 返回成功响应
  res.json({
    success: true,
    message: '建议提交成功，我们会尽快审核',
    suggestionId: Date.now(), // 模拟返回的建议ID
  })
})

// 获取评论列表 GET /api/reviews?locationId=xxx&page=1&pageSize=10

/**
 * @route GET /api/reviews
 * @query locationId, page?, pageSize?
 * @desc 获取地点评论列表（带分页信息）
 */
app.get('/api/reviews', (req, res) => {
  try {
    const locationId = req.query.locationId
    const page = parseInt(req.query.page || '1', 10)
    const pageSize = parseInt(req.query.pageSize || '10', 10)

    if (!locationId) {
      return res.status(400).json({ message: 'locationId 参数必填' })
    }

    // 模拟评论数据
    const mockComments = [
      {
        id: 1,
        userId: '1',
        userName: '学霸小李',
        userAvatar: '/avatar.jpg',
        locationId: locationId,
        rating: 5,
        comment: '环境非常好，座位充足，学习氛围浓厚。电子资源也很丰富，强烈推荐！',
        tags: ['环境好', '推荐'],
        images: ['/图书馆材料学院.jpg'],
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        likes: 15,
      },
      {
        id: 2,
        userId: '2',
        userName: '爱学习的小张',
        userAvatar: '/avatar.jpg',
        locationId: locationId,
        rating: 4,
        comment: '整体不错，但考试周人太多了，建议提前预约。',
        tags: ['人多', '需预约'],
        images: ['/嘉定校区游泳馆.jpg', '/艺嘉楼.jpg'],
        createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        likes: 8,
      },
      {
        id: 3,
        userId: '3',
        userName: '阅读爱好者',
        userAvatar: '/avatar.jpg',
        locationId: locationId,
        rating: 5,
        comment: '馆藏丰富，尤其是建筑和材料相关的书籍，非常专业。工作人员态度也很好。',
        tags: ['馆藏丰富', '服务好'],
        images: [],
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        likes: 12,
      },
      {
        id: 4,
        userId: '4',
        userName: '学习达人',
        userAvatar: '/avatar.jpg',
        locationId: locationId,
        rating: 5,
        comment: '自习环境很棒，WiFi速度也很快，很适合学习。唯一就是需要早点来占座位。',
        tags: ['环境好', 'WiFi快'],
        images: ['/图书馆材料学院.jpg'],
        createdAt: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
        likes: 20,
      },
      {
        id: 5,
        userId: '5',
        userName: '图书馆常客',
        userAvatar: '/avatar.jpg',
        locationId: locationId,
        rating: 4,
        comment: '设施齐全，座位舒适。只是有时候会有点吵，建议选择靠窗的位置。',
        tags: ['设施齐全'],
        images: ['/艺嘉楼.jpg'],
        createdAt: new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString(),
        likes: 6,
      },
    ]

    // 分页逻辑
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedComments = mockComments.slice(startIndex, endIndex)
    const total = mockComments.length
    const totalPages = Math.ceil(total / pageSize)

    res.json({
      items: paginatedComments,
      total: total,
      page: page,
      pageSize: pageSize,
      totalPages: totalPages,
    })
  } catch (error) {
    console.error('获取评论列表错误:', error)
    res.status(500).json({ message: '获取评论列表失败', error: error.message })
  }
})

// 发布评分与评论 POST /api/reviews

/**
 * @route POST /api/reviews
 * @body { userId, locationId, rating(1-5), comment, tags?, images? }
 * @desc 发布评分与评论，返回 { success, message, reviewId }
 */
app.post('/api/reviews', (req, res) => {
  try {
    const { userId, locationId, rating, comment, tags, images } = req.body

    // 验证必填字段
    if (!userId) {
      return res.status(400).json({ message: 'userId 参数必填' })
    }
    if (!locationId) {
      return res.status(400).json({ message: 'locationId 参数必填' })
    }
    if (!rating || rating < 1 || rating > 5) {
      return res.status(400).json({ message: 'rating 参数必填，且范围在 1-5 之间' })
    }
    if (!comment) {
      return res.status(400).json({ message: 'comment 参数必填' })
    }
    if (images && images.length > 9) {
      return res.status(400).json({ message: 'images 最多9张' })
    }

    // 模拟保存评论
    console.log(`收到地点 ${locationId} 的评论:`, {
      userId,
      rating,
      comment,
      tags,
      images,
    })

    // 返回成功响应
    res.json({
      success: true,
      message: '评论发布成功',
      reviewId: Date.now(), // 模拟返回的评论ID
    })
  } catch (error) {
    console.error('发布评论错误:', error)
    res.status(500).json({ message: '发布评论失败', error: error.message })
  }
})

// 404 处理
app.use((req, res) => {
  res.status(404).json({ message: `接口不存在: ${req.method} ${req.path}` })
})

// 错误处理中间件（必须放在最后）
app.use((err, req, res, next) => {
  console.error('服务器错误:', err)
  res.status(500).json({ message: '服务器内部错误', error: err.message })
})

app.listen(4000, () => {
  console.log('Mock server running at http://localhost:4000')
  console.log('可用的接口:')
  console.log('  GET  /api/location/:id/wiki')
  console.log('  POST /api/location/:id/wiki/suggestion')
  console.log('  POST /api/location/wiki (创建 Wiki)')
  console.log('  PUT  /api/location/:id/wiki (更新 Wiki)')
  console.log('  GET  /api/reviews?locationId=xxx&page=1&pageSize=10 (获取评论列表)')
  console.log('  POST /api/reviews (发布评分与评论)')
})