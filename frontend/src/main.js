import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router'
import './style.css'
import App from './App.vue'

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

app.mount('#app')

