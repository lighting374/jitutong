import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/style.css'
import userAuth from './services/userAuth'
import { startBanDetection } from './utils/banDetector'
import { setupApiInterceptor } from './utils/apiInterceptor'

const app = createApp(App)

app.use(router)

// 设置 API 拦截器
setupApiInterceptor()

// 如果用户已登录，启动封禁检测
if (userAuth.isAuthenticated()) {
  // 每 5 秒检测一次
  startBanDetection(5)
}

app.mount('#app')
