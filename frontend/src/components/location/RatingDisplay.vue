<template>
  <div class="card">
    <h2 class="text-2xl font-heading font-bold text-dark-blue mb-6">评分与评价</h2>

    <!-- Average Rating -->
    <div class="flex items-center mb-6 pb-6 border-b border-gray-200">
      <div class="text-center mr-8">
        <div class="text-5xl font-bold text-dark-blue mb-2">
          {{ Number(rating.average || 0).toFixed(1) }}
        </div>
        <div class="flex items-center justify-center mb-2">
          <div class="flex">
            <svg
              v-for="i in 5"
              :key="i"
              class="w-6 h-6"
              :class="i <= Math.round(Number(rating.average || 0)) ? 'text-yellow-400' : 'text-gray-300'"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
          </div>
        </div>
        <p class="text-sm text-gray-600">基于 {{ Number(rating.count || 0) }} 条评价</p>
      </div>

      <!-- Rating Distribution -->
      <div class="flex-1 space-y-2">
        <div
          v-for="dist in rating.distribution"
          :key="dist.stars"
          class="flex items-center"
        >
          <span class="text-sm text-gray-600 w-8">{{ dist.stars }}星</span>
          <div class="flex-1 mx-3 bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              class="bg-primary h-full rounded-full transition-all"
              :style="{
                width: `${Number(rating.count) > 0 ? (Number(dist.count || 0) / Number(rating.count)) * 100 : 0}%`,
              }"
            ></div>
          </div>
          <span class="text-sm text-gray-600 w-12 text-right">
            {{ dist.count }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface RatingData {
  average: number
  count: number
  distribution: Array<{ stars: number; count: number }>
}

defineProps<{
  rating: RatingData
}>()
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}
</style>
