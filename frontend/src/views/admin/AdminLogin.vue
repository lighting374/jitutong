<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import auth from '../../services/auth'
import adminApi from '../../api/admin'

const router = useRouter()
const username = ref('')
const password = ref('')
const remember = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    console.log('开始登录...', { username: username.value })
    const result = await auth.login(username.value, password.value)
    console.log('登录成功，返回数据:', result)
    
    if (remember.value) localStorage.setItem('admin_remember', '1')
    else localStorage.removeItem('admin_remember')
    
    // 确保用户信息已保存
    const currentUser = auth.getUser()
    console.log('当前用户信息:', currentUser)
    
    if (!currentUser) {
      throw new Error('登录成功但未能获取用户信息')
    }
    
    console.log('准备跳转到 dashboard...')
    await router.push('/admin/dashboard')
    console.log('跳转完成')
  } catch (e: any) {
    console.error('登录错误:', e)
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}

function onKeyup(e: KeyboardEvent) {
  if (e.key === 'Enter') submit()
}

// 如果浏览器已有 token，不直接跳转，先向后端校验 token 是否仍可用
onMounted(async () => {
  if (!auth.isAuthenticated()) return
  try {
    await adminApi.getAdminInfo()
    // token 有效
    router.replace('/admin/dashboard')
  } catch (err) {
    // 若校验失败（如后端不可达或返回 401），清理本地状态并停留登录页
    auth.logout()
    // 不设置 error，用户仍看到登录表单
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white p-6 rounded-lg shadow">
      <h2 class="text-2xl font-bold mb-4">管理员登录</h2>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700">管理员账号</label>
          <input v-model="username" @keyup="onKeyup" class="mt-1 block w-full rounded border px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">密码</label>
          <div class="relative">
            <input v-model="password" @keyup="onKeyup" :type="showPassword ? 'text' : 'password'" class="mt-1 block w-full rounded border px-3 py-2" />
            <button type="button" @click="showPassword = !showPassword" class="absolute right-2 top-2 text-sm text-gray-600">
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <div class="flex items-center">
          <input id="remember" type="checkbox" v-model="remember" class="mr-2" />
          <label for="remember" class="text-sm text-gray-600">记住我</label>
        </div>

        <div>
          <button @click="submit" :disabled="loading" class="w-full bg-primary text-white py-2 rounded">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-primary { background-color: #2563eb; }
</style>
