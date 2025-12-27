<template>
  <div class="min-h-screen bg-gray-50 overflow-x-hidden lg:overflow-x-visible">
    <!-- Navbar Start -->
    <div class="container mx-auto px-5">
      <header class="flex justify-between py-8 md:py-12 items-center">
        <div class="flex items-center space-x-2">
          <div
            class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center shadow-md"
          >
            <span class="text-white font-bold text-xl">济</span>
          </div>
          <span class="text-xl font-heading font-bold text-dark-blue hidden sm:block">{{ t('brand') }}</span>
        </div>

        <nav class="flex items-center gap-3">
          <!-- Desktop Menu -->
          <ul class="space-x-6 lg:space-x-10 font-heading font-medium items-center hidden md:flex">
            <li @click="showDialog('features')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              {{ t('navFeatures') }}
            </li>
            <li @click="showDialog('about')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              {{ t('navAbout') }}
            </li>
            <li @click="showDialog('help')" class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer">
              {{ t('navHelp') }}
            </li>
            <li>
              <RouterLink
                to="/register"
                class="uppercase bg-secondary px-5 py-2 text-white text-sm rounded shadow-md hover:bg-white border-2 border-transparent hover:border-secondary hover:text-secondary cursor-pointer transition duration-200"
              >
                {{ t('register') }}
              </RouterLink>
            </li>
          </ul>

          <!-- Mobile Menu Button -->
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

      <!-- Mobile Menu -->
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
              {{ t('navFeatures') }}
            </li>
            <li
              @click="showDialog('about')"
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              {{ t('navAbout') }}
            </li>
            <li
              @click="showDialog('help')"
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              {{ t('navHelp') }}
            </li>
            <li class="pt-2">
              <RouterLink
                to="/register"
                class="block w-full text-center bg-secondary px-5 py-2.5 text-white rounded-lg shadow-md hover:bg-secondary/90 transition-colors"
              >
                {{ t('register') }}
              </RouterLink>
            </li>
          </ul>
        </div>
      </Transition>
    </div>
    <!-- Navbar End -->

    <div class="container mx-auto px-5">
      <section class="grid grid-cols-none lg:grid-cols-2 items-center pb-8 lg:pb-16">
        <!-- Left Side - Login Form -->
        <div class="lg:w-5/6 order-2 lg:order-none">
          <!-- Header -->
          <div class="mb-8">
            <h1 class="text-4xl xl:text-5xl font-bold font-heading text-dark-blue mb-4">
              {{ t('welcomeTitle') }}
            </h1>
            <p class="text-lg lg:text-xl text-gray-600">{{ t('welcomeSubtitle') }}</p>
          </div>

          <!-- Login Card -->
          <div class="bg-white rounded-2xl shadow-soft p-8">
            <!-- Login Form -->
            <form @submit.prevent="handleLogin" class="space-y-5">
              <!-- Phone Number Input -->
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                  {{ t('phoneLabel') }}
                </label>
                <div class="relative">
                  <input
                    id="phone"
                    type="tel"
                    v-model="loginForm.phone"
                    @input="phoneError = ''"
                    :placeholder="t('phonePlaceholder')"
                    maxlength="11"
                    class="input-field pl-10"
                    :class="{ 'border-secondary focus:ring-secondary': phoneError }"
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
                <p v-if="phoneError" class="mt-2 text-sm text-secondary flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ phoneError }}
                </p>
              </div>

              <!-- Password Input -->
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                  {{ t('passwordLabel') }}
                </label>
                <div class="relative">
                  <input
                    id="password"
                    :type="showPassword ? 'text' : 'password'"
                    v-model="loginForm.password"
                    @input="passwordError = ''"
                    :placeholder="t('passwordPlaceholder')"
                    class="input-field pl-10 pr-10"
                    :class="{ 'border-secondary focus:ring-secondary': passwordError }"
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
                <p v-if="passwordError" class="mt-2 text-sm text-secondary flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ passwordError }}
                </p>
              </div>

              <!-- Login Button -->
              <button
                type="submit"
                :disabled="isLoading"
                class="w-full btn btn-primary py-3 text-base font-semibold relative"
              >
                <span v-if="isLoading" class="flex items-center justify-center">
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
                  {{ t('loggingIn') }}
                </span>
                <span v-else>{{ t('login') }}</span>
              </button>
            </form>

            <!-- Divider -->
            <div class="relative my-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-200"></div>
              </div>
              <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-500">{{ t('or') }}</span>
              </div>
            </div>

            <!-- Register Link -->
            <div class="text-center">
              <p class="text-sm text-gray-600">
                {{ t('noAccount') }}
                <RouterLink
                  to="/register"
                  class="text-primary hover:text-primary/80 font-medium transition-colors"
                >
                  {{ t('signUpNow') }}
                </RouterLink>
              </p>
            </div>
          </div>
        </div>

        <!-- Right Side - Illustration -->
        <div class="relative order-1 lg:order-none mb-12 lg:mb-0 lg:-mr-10">
          <div class="relative z-10">
            <img class="w-full" src="/illustration-hero.svg" :alt="t('illustrationAlt')" />
          </div>
          <!-- Background Decoration -->
          <div
            class="-z-10 bg-primary h-52 w-full sm:h-80 sm:w-full rounded-l-full absolute -right-28 md:-right-48 -bottom-8"
          ></div>
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
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { loginUser } from '../../api/user'
import userAuth from '../../services/userAuth'
import { startBanDetection } from '../../utils/banDetector'
import { getLocale, setLocale, type SupportedLocale } from '../../services/locale'

