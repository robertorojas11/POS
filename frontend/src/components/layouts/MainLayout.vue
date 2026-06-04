<template>
  <div class="layout-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="brand">
        <span class="logo-icon">⚡</span>
        <span class="brand-name">ApexPOS</span>
      </div>
      
      <nav class="nav-links">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="9" rx="1" />
            <rect x="14" y="3" width="7" height="5" rx="1" />
            <rect x="14" y="12" width="7" height="9" rx="1" />
            <rect x="3" y="16" width="7" height="5" rx="1" />
          </svg>
          Dashboard
        </router-link>
        
        <router-link to="/pos" class="nav-item" active-class="active">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="4" width="20" height="8" rx="2" ry="2" />
            <path d="M12 4v8M2 18h20M6 18v-2M10 18v-2M14 18v-2M18 18v-2" />
          </svg>
          Register (POS)
        </router-link>
        
        <router-link to="/products" class="nav-item" active-class="active">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
            <line x1="12" y1="22.08" x2="12" y2="12" />
          </svg>
          Products
        </router-link>
        
        <router-link to="/reports" class="nav-item" active-class="active">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          Reports
        </router-link>
      </nav>
      
      <div class="user-profile">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-details">
          <span class="user-name">{{ authStore.user?.username || 'Cashier' }}</span>
          <span class="user-role">{{ authStore.user?.role?.toUpperCase() || 'USER' }}</span>
        </div>
      </div>
    </aside>

    <!-- Main Section -->
    <div class="main-content">
      <header class="topbar">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        <div class="header-right" style="display: flex; align-items: center;">
          <!-- Connection Status Indicator -->
          <div class="connection-status" :class="{ 'online': cartStore.isOnline, 'offline': !cartStore.isOnline }">
            <span class="status-dot"></span>
            <span class="status-text">{{ cartStore.isOnline ? 'Online' : 'Offline' }}</span>
            <span v-if="cartStore.offlineSalesQueue.length > 0" class="pending-badge">
              {{ cartStore.offlineSalesQueue.length }} Unsynced
            </span>
          </div>

          <button v-if="cartStore.offlineSalesQueue.length > 0 && cartStore.isOnline" @click="cartStore.syncOfflineSales" class="sync-btn" :disabled="cartStore.isSyncing">
            <svg class="sync-icon" :class="{ 'rotating': cartStore.isSyncing }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
            {{ cartStore.isSyncing ? 'Syncing...' : 'Sync' }}
          </button>

          <button @click="handleLogout" class="logout-btn">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
            </svg>
            Logout
          </button>
        </div>
      </header>

      <main class="page-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCartStore } from '@/store/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  cartStore.initConnection()
})

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U'
})

const currentPageTitle = computed(() => {
  const name = route.name
  if (name === 'dashboard') return 'Overview Dashboard'
  if (name === 'pos') return 'Sales Register'
  if (name === 'products') return 'Inventory Catalog'
  if (name === 'reports') return 'Sales Reports & KPI'
  return 'ApexPOS'
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
}

.sidebar {
  width: 260px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: fixed;
  height: 100vh;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
  padding-left: 8px;
}

.logo-icon {
  font-size: 1.5rem;
  background: var(--bg-tertiary);
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.brand-name {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #fff;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-grow: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-item:hover {
  background-color: var(--bg-tertiary);
  color: #fff;
}

.nav-item.active {
  background-color: var(--accent-primary);
  color: #fff;
}

.icon {
  width: 18px;
  height: 18px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.user-avatar {
  width: 40px;
  height: 40px;
  background-color: var(--accent-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.main-content {
  margin-left: 260px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  height: 70px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.logout-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: var(--accent-danger);
  color: var(--accent-danger);
}

.logout-icon {
  width: 16px;
  height: 16px;
}

.page-body {
  padding: 32px;
  flex-grow: 1;
  background-color: var(--bg-primary);
}

@media (max-width: 1024px) {
  .sidebar {
    width: 80px;
    padding: 24px 8px;
  }
  .brand-name, .user-details, .logout-btn span {
    display: none;
  }
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  .main-content {
    margin-left: 80px;
  }
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  font-size: 0.85rem;
  font-weight: 500;
  margin-right: 12px;
}

.connection-status.online {
  color: #10b981;
}

.connection-status.offline {
  color: #f59e0b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.pending-badge {
  background-color: #ef4444;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 4px;
  animation: pulse 2s infinite;
}

.sync-btn {
  background: var(--accent-primary);
  border: none;
  color: #fff;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-fast);
  margin-right: 12px;
}

.sync-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.sync-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-icon {
  width: 14px;
  height: 14px;
}

.rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
