<template>
  <div class="min-h-screen bg-gray-50 overflow-x-hidden lg:overflow-visible">
    <div class="container mx-auto px-5">
      <header class="flex justify-between py-8 md:py-12 items-center">
        <div class="flex items-center space-x-2">
          <div
            class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center shadow-md"
          >
            <span class="text-white font-bold text-xl">济</span>
          </div>
          <span class="text-xl font-heading font-bold text-dark-blue hidden sm:block">济图通</span>
        </div>

        <nav class="flex items-center">
          <ul class="space-x-6 lg:space-x-10 font-heading font-medium items-center hidden md:flex">
            <li @click="showDialog('features')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              功能
            </li>
            <li @click="showDialog('about')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              关于
            </li>
            <li @click="showDialog('help')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              帮助
            </li>
            <li>
              <RouterLink
                to="/login"
                class="uppercase bg-secondary px-5 py-2 text-white text-sm rounded shadow-md hover:bg-white border-2 border-transparent hover:border-secondary hover:text-secondary cursor-pointer transition duration-200"
              >
                登录
              </RouterLink>
            </li>
          </ul>

          <button
            @click="toggleMobileMenu"
            type="button"
            class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg viewBox="0 0 24 24" class="h-6 w-6 fill-current text-gray-700">
              <path
                fill-rule="evenodd"
                d="M4 5h16a1 1 0 0 1 0 2H4a1 1 0 1 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2z"
              ></path>
            </svg>
          </button>
        </nav>
      </header>

      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-show="mobileMenuOpen" class="md:hidden pb-4 border-t border-gray-200 mb-4">
          <ul class="uppercase text-sm font-medium space-y-2 pt-4">
            <li
              @click="showDialog('features')"
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              功能
            </li>
            <li
              @click="showDialog('about')"
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              关于
            </li>
            <li
              @click="showDialog('help')"
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              帮助
            </li>
            <li class="pt-2">
              <RouterLink
                to="/login"
                class="block text-center bg-secondary px-5 py-2.5 text-white rounded-lg shadow-md hover:bg-secondary/90 transition-colors"
              >
                登录
              </RouterLink>
            </li>
          </ul>
        </div>
      </Transition>
    </div>

    <div class="container mx-auto px-5">
      <section class="grid grid-cols-none lg:grid-cols-2 items-center pb-8 lg:pb-16 gap-10">
        <div class="lg:w-5/6 order-2 lg:order-none">
          <div class="mb-8">
            <p
              class="inline-flex items-center px-3 py-1 bg-primary/10 text-primary text-sm font-medium rounded-full mb-4"
            >
              <svg class="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M12 2a10 10 0 00-3.162 19.478c.5.093.683-.217.683-.483 0-.237-.009-.868-.013-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.152-1.11-1.459-1.11-1.459-.908-.62.069-.608.069-.608 1.004.071 1.532 1.028 1.532 1.028.892 1.53 2.341 1.088 2.912.833.091-.647.35-1.088.637-1.338-2.221-.253-4.555-1.111-4.555-4.944 0-1.091.39-1.985 1.029-2.685-.103-.253-.446-1.272.098-2.65 0 0 .84-.269 2.75 1.026A9.564 9.564 0 0112 6.844a9.56 9.56 0 012.503.337c1.91-1.295 2.75-1.026 2.75-1.026.546 1.378.203 2.397.1 2.65.64.7 1.028 1.594 1.028 2.685 0 3.842-2.337 4.688-4.566 4.937.36.31.68.921.68 1.856 0 1.338-.012 2.418-.012 2.747 0 .268.18.58.688.482A10 10 0 0012 2z"
                />
              </svg>
              立即加入济图通
            </p>
            <h1 class="text-4xl xl:text-5xl font-bold font-heading text-dark-blue mb-4">
              新用户注册
            </h1>
            <p class="text-lg lg:text-xl text-gray-600">
              一次注册，畅游同济校园知识库，收藏你的专属地点。
            </p>
          </div>

          <div class="bg-white rounded-2xl shadow-soft p-8">
            <div
              v-if="formError"
              class="mb-4 flex items-start rounded-lg border border-secondary/30 bg-secondary/5 px-4 py-3 text-sm text-secondary"
            >
              <svg class="w-5 h-5 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M8.257 3.099c.763-1.36 2.722-1.36 3.485 0l5.916 10.553c.746 1.33-.207 2.998-1.742 2.998H4.083c-1.535 0-2.488-1.668-1.742-2.998L8.257 3.1zM11 13a1 1 0 10-2 0 1 1 0 002 0zm-1-2a1 1 0 01-1-1V7a1 1 0 112 0v3a1 1 0 01-1 1z"
                  clip-rule="evenodd"
                />
              </svg>
              <span>{{ formError }}</span>
            </div>

            <form @submit.prevent="handleRegister" class="space-y-5">
              <div>
                <label for="register-phone" class="block text-sm font-medium text-gray-700 mb-2"
                  >手机号</label
                >
                <div class="relative">
                  <input
                    id="register-phone"
                    type="tel"
                    maxlength="11"
                    v-model="form.phone"
                    @input="errors.phone = ''"
                    placeholder="请输入常用手机号"
                    class="input-field pl-10"
                    :class="{ 'border-secondary focus:ring-secondary': errors.phone }"
                  />
                  <svg
                    class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <p v-if="errors.phone" class="mt-2 text-sm text-secondary flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ errors.phone }}
                </p>
              </div>

              <div>
                <label for="register-password" class="block text-sm font-medium text-gray-700 mb-2"
                  >设置密码</label
                >
                <div class="relative">
                  <input
                    id="register-password"
                    :type="showPassword ? 'text' : 'password'"
                    v-model="form.password"
                    @input="errors.password = ''"
                    placeholder="至少 6 位，建议包含字母与数字"
                    class="input-field pl-10 pr-10"
                    :class="{ 'border-secondary focus:ring-secondary': errors.password }"
                  />
                  <svg
                    class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <!-- 密码隐藏时显示眼睛斜杠图标 -->
                    <svg
                      v-if="!showPassword"
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                      />
                    </svg>
                    <!-- 密码可见时显示眼睛图标 -->
                    <svg
                      v-else
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  </button>
                </div>
                <p v-if="errors.password" class="mt-2 text-sm text-secondary flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ errors.password }}
                </p>
              </div>

              <div>
                <label for="register-confirm" class="block text-sm font-medium text-gray-700 mb-2"
                  >确认密码</label
                >
                <div class="relative">
                  <input
                    id="register-confirm"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    v-model="form.confirmPassword"
                    @input="errors.confirmPassword = ''"
                    placeholder="再次输入密码"
                    class="input-field pl-10 pr-10"
                    :class="{ 'border-secondary focus:ring-secondary': errors.confirmPassword }"
                  />
                  <svg
                    class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <!-- 密码隐藏时显示眼睛斜杠图标 -->
                    <svg
                      v-if="!showConfirmPassword"
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                      />
                    </svg>
                    <!-- 密码可见时显示眼睛图标 -->
                    <svg
                      v-else
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                  </button>
                </div>
                <p
                  v-if="errors.confirmPassword"
                  class="mt-2 text-sm text-secondary flex items-center"
                >
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ errors.confirmPassword }}
                </p>
              </div>

              <div>
                <label for="register-nickname" class="block text-sm font-medium text-gray-700 mb-2"
                  >昵称（选填）</label
                >
                <input
                  id="register-nickname"
                  type="text"
                  v-model="form.nickname"
                  maxlength="20"
                  placeholder="展示在个人资料和评论中的名称"
                  class="input-field"
                />
              </div>

              <label class="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="form.agree"
                  @change="errors.agree = ''"
                  class="mt-1 w-4 h-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary cursor-pointer"
                />
                <span class="text-sm text-gray-600">
                  我已阅读并同意
                  <a @click.prevent="showDialog('terms')" class="text-primary font-medium hover:text-primary/80 cursor-pointer"
                    >《用户服务协议》</a
                  >
                  和
                  <a @click.prevent="showDialog('privacy')" class="text-primary font-medium hover:text-primary/80 cursor-pointer"
                    >《隐私政策》</a
                  >
                </span>
              </label>
              <p v-if="errors.agree" class="text-sm text-secondary flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clip-rule="evenodd"
                  />
                </svg>
                {{ errors.agree }}
              </p>

              <button
                type="submit"
                :disabled="isLoading"
                class="w-full btn btn-primary py-3 text-base font-semibold relative flex items-center justify-center"
              >
                <span v-if="isLoading" class="flex items-center">
                  <svg
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                  注册中...
                </span>
                <span v-else>创建账号</span>
              </button>
            </form>

            <div class="text-center mt-6 text-sm text-gray-600">
              已有账号？
              <RouterLink
                to="/login"
                class="text-primary font-medium hover:text-primary/80 transition-colors"
              >
                返回登录
              </RouterLink>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-4 rounded-xl bg-primary/5 text-center">
              <p class="text-3xl font-bold text-primary">3k+</p>
              <p class="text-sm text-gray-600">校园地点数据</p>
            </div>
            <div class="p-4 rounded-xl bg-secondary/5 text-center">
              <p class="text-3xl font-bold text-secondary">1.2w</p>
              <p class="text-sm text-gray-600">条真实评论</p>
            </div>
            <div class="p-4 rounded-xl bg-accent/5 text-center">
              <p class="text-3xl font-bold text-accent">24/7</p>
              <p class="text-sm text-gray-600">保障与支持</p>
            </div>
          </div>
        </div>

        <div class="relative order-1 lg:order-none mb-12 lg:mb-0 lg:-mr-10">
          <div class="relative z-10">
            <img class="w-full" src="/illustration-hero.svg" alt="济图通插画" />
          </div>
          <div
            class="-z-10 bg-primary h-56 w-full sm:h-80 sm:w-full rounded-l-full absolute -right-28 md:-right-48 -bottom-8"
          ></div>

          <div class="absolute top-10 -left-6 bg-white shadow-soft rounded-2xl p-5 w-64">
            <p class="text-sm text-gray-500 mb-2">今日探索热点</p>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-800">图书馆</span>
                <span class="text-primary text-sm font-semibold">热度 98%</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-800">嘉定体育中心</span>
                <span class="text-primary text-sm font-semibold">热度 92%</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-800">一食堂</span>
                <span class="text-primary text-sm font-semibold">热度 89%</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 弹窗 -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="dialogVisible"
          class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          @click="dialogVisible = false"
        >
          <div
            class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            @click.stop
          >
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-bold text-gray-900">{{ dialogTitle }}</h3>
              <button
                @click="dialogVisible = false"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="text-gray-600 whitespace-pre-line">
              {{ dialogContent }}
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { registerUser } from '../../api/user'
import userAuth from '../../services/userAuth'

