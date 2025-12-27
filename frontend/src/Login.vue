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
          <span class="text-xl font-heading font-bold text-dark-blue hidden sm:block">济图通</span>
        </div>

        <nav class="flex items-center">
          <!-- Desktop Menu -->
          <ul
            class="space-x-6 lg:space-x-10 font-heading font-medium items-center hidden md:flex"
          >
            <li
              class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer"
            >
              功能
            </li>
            <li
              class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer"
            >
              关于
            </li>
            <li
              class="uppercase text-sm hover:text-primary transition duration-200 cursor-pointer"
            >
              帮助
            </li>
            <li
              class="uppercase bg-secondary px-5 py-2 text-white text-sm rounded shadow-md hover:bg-white border-2 border-transparent hover:border-secondary hover:text-secondary cursor-pointer transition duration-200"
            >
              注册
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
        <div
          v-show="mobileMenuOpen"
          class="md:hidden pb-4 border-t border-gray-200 mb-4"
        >
          <ul class="uppercase text-sm font-medium space-y-2 pt-4">
            <li
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              功能
            </li>
            <li
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              关于
            </li>
            <li
              class="py-2.5 px-4 rounded-lg hover:bg-gray-100 hover:text-primary transition-colors cursor-pointer"
            >
              帮助
            </li>
            <li class="pt-2">
              <button
                class="w-full bg-secondary px-5 py-2.5 text-white rounded-lg shadow-md hover:bg-secondary/90 transition-colors"
              >
                注册
              </button>
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
              欢迎回来
            </h1>
            <p class="text-lg lg:text-xl text-gray-600">
              登录以探索同济校园的每个角落
            </p>
          </div>

          <!-- Login Card -->
          <div class="bg-white rounded-2xl shadow-soft p-8">
        <!-- Tab Switcher -->
        <div class="flex space-x-2 mb-6 bg-gray-100 rounded-lg p-1">
          <button
            @click="loginMode = 'password'"
            :class="[
              'flex-1 py-2.5 rounded-md font-medium transition-all duration-200',
              loginMode === 'password'
                ? 'bg-white text-primary shadow-sm'
                : 'text-gray-600 hover:text-gray-900',
            ]"
          >
            密码登录
          </button>
          <button
            @click="loginMode = 'code'"
            :class="[
              'flex-1 py-2.5 rounded-md font-medium transition-all duration-200',
              loginMode === 'code'
                ? 'bg-white text-primary shadow-sm'
                : 'text-gray-600 hover:text-gray-900',
            ]"
          >
            验证码登录
          </button>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Phone Number Input -->
          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              手机号
            </label>
            <div class="relative">
              <input
                id="phone"
                type="tel"
                v-model="loginForm.phone"
                @input="phoneError = ''"
                placeholder="请输入手机号"
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

          <!-- Password Input (Password Mode) -->
          <div v-if="loginMode === 'password'">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <div class="relative">
              <input
                id="password"
                :type="showPassword ? 'text' : 'password'"
                v-model="loginForm.password"
                @input="passwordError = ''"
                placeholder="请输入密码"
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
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
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

          <!-- Verification Code Input (Code Mode) -->
          <div v-if="loginMode === 'code'">
            <label for="code" class="block text-sm font-medium text-gray-700 mb-2">
              验证码
            </label>
            <div class="flex space-x-3">
              <div class="relative flex-1">
                <input
                  id="code"
                  type="text"
                  v-model="loginForm.code"
                  @input="codeError = ''"
                  placeholder="请输入验证码"
                  maxlength="6"
                  class="input-field pl-10"
                  :class="{ 'border-secondary focus:ring-secondary': codeError }"
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
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <button
                type="button"
                @click="sendVerificationCode"
                :disabled="countdown > 0 || !isPhoneValid"
                class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 whitespace-nowrap"
                :class="
                  countdown > 0 || !isPhoneValid
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : 'bg-primary text-white hover:bg-primary/90'
                "
              >
                {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
              </button>
            </div>
            <p v-if="codeError" class="mt-2 text-sm text-secondary flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
              </svg>
              {{ codeError }}
            </p>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div v-if="loginMode === 'password'" class="flex items-center justify-between">
            <label class="flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="loginForm.remember"
                class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary cursor-pointer"
              />
              <span class="ml-2 text-sm text-gray-700">记住我</span>
            </label>
            <a href="#" class="text-sm text-primary hover:text-primary/80 font-medium transition-colors">
              忘记密码？
            </a>
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
              登录中...
            </span>
            <span v-else>登录</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-white text-gray-500">或</span>
          </div>
        </div>

            <!-- Register Link -->
            <div class="text-center">
              <p class="text-sm text-gray-600">
                还没有账号？
                <a href="#" class="text-primary hover:text-primary/80 font-medium transition-colors">
                  立即注册
                </a>
              </p>
            </div>
          </div>

          <!-- Third-party Login -->
          <div class="mt-6">
            <p class="text-center text-sm text-gray-600 mb-4">使用第三方账号登录</p>
            <div class="flex justify-center space-x-4">
              <button
                class="w-12 h-12 rounded-full bg-white border border-gray-200 hover:border-primary hover:shadow-md transition-all flex items-center justify-center group"
              >
                <svg
                  class="w-5 h-5 text-gray-600 group-hover:text-primary transition-colors"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 008.44-9.9c0-5.53-4.5-10.02-10-10.02z"
                  />
                </svg>
              </button>
              <button
                class="w-12 h-12 rounded-full bg-white border border-gray-200 hover:border-primary hover:shadow-md transition-all flex items-center justify-center group"
              >
                <svg
                  class="w-5 h-5 text-gray-600 group-hover:text-primary transition-colors"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M22.46 6c-.85.38-1.78.64-2.75.76 1-.6 1.76-1.55 2.12-2.68-.93.55-1.96.95-3.06 1.17-.88-.94-2.13-1.53-3.51-1.53-2.66 0-4.81 2.16-4.81 4.81 0 .38.04.75.13 1.1-4-.2-7.55-2.12-9.92-5.04-.42.72-.66 1.55-.66 2.44 0 1.67.85 3.14 2.14 4-.79-.03-1.53-.24-2.18-.6v.06c0 2.33 1.66 4.28 3.87 4.72-.4.11-.83.17-1.27.17-.31 0-.62-.03-.92-.08.62 1.94 2.42 3.35 4.55 3.39-1.67 1.31-3.77 2.09-6.05 2.09-.39 0-.78-.02-1.17-.07 2.18 1.4 4.77 2.21 7.55 2.21 9.06 0 14-7.5 14-14 0-.21 0-.42-.02-.63.96-.69 1.8-1.56 2.46-2.55z"
                  />
                </svg>
              </button>
              <button
                class="w-12 h-12 rounded-full bg-white border border-gray-200 hover:border-accent hover:shadow-md transition-all flex items-center justify-center group"
              >
                <svg
                  class="w-5 h-5 text-gray-600 group-hover:text-accent transition-colors"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M12.018 6.537c-2.5 0-4.5 1.5-4.5 4.5s2 4.5 4.5 4.5 4.5-1.5 4.5-4.5-2-4.5-4.5-4.5zm0 7.5c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3-1.3 3-3 3z"
                  />
                  <circle cx="16.518" cy="6.037" r="1.5" />
                  <path
                    d="M20.018 2.037h-8c-3.3 0-6 2.7-6 6v8c0 3.3 2.7 6 6 6h8c3.3 0 6-2.7 6-6v-8c0-3.3-2.7-6-6-6zm4.5 14c0 2.5-2 4.5-4.5 4.5h-8c-2.5 0-4.5-2-4.5-4.5v-8c0-2.5 2-4.5 4.5-4.5h8c2.5 0 4.5 2 4.5 4.5v8z"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Right Side - Illustration -->
        <div class="relative order-1 lg:order-none mb-12 lg:mb-0 lg:-mr-10">
          <div class="relative z-10">
            <img class="w-full" src="/illustration-hero.svg" alt="济图通插画" />
          </div>
          <!-- Background Decoration -->
          <div
            class="-z-10 bg-primary h-52 w-full sm:h-80 sm:w-full rounded-l-full absolute -right-28 md:-right-48 -bottom-8"
          ></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 移动菜单状态
const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// 登录模式
const loginMode = ref<'password' | 'code'>('password')

// 表单数据
const loginForm = ref({
  phone: '',
  password: '',
  code: '',
  remember: false,
})

// 错误信息
const phoneError = ref('')
const passwordError = ref('')
const codeError = ref('')

// 状态
const isLoading = ref(false)
const showPassword = ref(false)
const countdown = ref(0)

// 手机号验证
const phoneRegex = /^1[3-9]\d{9}$/
const isPhoneValid = computed(() => phoneRegex.test(loginForm.value.phone))

// 验证表单
const validateForm = (): boolean => {
  phoneError.value = ''
  passwordError.value = ''
  codeError.value = ''

  if (!loginForm.value.phone) {
    phoneError.value = '请输入手机号'
    return false
  }

  if (!isPhoneValid.value) {
    phoneError.value = '请输入正确的手机号格式'
    return false
  }

  if (loginMode.value === 'password') {
    if (!loginForm.value.password) {
      passwordError.value = '请输入密码'
      return false
    }
    if (loginForm.value.password.length < 6) {
      passwordError.value = '密码长度至少为6位'
      return false
    }
  } else {
    if (!loginForm.value.code) {
      codeError.value = '请输入验证码'
      return false
    }
    if (loginForm.value.code.length !== 6) {
      codeError.value = '验证码为6位数字'
      return false
    }
  }

  return true
}

// 发送验证码
const sendVerificationCode = async () => {
  if (!isPhoneValid.value) {
    phoneError.value = '请输入正确的手机号'
    return
  }

  // 模拟发送验证码
  console.log('发送验证码到:', loginForm.value.phone)
  
  // 开始倒计时
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)

  // 模拟API调用
  alert(`验证码已发送到 ${loginForm.value.phone}`)
}

// 模拟登录API
const performLogin = (credentials: any) => {
  return new Promise((resolve) => {
    console.log('登录凭证:', credentials)
    setTimeout(() => {
      // 模拟成功登录
      localStorage.setItem('userToken', 'mock-token-' + Date.now())
      resolve({ success: true })
    }, 1500)
  })
}

// 处理登录
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const credentials = {
      phone: loginForm.value.phone,
      ...(loginMode.value === 'password'
        ? { password: loginForm.value.password }
        : { code: loginForm.value.code }),
      remember: loginForm.value.remember,
    }

    const response = await performLogin(credentials)
    
    // 登录成功，跳转到个人中心
    router.push({ name: 'UserProfile' })
  } catch (error) {
    console.error('登录失败:', error)
    if (loginMode.value === 'password') {
      passwordError.value = '手机号或密码错误'
    } else {
      codeError.value = '验证码错误'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

