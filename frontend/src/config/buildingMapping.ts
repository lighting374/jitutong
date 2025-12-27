export interface BuildingInfo {
  id: number
  wikiId?: number
  name: string
  description: string
  imageUrl: string
  type?: string
}

/**
 * 建筑基础信息。这里先放常用的几个地点，后续可按需扩展。
 * 图片路径可直接复用 public 目录下已经存在的示例图片。
 */
export const buildingsInfo: Record<number, BuildingInfo> = {
  1: {
    id: 1,
    wikiId: 1,
    name: '教学楼A楼',
    description: '教学区核心教学楼，配备多媒体教室与实验室。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  10: {
    id: 10,
    wikiId: 10,  // Building ID = Wiki ID
    name: '嘉定校区图书馆',
    description: '现代化学习空间，涵盖建筑、土木、材料等专业的丰富藏书与电子资源。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '学习场所',
  },
  33: {
    id: 33,
    wikiId: 33,  // Building ID = Wiki ID
    name: '嘉定校区游泳馆',
    description: '配备标准泳池与健身设施的综合运动场所，提供教学与开放时段。',
    imageUrl: '/嘉定校区游泳馆.jpg',
    type: '运动场所',
  },
  34: {
    id: 34,
    wikiId: 34,  // Building ID = Wiki ID
    name: '艺嘉楼',
    description: '集艺术展览与授课活动于一体的多功能教学楼，常设主题展览。',
    imageUrl: '/艺嘉楼.jpg',
    type: '教学楼',
  },
  35: {
    id: 35,
    wikiId: 35,
    name: '智信馆',
    description: '智能信息技术教学与研究中心。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  36: {
    id: 36,
    wikiId: 36,
    name: '材料科学与工程学院',
    description: '材料科学与工程学院教学楼。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  37: {
    id: 37,
    wikiId: 37,
    name: '机械与能源工程学院',
    description: '机械与能源工程学院教学楼。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  38: {
    id: 38,
    wikiId: 38,
    name: '交通运输工程学院',
    description: '交通运输工程学院教学楼。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  39: {
    id: 39,
    wikiId: 39,
    name: '校医院',
    description: '校区医疗服务中心。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '医疗设施',
  },
  40: {
    id: 40,
    wikiId: 40,
    name: '汽车学院',
    description: '汽车学院教学与研究中心。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
  41: {
    id: 41,
    wikiId: 41,
    name: '艺术与传媒学院',
    description: '艺术与传媒学院教学楼。',
    imageUrl: '/图书馆材料学院.jpg',
    type: '教学楼',
  },
}

/**
 * 建筑 ID -> Wiki 页面 ID 的映射。
 * 如果某个建筑尚未录入 wiki，可保持 undefined，前端会回退成使用建筑 ID。
 */
export const buildingToWikiMap: Record<number, number> = Object.entries(buildingsInfo).reduce(
  (acc, [, info]) => {
    if (info.wikiId) {
      acc[info.id] = info.wikiId
    }
    return acc
  },
  {} as Record<number, number>,
)

/**
 * 根据建筑 ID 获取对应 Wiki ID，如果未配置则返回 undefined。
 */
export const getWikiIdFromBuildingId = (buildingId: number): number | undefined => {
  return buildingToWikiMap[buildingId] ?? buildingsInfo[buildingId]?.wikiId
}

/**
 * 反查：根据 Wiki ID 找到建筑 ID。
 * 由于现在 Building ID = Wiki ID，直接返回即可。
 */
export const getBuildingIdFromWikiId = (wikiId: number): number | undefined => {
  // Building ID = Wiki ID，直接返回
  return wikiId
}
