import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router'
import './style.css'
import App from './App.vue'
import { useAuthStore } from '@/store/auth'

// Set terminal ID header for multi-terminal caching and tracking
let terminalId = localStorage.getItem('terminal_id')
if (!terminalId) {
  terminalId = 'terminal_' + Math.random().toString(36).substr(2, 9)
  localStorage.setItem('terminal_id', terminalId)
}
axios.defaults.headers.common['X-Terminal-Id'] = terminalId

// Restore Authorization header if token exists to prevent 401s on browser refresh
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Global Axios Interceptor to catch 401 unauthorized errors
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      if (router.currentRoute.value.name !== 'login') {
        router.push({ name: 'login' })
      }
    }
    return Promise.reject(error)
  }
)

app.mount('#app')


