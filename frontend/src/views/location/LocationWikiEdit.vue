<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <router-link
          :to="isEditMode ? `/location/${locationId}` : '/'"
          class="inline-flex items-center text-gray-600 hover:text-primary transition-colors mb-4"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          {{ isEditMode ? '返回 Wiki 页面' : '返回首页' }}
        </router-link>
        <h1 class="text-3xl font-heading font-bold text-dark-blue mb-2">
          {{ isEditMode ? '编辑地点 Wiki' : '发布新地点 Wiki' }}
        </h1>
        <p class="text-gray-600">
          {{ isEditMode ? '修改地点信息' : '创建并分享新的地点信息' }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center py-20">
        <div class="text-center">
          <div
            class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"
          ></div>
          <p class="text-gray-600">正在加载数据...</p>
        </div>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Basic Info Card -->
        <div class="card">
          <h2 class="text-xl font-heading font-bold text-dark-blue mb-6">基本信息</h2>
          <div class="space-y-4">
            <!-- Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                地点名称 <span class="text-red-500">*</span>
              </label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                placeholder="请输入地点名称"
                class="input-field"
                :class="{ 'border-red-500 focus:ring-red-500': errors.name }"
                @blur="validateField('name')"
              />
              <p v-if="errors.name" class="mt-2 text-sm text-red-600">{{ errors.name }}</p>
            </div>

            <!-- Address -->
            <div>
              <label for="address" class="block text-sm font-medium text-gray-700 mb-2">
                地址 <span class="text-red-500">*</span>
              </label>
              <input
                id="address"
                v-model="formData.address"
                type="text"
                placeholder="请输入详细地址"
                class="input-field"
                :class="{ 'border-red-500 focus:ring-red-500': errors.address }"
                @blur="validateField('address')"
              />
              <p v-if="errors.address" class="mt-2 text-sm text-red-600">{{ errors.address }}</p>
            </div>

            <!-- Coordinates -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="latitude" class="block text-sm font-medium text-gray-700 mb-2">
                  纬度 <span class="text-red-500">*</span>
                </label>
                <input
                  id="latitude"
                  v-model="formData.latitude"
                  type="text"
                  placeholder="例如：31.289549"
                  class="input-field"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.latitude }"
                  @blur="validateField('latitude')"
                />
                <p v-if="errors.latitude" class="mt-2 text-sm text-red-600">{{ errors.latitude }}</p>
                <p v-else class="mt-1 text-xs text-gray-500">范围：-90 到 90</p>
              </div>
              <div>
                <label for="longitude" class="block text-sm font-medium text-gray-700 mb-2">
                  经度 <span class="text-red-500">*</span>
                </label>
                <input
                  id="longitude"
                  v-model="formData.longitude"
                  type="text"
                  placeholder="例如：121.501123"
                  class="input-field"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.longitude }"
                  @blur="validateField('longitude')"
                />
                <p v-if="errors.longitude" class="mt-2 text-sm text-red-600">{{ errors.longitude }}</p>
                <p v-else class="mt-1 text-xs text-gray-500">范围：-180 到 180</p>
              </div>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p class="text-sm text-blue-800">
                💡 <strong>提示：</strong>可以在
                <a href="https://lbs.amap.com/tools/picker" target="_blank" class="text-blue-600 hover:underline">高德地图坐标拾取器</a>
                或
                <a href="https://api.map.baidu.com/lbsapi/getpoint/index.html" target="_blank" class="text-blue-600 hover:underline">百度地图坐标拾取器</a>
                中获取精确的经纬度坐标
              </p>
            </div>

            <!-- Category -->
            <div>
              <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
                分类
              </label>
              <select id="category" v-model="formData.category" class="input-field">
                <option value="">请选择分类</option>
                <option value="学术科研">📚 学术科研</option>
                <option value="生活服务">🍽️ 生活服务</option>
                <option value="休闲娱乐">⚽ 休闲娱乐</option>
                <option value="交通设施">🚌 交通设施</option>
                <option value="行政办公">🏢 行政办公</option>
              </select>
            </div>

            <!-- Main Image -->
            <div>
              <label for="mainImage" class="block text-sm font-medium text-gray-700 mb-2">
                主图 URL
              </label>
              <input
                id="mainImage"
                v-model="formData.mainImage"
                type="text"
                placeholder="请输入图片 URL 或路径"
                class="input-field"
              />
              <p class="mt-2 text-sm text-gray-500">
                例如：/图书馆材料学院.jpg 或 https://example.com/image.jpg
              </p>
              <!-- Image Preview -->
              <div v-if="formData.mainImage" class="mt-4">
                <img
                  :src="formData.mainImage"
                  alt="预览图"
                  class="max-w-md h-48 object-cover rounded-lg border border-gray-200"
                  @error="handleImageError"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Structured Info Card -->
        <div class="card">
          <h2 class="text-xl font-heading font-bold text-dark-blue mb-6">详细信息</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Open Time -->
            <div>
              <label for="openTime" class="block text-sm font-medium text-gray-700 mb-2">
                开放时间
              </label>
              <input
                id="openTime"
                v-model="formData.structuredInfo.openTime"
                type="text"
                placeholder="例如：周一至周日 8:00 - 22:00"
                class="input-field"
              />
            </div>

            <!-- Average Cost -->
            <div>
              <label for="averageCost" class="block text-sm font-medium text-gray-700 mb-2">
                人均消费
              </label>
              <input
                id="averageCost"
                v-model="formData.structuredInfo.averageCost"
                type="text"
                placeholder="例如：免费 或 30元"
                class="input-field"
              />
            </div>

            <!-- Phone -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                联系电话
              </label>
              <input
                id="phone"
                v-model="formData.structuredInfo.phone"
                type="tel"
                placeholder="例如：021-69585000"
                class="input-field"
              />
            </div>

            <!-- Website -->
            <div>
              <label for="website" class="block text-sm font-medium text-gray-700 mb-2">
                官方网站
              </label>
              <input
                id="website"
                v-model="formData.structuredInfo.website"
                type="url"
                placeholder="https://example.com"
                class="input-field"
              />
            </div>
          </div>
        </div>

        <!-- Rich Text Content Card -->
        <div class="card">
          <h2 class="text-xl font-heading font-bold text-dark-blue mb-6">内容描述</h2>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              富文本内容 <span class="text-red-500">*</span>
            </label>
            <RichTextEditor
              v-model="formData.richContent"
              placeholder="请输入地点详细介绍..."
              class="border border-gray-300 rounded-lg"
            />
            <p v-if="errors.richContent" class="mt-2 text-sm text-red-600">
              {{ errors.richContent }}
            </p>
            <p class="mt-2 text-sm text-gray-500">支持标题、加粗、斜体、列表、图片、链接等格式</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
          <button
            type="button"
            @click="handleCancel"
            class="btn btn-ghost"
            :disabled="isSubmitting"
          >
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="flex items-center">
              <svg
                class="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              提交中...
            </span>
            <span v-else>{{ isEditMode ? '保存修改' : '发布' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RichTextEditor from '../../components/RichTextEditor.vue'
import {
  getLocationWiki,
  createLocationWiki,
  updateLocationWiki,
  type LocationWikiData,
} from '../../api/location'
import auth from '../../services/auth'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => {
  // 检查路由名称或路径来判断是否为编辑模式
  return route.name === 'LocationWikiEdit' || (route.path.includes('/edit') && route.params.id)
})
const locationId = computed(() => {
  // 从路由参数中获取 locationId
  const id = route.params.id as string
  return id && id !== 'create' ? id : ''
})

const isLoading = ref(false)
const isSubmitting = ref(false)
const errors = ref<Record<string, string>>({})

const formData = ref({
  name: '',
  address: '',
  category: '',
  mainImage: '',
  latitude: '',
  longitude: '',
  richContent: '',
  structuredInfo: {
    openTime: '',
    averageCost: '',
    phone: '',
    website: '',
  },
})

// 表单验证
const validateField = (field: string): boolean => {
  // 删除该字段的错误信息
  delete errors.value[field]

  switch (field) {
    case 'name':
      if (!formData.value.name?.trim()) {
        errors.value.name = '地点名称不能为空'
        return false
      }
      break
    case 'address':
      if (!formData.value.address?.trim()) {
        errors.value.address = '地址不能为空'
        return false
      }
      break
    case 'latitude':
      if (!formData.value.latitude?.toString().trim()) {
        errors.value.latitude = '纬度不能为空'
        return false
      }
      const lat = parseFloat(formData.value.latitude)
      if (isNaN(lat)) {
        errors.value.latitude = '纬度必须是有效的数字'
        return false
      }
      if (lat < -90 || lat > 90) {
        errors.value.latitude = '纬度必须在 -90 到 90 之间'
        return false
      }
      break
    case 'longitude':
      if (!formData.value.longitude?.toString().trim()) {
        errors.value.longitude = '经度不能为空'
        return false
      }
      const lng = parseFloat(formData.value.longitude)
      if (isNaN(lng)) {
        errors.value.longitude = '经度必须是有效的数字'
        return false
      }
      if (lng < -180 || lng > 180) {
        errors.value.longitude = '经度必须在 -180 到 180 之间'
        return false
      }
      break
    case 'richContent':
      if (!formData.value.richContent?.trim() || formData.value.richContent === '<p><br></p>') {
        errors.value.richContent = '内容描述不能为空'
        return false
      }
      break
  }
  return true
}

const validateForm = (): boolean => {
  errors.value = {}

  const nameValid = validateField('name')
  const addressValid = validateField('address')
  const latValid = validateField('latitude')
  const lngValid = validateField('longitude')
  const contentValid = validateField('richContent')

  const hasErrors = Object.keys(errors.value).length > 0
  
  console.log('📝 [表单验证]', {
    name: formData.value.name,
    nameValid,
    address: formData.value.address,
    addressValid,
    richContent: formData.value.richContent?.substring(0, 50),
    contentValid,
    errors: errors.value,
    hasErrors,
    result: !hasErrors
  })

  return !hasErrors
}

// 获取现有数据（编辑模式）
const fetchWikiData = async () => {
  if (!isEditMode.value || !locationId.value) {
    console.log('不是编辑模式或没有 locationId，跳过加载')
    return
  }

  console.log(`加载 Wiki 数据: GET /api/location/${locationId.value}/wiki`)
  isLoading.value = true
  try {
    const data = await getLocationWiki(locationId.value)
    console.log('加载成功，Wiki 数据:', data)
    formData.value = {
      name: data.name,
      address: data.address,
      category: data.category || '',
      mainImage: data.mainImage || '',
      latitude: data.latitude?.toString() || '',
      longitude: data.longitude?.toString() || '',
      richContent: data.richContent,
      structuredInfo: {
        openTime: data.structuredInfo.openTime || '',
        averageCost: data.structuredInfo.averageCost || '',
        phone: data.structuredInfo.phone || '',
        website: data.structuredInfo.website || '',
      },
    }
  } catch (error: any) {
    console.error('获取 Wiki 数据失败:', error)
    alert('加载数据失败，请稍后重试')
    router.back()
  } finally {
    isLoading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  console.log('=== Wiki 提交开始 ===')
  console.log('表单数据:', JSON.parse(JSON.stringify(formData.value)))
  
  const isValid = validateForm()
  
  if (!isValid) {
    console.error('❌ 表单验证失败:', errors.value)
    alert('请填写完整信息：' + Object.values(errors.value).join(', '))
    // 滚动到第一个错误字段
    const firstError = Object.keys(errors.value)[0]
    if (firstError) {
      const element = document.getElementById(firstError)
      if (!element) return
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      element.focus()
    }
    return
  }

  isSubmitting.value = true
  console.log('提交中...')

  try {
    const payload = {
      name: formData.value.name.trim(),
      address: formData.value.address.trim(),
      category: formData.value.category.trim() || undefined,
      mainImage: formData.value.mainImage.trim() || undefined,
      latitude: parseFloat(formData.value.latitude),
      longitude: parseFloat(formData.value.longitude),
      richContent: formData.value.richContent,
      structuredInfo: formData.value.structuredInfo,
    }

    console.log('准备提交 Wiki 数据:', {
      isEditMode: isEditMode.value,
      locationId: locationId.value,
      payload
    })

    if (isEditMode.value && locationId.value) {
      // 更新
      console.log(`[UPDATE] 调用 updateLocationWiki API: PUT /api/location/${locationId.value}/wiki`)
      const result = await updateLocationWiki(locationId.value, payload)
      console.log('[UPDATE] Wiki 更新成功，返回数据:', result)
      alert('✅ Wiki 更新成功！')
      // 编辑模式：返回 Wiki 页面
      router.push(`/location/${locationId.value}`)
    } else {
      // 创建
      console.log('[CREATE] 调用 createLocationWiki API: POST /api/location/wiki')
      const result = await createLocationWiki(payload)
      console.log('[CREATE] Wiki 创建成功，返回数据:', result)
      alert('✅ Wiki 发布成功！')
      router.push(`/location/${result.id}`)
    }
  } catch (error: any) {
    console.error('❌ 提交失败 - 详细错误:', {
      message: error.message,
      status: error.status,
      stack: error.stack,
      error: error
    })
    
    // 更详细的错误提示
    let errorMsg = '提交失败'
    if (error.status === 401) {
      errorMsg = '未登录或登录已过期，请重新登录'
    } else if (error.status === 403) {
      errorMsg = '权限不足，只有 Wiki 管理员可以编辑'
    } else if (error.message) {
      errorMsg = error.message
    }
    
    alert(`❌ ${errorMsg}`)
  } finally {
    isSubmitting.value = false
    console.log('=== Wiki 提交结束 ===')
  }
}

// 取消
const handleCancel = () => {
  if (confirm('确定要离开吗？未保存的更改将丢失。')) {
    router.back()
  }
}

// 图片加载错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

onMounted(async () => {
  // 检查用户是否有权限编辑Wiki
  const user = auth.getUser()
  const isAdmin = auth.isAuthenticated() && user && (user.role === 'wiki_admin' || user.role === 'admin')
  
  if (!isAdmin) {
    alert('您没有权限编辑Wiki，只有Wiki管理员可以编辑')
    router.push('/admin/wiki')
    return
  }
  
  fetchWikiData()
})
</script>

<style scoped>
/* 确保表单样式正确 */
</style>
