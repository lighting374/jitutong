# 地图建筑数据 API 文档

## 接口概述

前端地图页面需要从后端动态获取所有建筑的位置信息，用于在地图上显示标记点。

---

## API 规范

### 接口地址

```
GET /api/location/map-buildings
```

### 请求参数

无需参数（获取所有已发布的地点）

### 请求示例

```bash
GET http://192.168.3.197:5000/api/location/map-buildings
```

---

## 响应格式

### 成功响应

**HTTP 状态码**: `200 OK`

**响应体**:

```json
{
  "buildings": [
    {
      "id": 1,
      "name": "图书馆",
      "type": "图书馆",
      "position": [121.212345, 31.287654],
      "description": "嘉定校区图书馆，提供丰富的学习资源",
      "openTime": "8:00-22:00",
      "address": "上海市嘉定区曹安公路4800号",
      "phone": "021-69580000",
      "facilities": ["自习室", "电子阅览室", "讨论室"],
      "mainImage": "/uploads/library.jpg",
      "wikiId": 10
    },
    {
      "id": 2,
      "name": "A楼",
      "type": "教学楼",
      "position": [121.213781, 31.285920],
      "description": "教学楼A楼",
      "openTime": "7:00-22:00",
      "address": "教学区",
      "phone": "",
      "facilities": ["教室", "办公室"],
      "mainImage": "/uploads/building-a.jpg",
      "wikiId": 1
    }
  ],
  "total": 34
}
```

---

## 字段说明

### 根对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `buildings` | Array | 是 | 建筑列表 |
| `total` | Integer | 是 | 建筑总数 |

### buildings 数组中的对象

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `id` | Integer | 是 | 建筑ID（Building ID） | `1` |
| `name` | String | 是 | 建筑名称 | `"图书馆"` |
| `type` | String | 是 | 建筑类型 | `"图书馆"`, `"教学楼"`, `"食堂"`, `"宿舍"`, `"体育设施"` 等 |
| `position` | Array[Number] | **是** | **经纬度坐标 [经度, 纬度]** | `[121.212345, 31.287654]` |
| `description` | String | 否 | 建筑描述（简短） | `"嘉定校区图书馆"` |
| `openTime` | String | 否 | 开放时间 | `"8:00-22:00"`, `"全天开放"` |
| `address` | String | 否 | 详细地址 | `"上海市嘉定区曹安公路4800号"` |
| `phone` | String | 否 | 联系电话 | `"021-69580000"` |
| `facilities` | Array[String] | 否 | 设施列表 | `["自习室", "电子阅览室"]` |
| `mainImage` | String | 否 | 主图片路径 | `"/uploads/library.jpg"` |
| `wikiId` | Integer | 是 | Wiki 页面 ID（用于跳转） | `10` |

---

## 重要说明

### 1. 经纬度格式 ⚠️

**`position` 字段格式**: `[经度, 纬度]`

- **经度（longitude）**: 数组第一个元素，范围 -180 ~ 180
- **纬度（latitude）**: 数组第二个元素，范围 -90 ~ 90
- **示例**: `[121.212345, 31.287654]` 表示经度 121.212345，纬度 31.287654

**注意**: 
- 必须是数字类型，不能是字符串
- 必须是两个元素的数组
- 如果某个地点没有经纬度，请不要返回该地点（前端会自动过滤）

### 2. 数据来源

建议从数据库 `locations` 表中获取：
- 经纬度存储在 `structured_info` 字段的 `position` 属性中
- 只返回 `status = 'published'` 的地点
- 过滤掉没有经纬度的地点

### 3. Building ID 与 Wiki ID

- **Building ID** (`id`): 建筑的唯一标识，用于地图标记
- **Wiki ID** (`wikiId`): 对应的 Wiki 页面 ID，用于点击跳转

在当前系统中，这两个 ID 通常是相同的。

---

## 数据库查询参考

如果使用 SQLAlchemy（Python）：

```python
@location_bp.route('/map-buildings', methods=['GET'])
def get_map_buildings():
    # 查询所有已发布的地点
    locations = Location.query.filter_by(status='published').all()
    
    buildings = []
    for loc in locations:
        structured_info = loc.structured_info or {}
        position = structured_info.get('position')
        
        # 如果没有经纬度，跳过该地点
        if not position or not isinstance(position, list) or len(position) != 2:
            continue
        
        building_data = {
            'id': loc.building_id or loc.id,
            'name': loc.name,
            'type': structured_info.get('type', '地点'),
            'position': position,  # [lng, lat]
            'description': (loc.rich_content or loc.address or '')[:100],
            'openTime': structured_info.get('openTime', ''),
            'address': loc.address or '',
            'phone': structured_info.get('phone', ''),
            'facilities': structured_info.get('facilities', []),
            'mainImage': loc.main_image,
            'wikiId': loc.id,
        }
        
        buildings.append(building_data)
    
    return jsonify({
        'buildings': buildings,
        'total': len(buildings)
    })
```

---

## 错误处理

### 服务器错误

**HTTP 状态码**: `500 Internal Server Error`

```json
{
  "error": "Internal server error",
  "message": "详细错误信息"
}
```

---

## 测试建议

### 使用 curl 测试

```bash
curl -X GET http://192.168.3.197:5000/api/location/map-buildings
```

### 使用浏览器测试

直接访问：
```
http://192.168.3.197:5000/api/location/map-buildings
```

### 验证要点

1. ✅ 返回的 JSON 格式正确
2. ✅ `buildings` 是数组
3. ✅ 每个建筑都有 `position` 字段
4. ✅ `position` 是两个数字的数组 `[经度, 纬度]`
5. ✅ 经纬度数值合理（上海地区大约：经度 121.x，纬度 31.x）
6. ✅ 至少返回几个测试数据

---

## 前端使用方式

前端会在地图页面加载时自动调用此接口：

```javascript
async loadBuildingsFromBackend() {
  try {
    const response = await fetch('/api/location/map-buildings')
    const data = await response.json()
    
    // 使用返回的建筑数据渲染地图标记
    this.buildings = data.buildings || []
    
    console.log(`成功加载 ${data.total} 个建筑`)
  } catch (error) {
    console.error('加载建筑数据失败:', error)
  }
}
```

---

## 常见问题

### Q1: 如果某个地点没有经纬度怎么办？

**A**: 不要返回该地点。前端会自动过滤，只显示有经纬度的地点。

### Q2: 经纬度的精度要求？

**A**: 建议保留 6 位小数（精确到米级），例如：`121.212345`

### Q3: 图片路径是相对路径还是绝对路径？

**A**: 
- 相对路径：`/uploads/library.jpg`（推荐）
- 绝对路径：`http://192.168.3.197:5000/uploads/library.jpg`

前端会自动处理相对路径。

### Q4: 需要登录才能访问吗？

**A**: 不需要。这是公开接口，任何人都可以访问。

---

## 联系方式

如有疑问，请联系前端开发：
- 前端开发者：[你的名字]
- 文档版本：v1.0
- 最后更新：2025-12-09
