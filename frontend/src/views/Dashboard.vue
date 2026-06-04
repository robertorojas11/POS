<template>
  <div class="dashboard-container">
    <!-- Stat Grid -->
    <div class="stat-grid" v-if="!loading">
      <div class="stat-card pos-card border-indigo">
        <div class="stat-icon bg-indigo">💰</div>
        <div class="stat-details">
          <span class="stat-label">Today's Revenue</span>
          <h3 class="stat-value">${{ stats.today_revenue.toFixed(2) }}</h3>
        </div>
      </div>
      
      <div class="stat-card pos-card border-green">
        <div class="stat-icon bg-green">🛒</div>
        <div class="stat-details">
          <span class="stat-label">Transactions</span>
          <h3 class="stat-value">{{ stats.today_transactions }}</h3>
        </div>
      </div>

      <div class="stat-card pos-card border-yellow">
        <div class="stat-icon bg-yellow">🎟️</div>
        <div class="stat-details">
          <span class="stat-label">Average Ticket</span>
          <h3 class="stat-value">${{ stats.average_ticket.toFixed(2) }}</h3>
        </div>
      </div>

      <div class="stat-card pos-card border-rose" :class="{ 'alert-glow': stats.low_stock_alerts > 0 }">
        <div class="stat-icon bg-rose">⚠️</div>
        <div class="stat-details">
          <span class="stat-label">Low Stock Alerts</span>
          <h3 class="stat-value">{{ stats.low_stock_alerts }}</h3>
        </div>
      </div>
    </div>

    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>Loading overview analytics...</p>
    </div>

    <!-- Main Grid -->
    <div class="main-sections" v-if="!loading">
      <!-- Quick Actions -->
      <div class="section-left">
        <!-- Live Cashier Shifts Panel -->
        <div v-if="isAdminOrManager" class="pos-card active-shifts-panel border-indigo" style="margin-bottom: 30px;">
          <div class="panel-header">
            <h3>⚡ Live Cashier Drawers</h3>
            <span class="badge badge-success" v-if="activeShifts.length">{{ activeShifts.length }} Active</span>
            <span class="badge badge-secondary" v-else>No Active Shifts</span>
          </div>
          
          <div class="table-container">
            <table class="report-table" v-if="activeShifts.length">
              <thead>
                <tr>
                  <th>Cashier</th>
                  <th>Terminal</th>
                  <th>Store Location</th>
                  <th class="text-right">Drawer Cash</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="shift in activeShifts" :key="shift.id" :class="{ 'warning-row': shift.expected_cash > 1000 }">
                  <td>
                    <div class="cashier-cell">
                      <span class="cashier-name font-bold">{{ shift.cashier_name }}</span>
                      <span class="shift-time text-muted">Started {{ formatTime(shift.start_time) }}</span>
                    </div>
                  </td>
                  <td><code>{{ shift.terminal_id }}</code></td>
                  <td>{{ shift.store_location }}</td>
                  <td class="text-right font-bold" :class="{ 'text-danger animate-pulse': shift.expected_cash > 1000 }">
                    ${{ shift.expected_cash.toFixed(2) }}
                  </td>
                  <td>
                    <span v-if="shift.expected_cash > 1000" class="alert-badge exceed">
                      ⚠️ Drop Required
                    </span>
                    <span v-else class="alert-badge normal">
                      ✓ Healthy
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="empty-state" v-else>
              <p>All cashier terminals are currently closed.</p>
            </div>
          </div>
        </div>

        <div class="pos-card quick-actions">
          <h3>Quick Terminal Actions</h3>
          <div class="btn-group">
            <router-link to="/pos" class="pos-btn pos-btn-primary action-btn">
              ⚡ Open Register
            </router-link>
            <router-link to="/products" class="pos-btn pos-btn-secondary action-btn">
              📦 Catalog Manager
            </router-link>
            <router-link to="/reports" class="pos-btn pos-btn-secondary action-btn">
              📊 Analytics Board
            </router-link>
          </div>
        </div>

        <!-- Low Stock Table -->
        <div class="pos-card low-stock-panel">
          <div class="panel-header">
            <h3>Low Stock Alerts</h3>
            <span class="badge" v-if="lowStockList.length">{{ lowStockList.length }} items</span>
          </div>
          
          <div class="table-container">
            <table class="report-table" v-if="lowStockList.length">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th class="text-right">In Stock</th>
                  <th class="text-right">Min Level</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in lowStockList" :key="item.id">
                  <td>{{ item.name }}</td>
                  <td><code>{{ item.sku }}</code></td>
                  <td class="text-right text-rose font-bold">{{ item.stock_quantity }}</td>
                  <td class="text-right">{{ item.min_stock_level }}</td>
                </tr>
              </tbody>
            </table>
            <div class="empty-state" v-else>
              <span class="check-icon">✓</span>
              <p>All product inventory levels are healthy.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Transactions -->
      <div class="section-right">
        <div class="pos-card recent-sales">
          <h3>Recent Sales Transactions</h3>
          <div class="sales-list" v-if="recentSales.length">
            <div class="sale-row" v-for="sale in recentSales" :key="sale.id">
              <div class="sale-left">
                <span class="invoice-num">{{ sale.invoice_number }}</span>
                <span class="sale-time">{{ formatTime(sale.created_at) }} • {{ sale.cashier_name }}</span>
              </div>
              <div class="sale-right">
                <span class="sale-total">${{ sale.total.toFixed(2) }}</span>
                <span class="payment-badge" :class="sale.payment_method">{{ sale.payment_method }}</span>
              </div>
            </div>
          </div>
          <div class="empty-state" v-else>
            <p>No transactions completed yet today.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

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
const loading = ref(true)

