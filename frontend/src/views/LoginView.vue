<template>
  <div class="login-container">
    <div class="login-box pos-card">
      <div class="header">
        <span class="logo">⚡</span>
        <h2>Welcome to ApexPOS</h2>
        <p>Sign in to launch your register terminal</p>
      </div>

      <form @submit.prevent="submitLogin" class="login-form">
        <div class="error-banner" v-if="authStore.error">
          {{ authStore.error }}
        </div>

        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            class="pos-input" 
            placeholder="e.g. cashier1" 
            required 
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            class="pos-input" 
            placeholder="••••••••" 
            required 
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="pos-btn pos-btn-primary full-width" :disabled="authStore.loading">
          <span v-if="authStore.loading">Authenticating...</span>
          <span v-else>Access Register</span>
        </button>
      </form>
      
      <div class="demo-info">
        <p><strong>Demo Access:</strong> admin / securepassword</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

const submitLogin = async () => {
  const success = await authStore.login(username.value, password.value)
  if (success) {
    router.push({ name: 'dashboard' })
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image: radial-gradient(circle at top right, rgba(79, 70, 229, 0.1), transparent);
}

.login-box {
  width: 420px;
  max-width: 90%;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  font-size: 2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
}

.header h2 {
  font-size: 1.6rem;
  color: #fff;
  margin-bottom: 6px;
}

.header p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-banner {
  background-color: rgba(239, 68, 68, 0.15);
  border: 1px solid var(--accent-danger);
  color: #fca5a5;
  padding: 12px;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  text-align: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.full-width {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
}

.demo-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  font-size: 0.85rem;
  color: var(--text-muted);
  text-align: center;
}
</style>
