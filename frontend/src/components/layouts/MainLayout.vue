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
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCartStore } from '@/store/cart'
import { useProductsStore } from '@/store/products'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const productsStore = useProductsStore()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  cartStore.initConnection()
  
  if (typeof EventSource !== 'undefined') {
    const eventSource = new EventSource('/api/products/events')
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.event === 'invalidate') {
          console.log('Catalog update nudge received from server. Reloading product list...')
          productsStore.fetchProducts()
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
  return 'ApexPOS'
})

const currentPageSubtitle = computed(() => {
  const name = route.name
  if (name === 'dashboard') return 'Monitor cashier shifts, cash drawers, and system alerts.'
  if (name === 'pos') return 'Add products, apply discount coupons, and complete checkouts.'
  if (name === 'products') return 'Browse, create, and modify catalog inventory and UOM formats.'
  if (name === 'reports') return 'Review revenue metrics, category sales, and cashier counts.'
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
</style>
