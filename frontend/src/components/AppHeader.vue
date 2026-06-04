<template>
  <header class="top-header">
    <div class="header-left">
      <h1 class="header-title">{{ title }}</h1>
      <p class="header-subtitle" v-if="subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="header-right">
      <!-- Sync Trigger & Connection Status Badge -->
      <div class="status-indicator-wrapper">
        <div class="status-badge" :class="isOnline ? 'online' : 'offline'">
          <Wifi v-if="isOnline" class="status-icon" />
          <WifiOff v-else class="status-icon" />
          <span>{{ isOnline ? 'Online' : 'Offline' }}</span>
        </div>
        <div v-if="pendingSyncCount > 0" class="sync-banner">
          <span class="sync-count">{{ pendingSyncCount }} Unsynced</span>
          <button @click="$emit('sync')" class="sync-btn" :disabled="isSyncing" title="Sync Offline Transactions">
            <RefreshCw class="sync-icon" :class="{ 'rotating': isSyncing }" />
          </button>
        </div>
      </div>

      <div class="divider"></div>

      <!-- Cashier User Section -->
      <div class="user-profile">
        <div class="avatar-circle">
          <User class="avatar-icon" />
        </div>
        <div class="user-meta">
          <span class="cashier-name">{{ cashierName }}</span>
          <span class="cashier-role">{{ cashierRole }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Wifi, WifiOff, RefreshCw, User } from 'lucide-vue-next'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  cashierName: {
    type: String,
    default: 'Cashier'
  },
  cashierRole: {
    type: String,
    default: 'Operator'
  },
  isOnline: {
    type: Boolean,
    default: true
  },
  pendingSyncCount: {
    type: Number,
    default: 0
  },
  isSyncing: {
    type: Boolean,
    default: false
  }
})

defineEmits(['sync'])
</script>

<style scoped>
.top-header {
  height: 80px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 90;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-indicator-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.status-badge.online {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.status-badge.offline {
  background-color: rgba(255, 94, 94, 0.1);
  color: var(--accent-danger);
}

.status-icon {
  width: 16px;
  height: 16px;
}

.sync-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--accent-warning);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.sync-count {
  white-space: nowrap;
}

.sync-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
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

.divider {
  width: 1px;
  height: 32px;
  background-color: var(--border-color);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background-color: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.avatar-icon {
  width: 20px;
  height: 20px;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.cashier-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.cashier-role {
  font-size: 0.75rem;
  color: var(--text-muted);
}
</style>
