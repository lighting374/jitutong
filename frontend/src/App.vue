<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import auth from './services/auth'
const mobileMenuOpen = ref(false)
const route = useRoute()

// 判断是否为登录或注册页面
const isLoginPage = computed(() => route.path === '/login' || route.path === '/register')

// 判断是否为管理员页面（只隐藏管理员后台的导航栏）
const isAdminPage = computed(() => {
  return route.path.startsWith('/admin')
})

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Navigation Header (Hidden on login page and admin pages) -->
    <header v-if="!isLoginPage && !isAdminPage" class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4 md:py-5">
          <!-- Logo -->
          <div class="flex items-center space-x-2">
            <div
              class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center shadow-md"
            >
              <span class="text-white font-bold text-xl">济</span>
            </div>
            <span class="text-xl font-heading font-bold text-dark-blue hidden sm:block"
              >济图通</span
            >
          </div>

          <!-- Desktop Navigation -->
          <nav class="hidden md:flex items-center space-x-8">
            <router-link
              to="/map"
              class="text-gray-700 hover:text-primary font-medium transition-colors duration-200"
              :class="{ 'text-primary': route.path === '/map' }"
            >
              校园地图
            </router-link>
            <router-link
              to="/wiki"
              class="text-gray-700 hover:text-primary font-medium transition-colors duration-200"
              :class="{ 'text-primary': route.path.startsWith('/wiki') }"
            >
              Wiki 展示
            </router-link>
            <router-link
              to="/user"
              class="text-gray-700 hover:text-primary font-medium transition-colors duration-200"
              :class="{ 'text-primary': route.path === '/user' }"
            >
              个人中心
            </router-link>
          </nav>

          <!-- Mobile menu button -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg
              v-if="!mobileMenuOpen"
              class="w-6 h-6 text-gray-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
            <svg
              v-else
              class="w-6 h-6 text-gray-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Mobile Navigation -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <nav
            v-show="mobileMenuOpen"
            class="md:hidden pb-4 border-t border-gray-100 mt-2 pt-4 space-y-2"
          >
            <router-link
              @click="closeMobileMenu"
              to="/map"
              class="block px-4 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 hover:text-primary font-medium transition-colors"
              :class="{ 'bg-blue-50 text-primary': route.path === '/map' }"
            >
              校园地图
            </router-link>
            <router-link
              @click="closeMobileMenu"
              to="/wiki"
              class="block px-4 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 hover:text-primary font-medium transition-colors"
              :class="{ 'bg-blue-50 text-primary': route.path.startsWith('/wiki') }"
            >
              Wiki 展示
            </router-link>
            <router-link
              @click="closeMobileMenu"
              to="/user"
              class="block px-4 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 hover:text-primary font-medium transition-colors"
              :class="{ 'bg-blue-50 text-primary': route.path === '/user' }"
            >
              个人中心
            </router-link>
          </nav>
        </Transition>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- Footer (Hidden on login page and admin pages) -->
    <footer v-if="!isLoginPage && !isAdminPage" class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center text-gray-600 text-sm">
          <p>© 2025 济图通 - 探索同济校园的每个角落</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Custom animations and additional styles can be added here if needed */
</style>
