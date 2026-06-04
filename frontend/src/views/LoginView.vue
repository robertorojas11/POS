<template>
  <div class="login-layout">
    <!-- Left Panel: Illustration & Welcome -->
    <div class="visual-panel">
      <div class="visual-content">
        <div class="brand-group">
          <div class="brand-icon-box">
            <Package class="brand-icon" />
          </div>
          <span class="brand-name">ApexPOS</span>
        </div>
        
        <div class="promo-text">
          <h1>Run your entire retail operation from a single, fast interface.</h1>
          <p>Deploy terminal registers instantly, manage fractional inventory, track drawer turns, and continue sales seamlessly even when offline.</p>
        </div>
        
        <div class="pos-art-canvas">
          <div class="art-terminal-screen">
            <div class="art-topbar">
              <div class="art-dot green"></div>
              <div class="art-dot yellow"></div>
              <div class="art-dot red"></div>
            </div>
            <div class="art-body-grid">
              <div class="art-sidebar">
                <div class="art-menu-item active"></div>
                <div class="art-menu-item"></div>
                <div class="art-menu-item"></div>
              </div>
              <div class="art-main">
                <div class="art-kpi-row">
                  <div class="art-kpi"></div>
                  <div class="art-kpi"></div>
                  <div class="art-kpi"></div>
                </div>
                <div class="art-chart-box">
                  <div class="art-bar" style="height: 40%"></div>
                  <div class="art-bar" style="height: 70%"></div>
                  <div class="art-bar" style="height: 50%"></div>
                  <div class="art-bar" style="height: 90%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="visual-footer">
        <span>© 2026 ApexPOS Systems Inc. All rights reserved.</span>
      </div>
    </div>
    
    <!-- Right Panel: Auth Form -->
    <div class="form-panel">
      <div class="auth-card premium-card">
        <div class="card-header-group">
          <h2>Cashier Turn Sign In</h2>
          <p>Enter your credentials to unlock this terminal register.</p>
        </div>

        <form @submit.prevent="submitLogin" class="auth-form">
          <div class="error-toast" v-if="authStore.error">
            <AlertCircle class="error-icon" />
            <span>{{ authStore.error }}</span>
          </div>

          <div class="form-group">
            <label for="username" class="pos-label">Cashier ID / Username</label>
            <div class="input-icon-wrapper">
              <User class="input-icon" />
              <input 
                type="text" 
                id="username" 
                v-model="username" 
                class="pos-input with-left-icon" 
                placeholder="e.g. admin or cashier1" 
                required 
                autocomplete="username"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password" class="pos-label">Password</label>
            <div class="input-icon-wrapper">
              <Lock class="input-icon" />
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                class="pos-input with-left-icon with-right-icon" 
                placeholder="••••••••" 
                required 
                autocomplete="current-password"
              />
              <button 
                type="button" 
                class="password-toggle-btn"
                @click="showPassword = !showPassword"
                title="Toggle password visibility"
              >
                <Eye v-if="!showPassword" class="toggle-icon" />
                <EyeOff v-else class="toggle-icon" />
              </button>
            </div>
          </div>

          <div class="session-remember">
            <label class="checkbox-container">
              <input type="checkbox" v-model="rememberSession" />
              <span class="checkmark"></span>
              Remember terminal session
            </label>
          </div>

          <button type="submit" class="pos-btn pos-btn-accent auth-submit-btn" :disabled="authStore.loading">
            <span v-if="authStore.loading">Authenticating...</span>
            <span v-else>Sign In</span>
          </button>
        </form>
        
        <div class="dev-credentials">
          <span class="credentials-title">Seeded Accounts for Testing</span>
          <div class="credentials-grid">
            <div class="credential-item">
              <span class="role-tag admin">Admin</span>
              <code>admin / admin</code>
            </div>
            <div class="credential-item">
              <span class="role-tag operator">Cashier</span>
              <code>cashier1 / securepassword</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { Package, User, Lock, Eye, EyeOff, AlertCircle } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberSession = ref(true)

const submitLogin = async () => {
  const success = await authStore.login(username.value, password.value)
  if (success) {
    router.push({ name: 'dashboard' })
  }
}
</script>

