<template>
  <div class="dashboard-layout">
    <!-- Top KPI Grid -->
    <div class="kpi-grid" v-if="!loading">
      <MetricCard 
        title="Active Cashiers" 
        :value="activeCashiersCount"
        :icon="Users"
        iconBg="rgba(184, 241, 90, 0.15)"
        iconColor="var(--text-primary)"
      />
      <MetricCard 
        title="Open Registers" 
        :value="openRegistersCount"
        :icon="Monitor"
        iconBg="rgba(99, 102, 241, 0.1)"
        iconColor="#4f46e5"
      />
      <MetricCard 
        title="Total Drawer Cash" 
        :value="'$' + totalDrawerCash.toFixed(2)"
        :icon="DollarSign"
        iconBg="rgba(16, 185, 129, 0.1)"
        iconColor="var(--accent-success)"
      />
      <MetricCard 
        title="Pending Cash Drops" 
        :value="pendingDropsCount"
        :icon="AlertTriangle"
        iconBg="rgba(255, 94, 94, 0.1)"
        iconColor="var(--accent-danger)"
        :trend="pendingDropsCount > 0 ? 'Action required' : 'Status healthy'"
        :trendType="pendingDropsCount > 0 ? 'negative' : 'positive'"
      />
    </div>

    <!-- Secondary KPI Row (Overview Stats) -->
    <div class="kpi-grid secondary-kpis" v-if="!loading">
      <div class="mini-kpi premium-card">
        <span class="mini-title">Today's Revenue</span>
        <h4 class="mini-value">${{ stats.today_revenue.toFixed(2) }}</h4>
      </div>
      <div class="mini-kpi premium-card">
        <span class="mini-title">Total Checkouts</span>
        <h4 class="mini-value">{{ stats.today_transactions }}</h4>
      </div>
      <div class="mini-kpi premium-card">
        <span class="mini-title">Average Ticket</span>
        <h4 class="mini-value">${{ stats.average_ticket.toFixed(2) }}</h4>
      </div>
      <div class="mini-kpi premium-card" :class="{ 'warning-border': stats.low_stock_alerts > 0 }">
        <span class="mini-title">Low Stock Items</span>
        <h4 class="mini-value" :class="{ 'text-danger': stats.low_stock_alerts > 0 }">{{ stats.low_stock_alerts }}</h4>
      </div>
    </div>

    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>Syncing dashboard statistics...</p>
    </div>

    <!-- Main Command Content -->
    <div class="dashboard-main-grid" v-if="!loading">
      
      <!-- Shift & Drawer Management Column -->
      <div class="main-column-left">
        
        <!-- Shift Monitoring Section -->
        <SectionCard title="Active Cashier Terminals" description="Overview of currently logged-in POS cashiers and open shift status.">
          <div class="shift-grid-list" v-if="activeShifts.length">
            <div 
              v-for="shift in activeShifts" 
              :key="shift.id"
              class="cashier-status-card"
              :class="{ 'card-warning': shift.expected_cash > 1000 }"
            >
              <div class="cashier-card-header">
                <div>
                  <h4 class="cashier-card-name">{{ shift.cashier_name }}</h4>
                  <span class="register-label">Register #{{ shift.terminal_id }} • {{ shift.store_location }}</span>
                </div>
                <StatusBadge :status="shift.expected_cash > 1000 ? 'break' : 'active'" />
              </div>
              
              <div class="cashier-card-body">
                <div class="body-metric">
                  <span class="metric-label">Shift Start</span>
                  <span class="metric-val">{{ formatTime(shift.start_time) }}</span>
                </div>
                <div class="body-metric">
                  <span class="metric-label">Drawer Balance</span>
                  <span class="metric-val text-bold" :class="{ 'text-danger': shift.expected_cash > 1000 }">
                    ${{ shift.expected_cash.toFixed(2) }}
                  </span>
                </div>
              </div>

              <div class="cashier-card-footer" v-if="shift.expected_cash > 1000">
                <div class="drop-banner">
                  <AlertTriangle class="drop-banner-icon" />
                  <span>Drawer threshold exceeded. Collect cash drop.</span>
                </div>
              </div>
            </div>
          </div>
          <div class="empty-status-state" v-else>
            <Users class="empty-state-icon" />
            <p>No active cashier terminals currently running.</p>
          </div>
        </SectionCard>

        <!-- Cash Drawer Monitoring -->
        <SectionCard title="Cash Drawer Analysis" description="Compare current register holdings and detect system variances.">
          <div class="drawer-monitoring-list" v-if="activeShifts.length">
            <div v-for="shift in activeShifts" :key="'drawer-' + shift.id" class="drawer-monitor-item">
              <div class="drawer-meta-title">
                <span class="register-tag">Register #{{ shift.terminal_id }}</span>
                <span class="cashier-meta-name">({{ shift.cashier_name }})</span>
              </div>
              <div class="drawer-grid-metrics">
                <div class="drawer-pill green">
                  <span class="pill-title">Opening Balance</span>
                  <span class="pill-value">${{ shift.start_cash.toFixed(2) }}</span>
                </div>
                <div class="drawer-pill border">
                  <span class="pill-title">Expected Holdings</span>
                  <span class="pill-value">${{ shift.expected_cash.toFixed(2) }}</span>
                </div>
                <div class="drawer-pill" :class="shift.expected_cash > 1000 ? 'red' : 'green'">
                  <span class="pill-title">Status</span>
                  <span class="pill-value">{{ shift.expected_cash > 1000 ? 'Drop Triggered' : 'Healthy' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="empty-status-state" v-else>
            <DollarSign class="empty-state-icon" />
            <p>No registers active for cash analysis.</p>
          </div>
        </SectionCard>

        <!-- Workers directory panel -->
        <SectionCard 
          v-if="isAdminOrManager" 
          :title="authStore.user?.role === 'admin' ? 'Store Workers Directory' : 'Shift Employees Directory'" 
          :description="authStore.user?.role === 'admin' ? 'View status of all managers and register operators.' : 'Monitor cashier operators assigned to your shift.'"
        >
          <div class="workers-grid-list">
            <div 
              v-for="worker in workers" 
              :key="worker.id" 
              class="worker-badge-card"
            >
              <div class="worker-card-left">
                <div class="worker-avatar-badge">
                  {{ worker.username.charAt(0).toUpperCase() }}
                </div>
                <div class="worker-details-meta">
                  <span class="worker-name">{{ worker.username }}</span>
                  <span class="worker-email">{{ worker.email }}</span>
                </div>
              </div>
              <div class="worker-card-right">
                <span class="role-badge" :class="worker.role.toLowerCase()">
                  {{ worker.role.toUpperCase() }}
                </span>
                <span class="status-indicator-dot" :class="isWorkerActive(worker) ? 'active' : 'offline'">
                  <span class="status-dot"></span>
                  {{ isWorkerActive(worker) ? 'Active' : 'Offline' }}
                </span>
              </div>
            </div>
          </div>
        </SectionCard>

      </div>

      <!-- Right Column: Real-Time Alerts & Feed -->
      <div class="main-column-right">
        
        <!-- Alerts Feed -->
        <SectionCard title="Real-Time Alerts Feed" description="Critical notifications and system activity triggers.">
          <div class="alerts-feed-list">
            
            <!-- Cash Drop Alert -->
            <div v-for="shift in cashDropAlerts" :key="'alert-drop-' + shift.id" class="feed-alert-item alert-danger">
              <div class="alert-header">
                <div class="alert-icon-box">
                  <AlertTriangle class="alert-feed-icon" />
                </div>
                <div class="alert-text">
                  <h5>Cash Drop Required</h5>
                  <p>Register #{{ shift.terminal_id }} ({{ shift.cashier_name }}) has reached ${{ shift.expected_cash.toFixed(2) }}. Safe drop is required immediately.</p>
                </div>
              </div>
            </div>

            <!-- Low Stock Alerts -->
            <div v-if="stats.low_stock_alerts > 0" class="feed-alert-item alert-warning">
              <div class="alert-header">
                <div class="alert-icon-box">
                  <Package class="alert-feed-icon" />
                </div>
                <div class="alert-text">
                  <h5>Low Stock Thresholds Triggered</h5>
                  <p>{{ stats.low_stock_alerts }} catalog items have dropped below their minimum stock warnings. Restock suggested.</p>
                </div>
              </div>
            </div>

            <!-- Healthy Status Alert -->
            <div v-if="cashDropAlerts.length === 0 && stats.low_stock_alerts === 0" class="feed-alert-item alert-success">
              <div class="alert-header">
                <div class="alert-icon-box">
                  <Activity class="alert-feed-icon" />
                </div>
                <div class="alert-text">
                  <h5>System Status Nominal</h5>
                  <p>No register variances or stock alarms detected. All active terminals operating within standard parameters.</p>
                </div>
              </div>
            </div>

          </div>
        </SectionCard>

        <!-- Quick Access Navigation -->
        <SectionCard title="Command Shortcuts" description="Jump quickly to other management views.">
          <div class="shortcut-buttons-grid">
            <router-link to="/pos" class="pos-btn pos-btn-accent shortcut-btn">
              Open POS Register
            </router-link>
            <router-link to="/products" class="pos-btn pos-btn-secondary shortcut-btn">
              Inventory Catalog
            </router-link>
            <router-link to="/reports" class="pos-btn pos-btn-secondary shortcut-btn">
              Executive Reports
            </router-link>
          </div>
        </SectionCard>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import MetricCard from '@/components/MetricCard.vue'
import SectionCard from '@/components/SectionCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { Users, Monitor, DollarSign, AlertTriangle, Package, Activity } from 'lucide-vue-next'

const authStore = useAuthStore()

const stats = ref({
  today_revenue: 0.00,
  today_transactions: 0,
  average_ticket: 0.00,
  low_stock_alerts: 0
})
const recentSales = ref([])
const lowStockList = ref([])
const activeShifts = ref([])
const workers = ref([])
const loading = ref(true)

const isAdminOrManager = computed(() => ['admin', 'manager'].includes(authStore.user?.role))

// Computed metrics from active shifts
const activeCashiersCount = computed(() => activeShifts.value.length)
const openRegistersCount = computed(() => {
  const terminals = activeShifts.value.map(s => s.terminal_id)
  return new Set(terminals).size
})
const totalDrawerCash = computed(() => {
  return activeShifts.value.reduce((sum, s) => sum + s.expected_cash, 0)
})
const pendingDropsCount = computed(() => {
  return activeShifts.value.filter(s => s.expected_cash > 1000).length
})

const cashDropAlerts = computed(() => {
  return activeShifts.value.filter(s => s.expected_cash > 1000)
})

const isWorkerActive = (worker) => {
  return activeShifts.value.some(s => s.cashier_id === worker.id)
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    const requests = [
      axios.get('/api/reports/dashboard'),
      axios.get('/api/sales/history?limit=8'),
      axios.get('/api/reports/low-stock')
    ]
    if (isAdminOrManager.value) {
      requests.push(axios.get('/api/sales/shifts/active-all'))
      requests.push(axios.get('/api/auth/users'))
    }
    
    const results = await Promise.all(requests)
    stats.value = results[0].data
    recentSales.value = results[1].data
    lowStockList.value = results[2].data
    
    if (isAdminOrManager.value && results[3]) {
      activeShifts.value = results[3].data
    }
    if (isAdminOrManager.value && results[4]) {
      workers.value = results[4].data
    }
  } catch (err) {
    console.error('Failed to load dashboard data', err)
  } finally {
    loading.value = false
  }
}

const formatTime = (isoString) => {
  const dateObj = new Date(isoString)
  return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.secondary-kpis {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.mini-kpi {
  background-color: var(--bg-card);
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-kpi.warning-border {
  border-color: rgba(255, 94, 94, 0.3);
}

.mini-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mini-value {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
}

.dashboard-main-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .dashboard-main-grid {
    grid-template-columns: 1fr;
  }
}

.main-column-left, .main-column-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Cashier Status Card design */
.shift-grid-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.cashier-status-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  background-color: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.cashier-status-card.card-warning {
  border-color: rgba(255, 94, 94, 0.3);
  background-color: rgba(255, 94, 94, 0.01);
}

.cashier-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.cashier-card-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.register-label {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.cashier-card-body {
  display: flex;
  gap: 24px;
}

.body-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.3px;
}

.metric-val {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.metric-val.text-bold {
  font-size: 0.95rem;
  font-weight: 700;
}

.cashier-card-footer {
  border-top: 1px dashed var(--border-color);
  padding-top: 12px;
}

.drop-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent-danger);
  font-size: 0.8rem;
  font-weight: 700;
}

.drop-banner-icon {
  width: 16px;
  height: 16px;
  animation: pulse-icon 1.5s infinite;
}

@keyframes pulse-icon {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.empty-status-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--text-muted);
  gap: 8px;
}

.empty-state-icon {
  width: 32px;
  height: 32px;
  stroke-width: 1.5px;
}

/* Cash drawer monitoring pills */
.drawer-monitoring-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.drawer-monitor-item {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drawer-meta-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-tag {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
}

.cashier-meta-name {
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.drawer-grid-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.drawer-pill {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drawer-pill.border {
  border: 1px solid var(--border-color);
  background-color: #ffffff;
}

.drawer-pill.green {
  background-color: rgba(184, 241, 90, 0.15);
  color: #557c11;
  font-weight: 600;
}

.drawer-pill.red {
  background-color: rgba(255, 94, 94, 0.1);
  color: #c22525;
  font-weight: 600;
}

.pill-title {
  font-size: 0.65rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.pill-value {
  font-size: 0.85rem;
  font-weight: 700;
}

/* Alerts feed */
.alerts-feed-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feed-alert-item {
  border-radius: var(--radius-md);
  padding: 14px 16px;
  border: 1px solid transparent;
}

.feed-alert-item.alert-danger {
  background-color: rgba(255, 94, 94, 0.05);
  border-color: rgba(255, 94, 94, 0.2);
  color: #b91c1c;
}

.feed-alert-item.alert-warning {
  background-color: rgba(245, 158, 11, 0.05);
  border-color: rgba(245, 158, 11, 0.2);
  color: #b45309;
}

.feed-alert-item.alert-success {
  background-color: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
  color: #047857;
}

.alert-header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.alert-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 2px;
}

.alert-feed-icon {
  width: 18px;
  height: 18px;
}

.alert-text h5 {
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 2px;
}

.alert-text p {
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--text-secondary);
}

.shortcut-buttons-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.shortcut-btn {
  width: 100%;
  padding: 10px 16px;
  text-decoration: none;
  font-size: 0.85rem;
}

/* Loading animations */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
  gap: 16px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-lime-hover);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.workers-grid-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.worker-badge-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f9fafb;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.worker-card-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.worker-avatar-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e5e7eb;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
}

.worker-details-meta {
  display: flex;
  flex-direction: column;
}

.worker-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary);
}

.worker-email {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.worker-card-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.role-badge.admin {
  background-color: rgba(184, 241, 90, 0.2);
  color: #557c11;
}

.role-badge.manager {
  background-color: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
}

.role-badge.operator {
  background-color: rgba(229, 231, 235, 1);
  color: #374151;
}

.status-indicator-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-indicator-dot.active {
  color: var(--accent-success);
}

.status-indicator-dot.offline {
  color: var(--text-muted);
}

.status-indicator-dot .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}
</style>