const router = useRouter()

const messages = {
  zh: {
    brand: '济图通',
    navFeatures: '功能',
    navAbout: '关于',
    navHelp: '帮助',
    register: '注册',
    welcomeTitle: '欢迎回来',
    welcomeSubtitle: '登录以探索同济校园的每个角落',
    phoneLabel: '手机号',
    phonePlaceholder: '请输入手机号',
    passwordLabel: '密码',
    passwordPlaceholder: '请输入密码',
    rememberMe: '记住我',
    forgotPassword: '忘记密码？',
    loggingIn: '登录中...',
    login: '登录',
    or: '或',
    noAccount: '还没有账号？',
    signUpNow: '立即注册',
    thirdPartyLogin: '使用第三方账号登录',
    illustrationAlt: '济图通插画',
    phoneRequired: '请输入手机号',
    phoneInvalid: '请输入正确的手机号格式',
    passwordRequired: '请输入密码',
    passwordTooShort: '密码长度至少为6位',
    loginFailed: '登录失败，请稍后重试',
  },
  en: {
    brand: 'Jitutong',
    navFeatures: 'Features',
    navAbout: 'About',
    navHelp: 'Help',
    register: 'Sign Up',
    welcomeTitle: 'Welcome back',
    welcomeSubtitle: 'Log in to explore every corner of Tongji campus',
    phoneLabel: 'Phone',
    phonePlaceholder: 'Enter phone number',
    passwordLabel: 'Password',
    passwordPlaceholder: 'Enter password',
    rememberMe: 'Remember me',
    forgotPassword: 'Forgot password?',
    loggingIn: 'Logging in...',
    login: 'Log in',
    or: 'or',
    noAccount: "Don't have an account?",
    signUpNow: 'Sign up now',
    thirdPartyLogin: 'Sign in with third-party account',
    illustrationAlt: 'Jitutong illustration',
    phoneRequired: 'Please enter phone number',
    phoneInvalid: 'Please enter a valid phone number',
    passwordRequired: 'Please enter password',
    passwordTooShort: 'Password must be at least 6 characters',
    loginFailed: 'Login failed, please try again later',
  },
}

const lang = ref<SupportedLocale>('zh')
const t = (key: keyof typeof messages.zh) => messages[lang.value][key]

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
    content: '如需帮助，请联系我们的客服团队。',
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

// 移动菜单状态
const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// 表单数据
const loginForm = ref({
  phone: '',
  password: '',
  remember: false,
})

// 错误信息
const phoneError = ref('')
const passwordError = ref('')

// 状态
const isLoading = ref(false)
const showPassword = ref(false)

// 手机号验证
const phoneRegex = /^1[3-9]\d{9}$/
const isPhoneValid = computed(() => phoneRegex.test(loginForm.value.phone))

// 验证表单
const validateForm = (): boolean => {
  phoneError.value = ''
  passwordError.value = ''

  if (!loginForm.value.phone) {
    phoneError.value = t('phoneRequired')
    return false
  }

  if (!isPhoneValid.value) {
    phoneError.value = t('phoneInvalid')
    return false
  }

  if (!loginForm.value.password) {
    passwordError.value = t('passwordRequired')
    return false
  }
  if (loginForm.value.password.length < 6) {
    passwordError.value = t('passwordTooShort')
    return false
  }

  return true
}

// 处理登录
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    // 检查是否已有其他用户登录
    const existingUser = localStorage.getItem('user')
    if (existingUser) {
      try {
        const user = JSON.parse(existingUser)
        // 如果已有用户且不是当前要登录的用户
        if (user.phone && user.phone !== loginForm.value.phone) {
          const confirmSwitch = confirm(
            `检测到已有用户 ${user.phone} 登录。\n\n` +
            `登录新账号将会影响所有打开的标签页，` +
            `其他标签页也会切换到新账号。\n\n` +
            `是否继续登录？`
          )
          if (!confirmSwitch) {
            isLoading.value = false
            return
          }
        }
      } catch (e) {
        // 忽略 JSON 解析错误
      }
    }

    const credentials = {
      phone: loginForm.value.phone,
      password: loginForm.value.password,
      remember: loginForm.value.remember,
    }

    const response = await loginUser(credentials)
    
    // 清除旧的 session，再设置新的 session
    userAuth.clearSession()
    userAuth.setSession(response)
    
    // 启动封禁检测（每 5 秒检测一次）
    startBanDetection(5)
    
    router.push({ name: 'UserProfile' })
  } catch (error: any) {
    console.error('登录失败:', error)
    
    // 将英文错误信息转换为中文
    let message = error?.message || t('loginFailed')
    
    // 常见错误信息映射
    const errorMap: Record<string, string> = {
      'Invalid phone or password': '手机号或密码错误',
      'Invalid credentials': '手机号或密码错误',
      'User not found': '用户不存在',
      'Incorrect password': '密码错误',
      'Account is disabled': '账号已被禁用',
      'Too many login attempts': '登录尝试次数过多，请稍后再试',
    }
    
    // 尝试匹配错误信息
    for (const [enMsg, zhMsg] of Object.entries(errorMap)) {
      if (message.includes(enMsg)) {
        message = zhMsg
        break
      }
    }
    
    passwordError.value = message
  } finally {
    isLoading.value = false
  }
}
</script>