const router = useRouter()

const mobileMenuOpen = ref(false)
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogContent = ref('')

const dialogContents: Record<string, { title: string; content: string }> = {
  features: {
    title: '功能介绍',
    content: '济图通提供校园地图导航、地点查询、路线规划等功能，帮助你更好地探索校园。',
  },
  about: {
    title: '关于我们',
    content: '济图通是专为同济大学嘉定校区打造的校园服务平台，致力于为师生提供便捷的校园生活服务。',
  },
  help: {
    title: '帮助中心',
    content: '如需帮助，请联系我们的客服团队或查看常见问题解答。',
  },
  terms: {
    title: '用户服务协议',
    content: '暂无',
  },
  privacy: {
    title: '隐私政策',
    content: '暂无',
  },
}

const showDialog = (type: string) => {
  const content = dialogContents[type]
  if (content) {
    dialogTitle.value = content.title
    dialogContent.value = content.content
    dialogVisible.value = true
  }
}

const form = ref({
  phone: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  agree: false,
})

const errors = ref({
  phone: '',
  password: '',
  confirmPassword: '',
  agree: '',
})

const formError = ref('')
const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const phoneRegex = /^1[3-9]\d{9}$/
const isPhoneValid = computed(() => phoneRegex.test(form.value.phone))

const validateForm = () => {
  errors.value = {
    phone: '',
    password: '',
    confirmPassword: '',
    agree: '',
  }
  formError.value = ''

  if (!form.value.phone) {
    errors.value.phone = '请输入手机号'
    return false
  }

  if (!isPhoneValid.value) {
    errors.value.phone = '请输入正确的手机号格式'
    return false
  }

  if (!form.value.password) {
    errors.value.password = '请设置登录密码'
    return false
  }

  if (form.value.password.length < 6) {
    errors.value.password = '密码长度至少为 6 位'
    return false
  }

  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = '请再次输入密码'
    return false
  }

  if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = '两次输入的密码不一致'
    return false
  }

  if (!form.value.agree) {
    errors.value.agree = '请勾选并同意相关协议'
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const payload = {
      phone: form.value.phone,
      password: form.value.password,
      nickname: form.value.nickname.trim() || undefined,
    }
    const response = await registerUser(payload)
    
    // 注册成功后，先清除旧的 session，再设置新的 session
    userAuth.clearSession()
    userAuth.setSession(response)
    
    router.push({ name: 'UserProfile' })
  } catch (error: any) {
    console.error('注册失败:', error)
    formError.value = error?.message || '注册失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}
</script>
