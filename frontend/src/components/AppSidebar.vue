<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="logo-box">
        <Package class="logo-icon" />
      </div>
    </div>
    
    <nav class="nav-links">
      <router-link to="/dashboard" class="nav-item" active-class="active" title="Dashboard">
        <div class="icon-container">
          <LayoutDashboard class="icon" />
        </div>
      </router-link>
      
      <router-link to="/pos" class="nav-item" active-class="active" title="POS Register">
        <div class="icon-container">
          <Monitor class="icon" />
        </div>
      </router-link>
      
      <router-link to="/products" class="nav-item" active-class="active" title="Products">
        <div class="icon-container">
          <Package class="icon" />
        </div>
      </router-link>
      
      <router-link to="/reports" class="nav-item" active-class="active" title="Reports">
        <div class="icon-container">
          <BarChart3 class="icon" />
        </div>
      </router-link>

      <router-link v-if="authStore.user?.role === 'admin'" to="/admin" class="nav-item" active-class="active" title="Admin Panel">
        <div class="icon-container">
          <Settings class="icon" />
        </div>
      </router-link>
    </nav>
    
    <div class="bottom-actions">
      <button class="nav-item logout-btn" @click="$emit('logout')" title="Logout">
        <div class="icon-container">
          <LogOut class="icon" />
        </div>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { LayoutDashboard, Monitor, Package, BarChart3, Settings, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()

defineEmits(['logout'])
</script>

<style scoped>
.sidebar {
  width: 85px;
  background-color: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 100;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.brand {
  margin-bottom: 40px;
}

.logo-box {
  width: 48px;
  height: 48px;
  background-color: var(--accent-lime);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-sidebar);
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-grow: 1;
  width: 100%;
  align-items: center;
}

.nav-item {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  text-decoration: none;
  border-radius: 50%;
  transition: all var(--transition-fast);
  background: transparent;
  border: none;
  cursor: pointer;
}

.nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background-color: var(--accent-lime);
  color: var(--bg-sidebar);
  border-radius: 14px;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  width: 22px;
  height: 22px;
  stroke-width: 2px;
}

.bottom-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logout-btn {
  color: #fca5a5;
}
.logout-btn:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}
</style>