const isAdminOrManager = computed(() => ['admin', 'manager'].includes(authStore.user?.role))

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
    }
    
    const results = await Promise.all(requests)
    stats.value = results[0].data
    recentSales.value = results[1].data
    lowStockList.value = results[2].data
    
    if (isAdminOrManager.value && results[3]) {
      activeShifts.value = results[3].data
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
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.border-indigo { border-left: 4px solid var(--accent-primary); }
.border-green { border-left: 4px solid var(--accent-success); }
.border-yellow { border-left: 4px solid var(--accent-warning); }
.border-rose { border-left: 4px solid var(--accent-danger); }

.alert-glow {
  animation: pulse-border 2s infinite alternate;
}

@keyframes pulse-border {
  from { box-shadow: var(--shadow-md); }
  to { box-shadow: 0 0 16px rgba(239, 68, 68, 0.25); }
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.bg-indigo { background-color: rgba(79, 70, 229, 0.15); }
.bg-green { background-color: rgba(16, 185, 129, 0.15); }
.bg-yellow { background-color: rgba(245, 158, 11, 0.15); }
.bg-rose { background-color: rgba(239, 68, 68, 0.15); }

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  color: #fff;
  font-weight: 700;
}

.main-sections {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 30px;
}

@media (max-width: 1024px) {
  .main-sections {
    grid-template-columns: 1fr;
  }
}

.section-left {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.quick-actions h3,
.low-stock-panel h3,
.recent-sales h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #fff;
}

.btn-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  flex-grow: 1;
  text-decoration: none;
  font-size: 0.95rem;
  padding: 12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.badge {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--accent-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.table-container {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table th,
.report-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.report-table th {
  color: var(--text-secondary);
  font-weight: 600;
  background-color: var(--bg-tertiary);
}

.report-table tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.text-right { text-align: right; }
.text-rose { color: var(--accent-danger); }
.font-bold { font-weight: 600; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.check-icon {
  font-size: 2rem;
  color: var(--accent-success);
  margin-bottom: 12px;
}

.sales-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sale-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  transition: transform var(--transition-fast);
}

.sale-row:hover {
  transform: translateX(4px);
}

.sale-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.invoice-num {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
}

.sale-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.sale-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.sale-total {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent-success);
}

.payment-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 600;
}
.payment-badge.cash { background-color: rgba(16, 185, 129, 0.15); color: #34d399; }
.payment-badge.card { background-color: rgba(79, 70, 229, 0.15); color: #818cf8; }
.payment-badge.mobile_pay { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; }

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
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.badge-success {
  background-color: rgba(16, 185, 129, 0.15);
  color: var(--accent-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.badge-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.cashier-cell {
  display: flex;
  flex-direction: column;
}

.shift-time {
  font-size: 0.75rem;
}

.alert-badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.alert-badge.exceed {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--accent-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
  animation: pulse-border-exceed 1.5s infinite alternate;
}

.alert-badge.normal {
  background-color: rgba(16, 185, 129, 0.15);
  color: var(--accent-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.warning-row {
  background-color: rgba(239, 68, 68, 0.02) !important;
}

.warning-row:hover {
  background-color: rgba(239, 68, 68, 0.04) !important;
}

.animate-pulse {
  animation: text-pulse 2s infinite;
}

@keyframes text-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-border-exceed {
  from { box-shadow: 0 0 2px rgba(239, 68, 68, 0.2); }
  to { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
}
</style>