<style scoped>
.login-layout {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--bg-app);
}

/* Left Panel Style */
.visual-panel {
  flex: 1.2;
  background-color: #111111;
  color: #ffffff;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

@media (max-width: 900px) {
  .visual-panel {
    display: none;
  }
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon-box {
  width: 40px;
  height: 40px;
  background-color: var(--accent-lime);
  color: var(--bg-sidebar);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon {
  width: 22px;
  height: 22px;
}

.brand-name {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.promo-text {
  max-width: 520px;
  margin-top: auto;
  margin-bottom: 40px;
}

.promo-text h1 {
  font-size: 2.35rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 16px;
}

.promo-text p {
  font-size: 1rem;
  color: #9ca3af;
  line-height: 1.5;
}

.pos-art-canvas {
  height: 240px;
  width: 100%;
  display: flex;
  align-items: flex-end;
}

.art-terminal-screen {
  background-color: #1e1e1e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px 12px 0 0;
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  padding: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.art-topbar {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.art-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.art-dot.green { background-color: #10b981; }
.art-dot.yellow { background-color: #f59e0b; }
.art-dot.red { background-color: #ff5e5e; }

.art-body-grid {
  display: flex;
  flex-grow: 1;
  gap: 8px;
}

.art-sidebar {
  width: 40px;
  background-color: #111111;
  border-radius: 6px;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.art-menu-item {
  width: 20px;
  height: 20px;
  background-color: #2e2e2e;
  border-radius: 4px;
}

.art-menu-item.active {
  background-color: var(--accent-lime);
}

.art-main {
  flex-grow: 1;
  background-color: #242424;
  border-radius: 6px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.art-kpi-row {
  display: flex;
  gap: 8px;
}

.art-kpi {
  flex: 1;
  height: 24px;
  background-color: #2d2d2d;
  border-radius: 4px;
}

.art-chart-box {
  flex-grow: 1;
  background-color: #2d2d2d;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  padding: 8px;
  gap: 12px;
  justify-content: center;
}

.art-bar {
  width: 14px;
  background-color: var(--accent-lime);
  border-radius: 2px 2px 0 0;
  opacity: 0.8;
}

.visual-footer {
  font-size: 0.8rem;
  color: #4b5563;
}

/* Right Panel Style */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

@media (max-width: 900px) {
  .form-panel {
    flex: 1;
    background-color: var(--bg-app);
  }
}

.auth-card {
  width: 480px;
  max-width: 100%;
  padding: 40px !important;
}

.card-header-group {
  margin-bottom: 32px;
}

.card-header-group h2 {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.card-header-group p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-top: 6px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-toast {
  background-color: rgba(255, 94, 94, 0.08);
  border: 1px solid var(--accent-danger);
  color: var(--accent-danger);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pos-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.pos-input.with-left-icon {
  padding-left: 44px;
}

.pos-input.with-right-icon {
  padding-right: 44px;
}

.password-toggle-btn {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  padding: 0;
}

.password-toggle-btn:hover {
  color: var(--text-primary);
}

.toggle-icon {
  width: 18px;
  height: 18px;
}

.session-remember {
  display: flex;
  align-items: center;
}

/* Custom Checkbox */
.checkbox-container {
  display: block;
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 1px;
  left: 0;
  height: 18px;
  width: 18px;
  background-color: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.checkbox-container:hover input ~ .checkmark {
  border-color: var(--text-muted);
}

.checkbox-container input:checked ~ .checkmark {
  background-color: var(--accent-lime);
  border-color: var(--accent-lime-hover);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 6px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid var(--accent-lime-text);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.auth-submit-btn {
  width: 100%;
  height: 50px;
  font-size: 1rem;
  margin-top: 10px;
}

.dev-credentials {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.credentials-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.credentials-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.credential-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f9fafb;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid #f3f4f6;
  font-size: 0.8rem;
}

.role-tag {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.role-tag.admin {
  background-color: rgba(184, 241, 90, 0.2);
  color: #6d9620;
}

.role-tag.operator {
  background-color: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
}

code {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
