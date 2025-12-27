<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import auth from '../services/auth'

const router = useRouter()

const currentUser = computed(() => auth.getUser())
const isWikiAdmin = computed(() => currentUser.value?.role === 'wiki_admin')

function doLogout() {
  auth.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="min-h-screen flex bg-gray-100">
    <aside class="w-64 bg-white border-r flex flex-col">
      <div class="p-4 border-b">
        <div class="text-xl font-bold">管理后台</div>
        <div v-if="currentUser" class="text-sm text-gray-500 mt-1">
          {{ currentUser.username }}
          <span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded ml-1">
            {{ isWikiAdmin ? 'Wiki管理员' : '管理员' }}
          </span>
        </div>
      </div>
      <nav class="p-4 space-y-2 flex-1">
        <!-- Wiki 管理员专属菜单 -->
        <template v-if="isWikiAdmin">
          <router-link to="/admin/wiki" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            📝 Wiki 管理
          </router-link>
        </template>
        
        <!-- 普通管理员菜单 -->
        <template v-else>
          <router-link to="/admin/dashboard" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            📊 仪表盘
          </router-link>
          <router-link to="/admin/users" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            👥 用户管理
          </router-link>
          <router-link to="/admin/locations" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            📍 地点管理
          </router-link>
          <router-link to="/admin/reviews" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            ✅ 内容审核
          </router-link>
          <router-link to="/admin/analytics" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            📈 数据看板
          </router-link>
          <router-link to="/admin/logs" class="block px-3 py-2 rounded hover:bg-gray-50 transition-colors">
            📋 日志查看
          </router-link>
        </template>
      </nav>
      <div class="p-4 border-t">
        <button @click="doLogout" class="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600 transition-colors">
          登出
        </button>
      </div>
    </aside>

    <main class="flex-1 p-6 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.router-link-active {
  background-color: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}
</style>
