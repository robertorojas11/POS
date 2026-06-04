<template>
  <div class="reports-container">
    <!-- Reports overview stats -->
    <div class="report-overview">
      <div class="pos-card stats-summary">
        <h3>Sales Performance Overview</h3>
        <p class="desc">A summary of the store's transactional statistics and inventory valuation.</p>
        
        <div class="grid-3">
          <div class="report-stat">
            <span class="label">Gross Sales Revenue</span>
            <span class="value text-green">${{ totalSalesRevenue.toFixed(2) }}</span>
          </div>
          <div class="report-stat">
            <span class="label">Average Transaction Value</span>
            <span class="value">${{ averageTransactionSize.toFixed(2) }}</span>
          </div>
          <div class="report-stat">
            <span class="label">Total Products Cataloged</span>
            <span class="value">{{ productsCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Layout: Chart & Category Distribution -->
    <div class="report-details">
      <!-- Sales by Category (CSS Visual bars) -->
      <div class="pos-card category-breakdown">
        <h3>Sales Revenue by Category</h3>
        <p class="desc">Proportion of gross revenue distributed across catalog categories.</p>
        
        <div class="chart-list" v-if="!loading">
          <div v-for="item in salesByCategory" :key="item.category" class="chart-row">
            <div class="chart-row-header">
              <span class="cat-name">{{ item.category }}</span>
              <span class="cat-value">${{ item.revenue.toFixed(2) }} ({{ item.items_sold }} items sold)</span>
            </div>
            
            <div class="bar-container">
              <div 
                class="bar-fill" 
                :style="{ width: getPercentage(item.revenue) + '%' }"
              ></div>
            </div>
          </div>
          <div class="empty-state" v-if="salesByCategory.length === 0">
            <p>No sales data recorded to generate reports.</p>
          </div>
        </div>
        <div class="loading-state" v-else>
          <div class="spinner"></div>
        </div>
      </div>

      <!-- Transaction Log -->
      <div class="pos-card transaction-log">
        <h3>Detailed Transaction Register</h3>
        <p class="desc">Historical logs of all finalized checkout orders.</p>
        
        <div class="table-container" v-if="!loading">
          <table class="report-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Cashier</th>
                <th>Date & Time</th>
                <th>Payment</th>
                <th class="text-right">Subtotal</th>
                <th class="text-right">Discount</th>
                <th class="text-right">Tax</th>
                <th class="text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sale in salesHistory" :key="sale.id">
                <td><code>{{ sale.invoice_number }}</code></td>
                <td>{{ sale.cashier_name }}</td>
                <td>{{ formatDate(sale.created_at) }}</td>
                <td>
                  <span class="payment-badge" :class="sale.payment_method">
                    {{ sale.payment_method }}
                  </span>
                </td>
                <td class="text-right">${{ sale.subtotal.toFixed(2) }}</td>
                <td class="text-right text-rose">${{ sale.discount.toFixed(2) }}</td>
                <td class="text-right">${{ sale.tax.toFixed(2) }}</td>
                <td class="text-right text-green font-bold">${{ sale.total.toFixed(2) }}</td>
              </tr>
              <tr v-if="salesHistory.length === 0">
                <td colspan="8" class="empty-row">No orders recorded in register history.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="loading-state" v-else>
          <div class="spinner"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const salesByCategory = ref([])
const salesHistory = ref([])
const productsCount = ref(0)
const loading = ref(true)

const loadReports = async () => {
  loading.value = true
  try {
    const [catRes, historyRes, prodRes] = await Promise.all([
      axios.get('/api/reports/sales-by-category'),
      axios.get('/api/sales/history'),
      axios.get('/api/products')
    ])
    
    salesByCategory.value = catRes.data
    salesHistory.value = historyRes.data
    productsCount.value = prodRes.data.length
  } catch (err) {
    console.error('Failed to load reports', err)
  } finally {
    loading.value = false
  }
}

const totalSalesRevenue = computed(() => {
  return salesHistory.value.reduce((sum, sale) => sum + sale.total, 0)
})

const averageTransactionSize = computed(() => {
  if (salesHistory.value.length === 0) return 0
  return totalSalesRevenue.value / salesHistory.value.length
})

const maxCategoryRevenue = computed(() => {
  if (salesByCategory.value.length === 0) return 1
  return Math.max(...salesByCategory.value.map(item => item.revenue))
})

const getPercentage = (val) => {
  if (maxCategoryRevenue.value === 0) return 0
  return (val / maxCategoryRevenue.value) * 100
}

const formatDate = (isoString) => {
  const d = new Date(isoString)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.reports-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.stats-summary {
  background-color: var(--bg-secondary);
}

.desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 4px;
  margin-bottom: 24px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

@media (max-width: 768px) {
  .grid-3 {
    grid-template-columns: 1fr;
  }
}

.report-stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.report-stat .label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.report-stat .value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #fff;
}

.text-green { color: var(--accent-success) !important; }
.text-rose { color: var(--accent-danger) !important; }

.report-details {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.chart-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-row-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.cat-name { font-weight: 600; color: #fff; }
.cat-value { color: var(--text-secondary); }

.bar-container {
  height: 12px;
  background-color: var(--bg-tertiary);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-success));
  border-radius: 6px;
  transition: width 1s ease-out;
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
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.report-table th {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 600;
}

.report-table tr:hover {
  background-color: rgba(255, 255, 255, 0.01);
}

.text-right { text-align: right; }
.font-bold { font-weight: 600; }

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

.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 40px !important;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 150px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
