<template>
  <div class="layout-container">
    <!-- Permanent Left Navigation Rail -->
    <AppSidebar @logout="handleLogout" />

    <!-- Main Workspace Area -->
    <div class="workspace-wrapper">
      <!-- Top Integrated Header -->
      <AppHeader 
        :title="currentPageTitle"
        :subtitle="currentPageSubtitle"
        :cashierName="authStore.user?.username || 'Cashier'"
        :cashierRole="authStore.user?.role?.toUpperCase() || 'USER'"
        :isOnline="cartStore.isOnline"
        :pendingSyncCount="cartStore.offlineSalesQueue.length"
        :isSyncing="cartStore.isSyncing"
        @sync="cartStore.syncOfflineSales"
      />

      <!-- Dynamic Page Body -->
      <main class="page-body">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Mandatory Password Change Modal Overlay -->
    <div class="mandatory-password-overlay" v-if="authStore.user?.must_change_password">
      <div class="password-modal premium-card animate-enter">
        <div class="password-modal-header">
          <Key class="modal-title-icon" />
          <h2>Change Password Required</h2>
          <p>For security, you must update your temporary password before accessing the system.</p>
        </div>
        <form @submit.prevent="submitPasswordChange" class="password-form">
          <div class="form-group">
            <label>New Password *</label>
            <input 
              type="password" 
              v-model="newPassword" 
              placeholder="Min. 4 characters" 
              class="pos-input" 
              required 
              minlength="4"
            />
          </div>
          <div class="form-group">
            <label>Confirm Password *</label>
            <input 
              type="password" 
              v-model="confirmPassword" 
              placeholder="Confirm new password" 
              class="pos-input" 
              required
            />
            <span class="pwd-error" v-if="passwordMismatch">Passwords do not match</span>
          </div>
          <button type="submit" class="pos-btn pos-btn-accent full-width" :disabled="submitting || passwordMismatch">
            Update Password & Access POS
          </button>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useCartStore } from '@/store/cart'
import { useProductsStore } from '@/store/products'
import { Key } from 'lucide-vue-next'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const productsStore = useProductsStore()
const route = useRoute()
const router = useRouter()

// Password change fields
const newPassword = ref('')
const confirmPassword = ref('')
const submitting = ref(false)

const passwordMismatch = computed(() => {
  if (!confirmPassword.value) return false
  return newPassword.value !== confirmPassword.value
})

const submitPasswordChange = async () => {
  if (passwordMismatch.value) return
  submitting.value = true
  try {
    await axios.post('/api/auth/change-password', {
      new_password: newPassword.value
    })
    alert('Password updated successfully! Welcome to ApexPOS.')
    if (authStore.user) {
      authStore.user.must_change_password = false
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update password')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  cartStore.initConnection()
  
  if (typeof EventSource !== 'undefined') {
    const eventSource = new EventSource('/api/products/events')
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.event === 'invalidate') {
          console.log('Catalog update nudge received from server. Reloading product list...')
          productsStore.fetchProducts({}, true)
        }
      } catch (err) {
        console.error('Failed to parse SSE event', err)
      }
    }
    eventSource.onerror = (err) => {
      console.warn('SSE catalog stream lost. Will reconnect automatically.', err)
    }
  }
})

const currentPageTitle = computed(() => {
  const name = route.name
  if (name === 'dashboard') return 'Management Command Center'
  if (name === 'pos') return 'Sales Register Terminal'
  if (name === 'products') return 'Inventory Catalog Manager'
  if (name === 'reports') return 'Executive Business Analytics'
  if (name === 'admin') return 'System Administration Panel'
  return 'ApexPOS'
})

const currentPageSubtitle = computed(() => {
  const name = route.name
  if (name === 'dashboard') return 'Monitor cashier shifts, cash drawers, and system alerts.'
  if (name === 'pos') return 'Add products, apply discount coupons, and complete checkouts.'
  if (name === 'products') return 'Browse, create, and modify catalog inventory and UOM formats.'
  if (name === 'reports') return 'Review revenue metrics, category sales, and cashier counts.'
  if (name === 'admin') return 'Manage store branches/sucursales, configure user access, and register staff.'
  return 'Modern retail point-of-sale platform.'
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--bg-app);
}

.workspace-wrapper {
  margin-left: 85px; /* Offset for sidebar width */
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.page-body {
  padding: 32px;
  flex-grow: 1;
  background-color: var(--bg-app);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .page-body {
    padding: 16px;
  }
}

/* Slide Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Mandatory password overlay style */
.mandatory-password-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(17, 17, 17, 0.8);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-modal {
  background-color: #ffffff;
  width: 100%;
  max-width: 440px;
  padding: 32px;
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.password-modal.animate-enter {
  animation: modal-zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-zoom {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.password-modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.modal-title-icon {
  width: 48px;
  height: 48px;
  color: var(--accent-lime);
  background-color: rgba(184, 241, 90, 0.15);
  padding: 10px;
  border-radius: 50%;
  margin-bottom: 16px;
}

.password-modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.password-modal-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.pwd-error {
  font-size: 11px;
  color: #ef4444;
  margin-top: 2px;
}

.full-width {
  width: 100%;
}
</style>
