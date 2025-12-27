<template>
  <div v-if="tags && tags.length > 0" class="card">
    <h2 class="text-xl font-heading font-bold text-dark-blue mb-4">热门标签</h2>
    <div class="flex flex-wrap gap-3">
      <component
        :is="clickable ? 'button' : 'span'"
        v-for="tag in sortedTags"
        :key="tag.id"
        @click="clickable ? handleTagClick(tag) : null"
        class="px-3 py-1.5 rounded-full font-medium transition-all"
        :class="[
          getTagClasses(tag),
          clickable ? 'hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 cursor-pointer' : 'cursor-default'
        ]"
        :style="getTagStyles(tag)"
      >
        #{{ tag.name }}
        <span v-if="showCount && tag.count" class="ml-1 text-xs opacity-75">
          ({{ tag.count }})
        </span>
      </component>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export interface Tag {
  id: number
  name: string
  color?: string
  count?: number // 热度/使用次数
}

const props = withDefaults(
  defineProps<{
    tags: Tag[]
    showCount?: boolean // 是否显示标签数量
    clickable?: boolean // 是否可点击
  }>(),
  {
    showCount: false,
    clickable: true,
  },
)

const emit = defineEmits<{
  (e: 'tag-click', tag: Tag): void
}>()

const router = useRouter()

// 根据热度排序标签（热度高的在前）
const sortedTags = computed(() => {
  return [...props.tags].sort((a, b) => (b.count || 0) - (a.count || 0))
})

type TagLevel = 0 | 1 | 2 | 3 | 4

// 计算标签的热度等级（0-4，用于确定大小和透明度）
const getTagLevel = (tag: Tag): TagLevel => {
  if (!tag.count || props.tags.length === 0) return 2

  const maxCount = Math.max(...props.tags.map((t) => t.count || 0))
  if (maxCount === 0) return 2

  const ratio = tag.count / maxCount
  if (ratio >= 0.8) return 4 // 最热门
  if (ratio >= 0.6) return 3 // 很热门
  if (ratio >= 0.4) return 2 // 一般
  if (ratio >= 0.2) return 1 // 较冷门
  return 0 // 冷门
}

// 获取标签的样式类
const getTagClasses = (tag: Tag): string => {
  const level = getTagLevel(tag)

  // 根据热度等级设置基础大小
  const sizeClasses: Record<TagLevel, string> = {
    0: 'text-xs px-2 py-1', // 冷门 - 最小
    1: 'text-sm px-2.5 py-1', // 较冷门
    2: 'text-sm px-3 py-1.5', // 一般
    3: 'text-base px-3.5 py-2', // 很热门
    4: 'text-lg px-4 py-2.5', // 最热门 - 最大
  }

  // 如果标签有自定义颜色，使用自定义颜色
  if (tag.color) {
    return `${sizeClasses[level]}`
  }

  // 根据热度使用不同的颜色方案
  const colorClasses: Record<TagLevel, string> = {
    0: 'bg-gray-100 text-gray-600', // 冷门 - 灰色
    1: 'bg-blue-50 text-blue-600', // 较冷门 - 浅蓝
    2: 'bg-blue-100 text-blue-700', // 一般 - 蓝色
    3: 'bg-primary/10 text-primary', // 很热门 - 主色调
    4: 'bg-primary text-white', // 最热门 - 主色调实心
  }

  return `${sizeClasses[level]} ${colorClasses[level]}`
}

// 将十六进制颜色转换为 rgba
const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

// 获取标签的内联样式（用于自定义颜色）
const getTagStyles = (tag: Tag): Record<string, string> => {
  if (!tag.color) return {}

  const level = getTagLevel(tag)
  // 根据热度设置透明度
  const opacities: Record<TagLevel, number> = {
    0: 0.15, // 冷门 - 很透明
    1: 0.25, // 较冷门
    2: 0.4, // 一般
    3: 0.7, // 很热门
    4: 1.0, // 最热门 - 不透明
  }

  const alpha = opacities[level]
  const isDark = level >= 4 // 最热门的标签使用白色文字

  return {
    backgroundColor: hexToRgba(tag.color, alpha),
    color: isDark ? 'white' : tag.color,
    borderColor: tag.color,
    borderWidth: '1px',
    borderStyle: 'solid',
  }
}

// 处理标签点击
const handleTagClick = (tag: Tag) => {
  emit('tag-click', tag)

  // 默认跳转到搜索页面，带标签筛选
  // 可以根据实际需求修改路由
  router.push({
    path: '/',
    query: {
      tag: tag.name,
      tagId: tag.id,
    },
  })
}
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}
</style>
