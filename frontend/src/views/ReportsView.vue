<template>
  <div class="reports-layout">
    <!-- Filters Header Bar -->
    <FilterBar 
      v-model:selectedDateRange="selectedDateRange"
      v-model:selectedCashier="selectedCashier"
      v-model:selectedCategory="selectedCategory"
      :cashiers="mockCashiers"
      :categories="productsStore.categories"
    />

    <!-- Executive KPI Row -->
    <div class="kpi-grid" v-if="!loading">
      <MetricCard 
        title="Gross Sales Revenue" 
        :value="'$' + totalSalesRevenue.toFixed(2)"
        :icon="DollarSign"
        iconBg="rgba(184, 241, 90, 0.15)"
        iconColor="var(--text-primary)"
      />
      <MetricCard 
        title="Total Checkouts" 
        :value="salesHistory.length"
        :icon="ShoppingCart"
        iconBg="rgba(99, 102, 241, 0.1)"
        iconColor="#4f46e5"
      />
      <MetricCard 
        title="Average Ticket Value" 
        :value="'$' + averageTransactionSize.toFixed(2)"
        :icon="Award"
        iconBg="rgba(16, 185, 129, 0.1)"
        iconColor="var(--accent-success)"
      />
      <MetricCard 
        title="Products In Catalog" 
        :value="productsCount"
        :icon="Package"
        iconBg="#f3f4f6"
        iconColor="var(--text-secondary)"
      />
    </div>

    <div class="reports-loading-state" v-else>
      <div class="spinner"></div>
      <p>Generating analytics datasets...</p>
    </div>

    <!-- Charts and Performance Section -->
    <div class="reports-dashboard-grid" v-if="!loading">
      
      <!-- Chart Row: Sales Trend (Interactive Visuals) -->
      <SectionCard title="Sales Trend Analysis" description="Visual overview of hourly transactions and sales growth index.">
        <div class="chart-placeholder-box">
          <!-- Elegant SVG representation for Trend -->
          <svg class="trend-chart-svg" viewBox="0 0 500 150">
            <defs>
              <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--accent-lime)" stop-opacity="0.4" />
                <stop offset="100%" stop-color="var(--accent-lime)" stop-opacity="0.0" />
              </linearGradient>
            </defs>
            <path 
              d="M 0 120 Q 80 90 150 110 T 300 40 T 450 60 L 500 20 L 500 150 L 0 150 Z" 
              fill="url(#chartGrad)" 
            />
            <path 
              d="M 0 120 Q 80 90 150 110 T 300 40 T 450 60 L 500 20" 
              fill="none" 
              stroke="var(--accent-lime-hover)" 
              stroke-width="3" 
            />
            <circle cx="150" cy="110" r="4" fill="var(--text-primary)" />
            <circle cx="300" cy="40" r="4" fill="var(--text-primary)" />
            <circle cx="500" cy="20" r="5" fill="var(--text-primary)" />
          </svg>
          <div class="chart-time-labels">
            <span>08:00 AM</span>
            <span>11:00 AM</span>
            <span>02:00 PM</span>
            <span>05:00 PM</span>
            <span>08:00 PM</span>
          </div>
        </div>
      </SectionCard>

      <!-- Revenue by Category -->
      <SectionCard title="Revenue Distribution by Category" description="Visual categorization of itemized gross revenue.">
        <div class="chart-list">
          <div v-for="item in salesByCategory" :key="item.category" class="chart-row">
            <div class="chart-row-header">
              <span class="cat-name">{{ item.category }}</span>
              <span class="cat-value">${{ item.revenue.toFixed(2) }} ({{ item.items_sold }} units)</span>
            </div>
            
            <div class="bar-container">
              <div 
                class="bar-fill" 
                :style="{ width: getPercentage(item.revenue) + '%' }"
              ></div>
            </div>
          </div>
          <div class="empty-state" v-if="salesByCategory.length === 0">
            <p>No categoric checkout logs recorded yet.</p>
          </div>
        </div>
      </SectionCard>

      <!-- Cashier Performance -->
      <SectionCard title="Cashier Operations Ledger" description="Aggregated transactions processing speed and value metrics.">
        <div class="cashier-performance-list">
          <div class="perf-row" v-for="c in mockCashiers" :key="c.id">
            <div class="perf-avatar">
              {{ c.username.charAt(0).toUpperCase() }}
            </div>
            <div class="perf-meta">
              <span class="perf-name">{{ c.username }}</span>
              <span class="perf-sub">Terminal Operator</span>
            </div>
            <div class="perf-values">
              <span class="perf-total-sales">${{ (totalSalesRevenue * (c.id === 'c1' ? 0.6 : 0.4)).toFixed(2) }}</span>
              <span class="perf-count">{{ c.id === 'c1' ? '12 orders' : '8 orders' }}</span>
            </div>
          </div>
        </div>
      </SectionCard>

      <!-- Detailed Transaction Register -->
      <SectionCard title="Sales Register Invoices" description="Chronological record of completed transactions." class="span-all-columns">
        <div class="table-container">
          <div class="premium-table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Cashier</th>
                  <th>Date & Time</th>
                  <th>Payment Method</th>
                  <th class="text-right">Subtotal</th>
                  <th class="text-right">Discount</th>
                  <th class="text-right">Tax</th>
                  <th class="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sale in salesHistory" :key="sale.id">
                  <td><code>{{ sale.invoice_number }}</code></td>
                  <td><span class="cashier-tag">{{ sale.cashier_name }}</span></td>
                  <td>{{ formatDate(sale.created_at) }}</td>
                  <td>
                    <span class="payment-method-chip" :class="sale.payment_method">
                      {{ sale.payment_method.toUpperCase() }}
                    </span>
                  </td>
                  <td class="text-right">${{ sale.subtotal.toFixed(2) }}</td>
                  <td class="text-right text-danger">${{ sale.discount.toFixed(2) }}</td>
                  <td class="text-right">${{ sale.tax.toFixed(2) }}</td>
                  <td class="text-right font-bold text-total">${{ sale.total.toFixed(2) }}</td>
                </tr>
                <tr v-if="salesHistory.length === 0">
                  <td colspan="8" class="empty-row">No orders recorded in register history.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </SectionCard>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FilterBar from '@/components/FilterBar.vue'
import MetricCard from '@/components/MetricCard.vue'
import SectionCard from '@/components/SectionCard.vue'
import { useProductsStore } from '@/store/products'
import { DollarSign, ShoppingCart, Award, Package } from 'lucide-vue-next'

const productsStore = useProductsStore()

const salesByCategory = ref([])
const salesHistory = ref([])
const productsCount = ref(0)
const loading = ref(true)

// Filter binds
const selectedDateRange = ref('today')
const selectedCashier = ref('')
const selectedCategory = ref('')

const mockCashiers = ref([
  { id: 'c1', username: 'cashier1' },
  { id: 'admin', username: 'admin' }
])

const loadReports = async () => {
  loading.value = true
  try {
    const [catRes, historyRes, prodList] = await Promise.all([
      axios.get('/api/reports/sales-by-category'),
      axios.get('/api/sales/history'),
      productsStore.fetchProducts()
    ])
    
    salesByCategory.value = catRes.data
    salesHistory.value = historyRes.data
    productsCount.value = prodList.length
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
  productsStore.fetchCategories()
  loadReports()
})
</script>

<style scoped>
.reports-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.reports-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 24px;
}

.span-all-columns {
  grid-column: 1 / -1;
}

/* Sales Trend SVG Box */
.chart-placeholder-box {
  background-color: #f9fafb;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trend-chart-svg {
  width: 100%;
  height: 140px;
}

.chart-time-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
}

/* Category breakdowns */
.chart-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chart-row-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.cat-name {
  font-weight: 700;
  color: var(--text-primary);
}

.cat-value {
  font-weight: 600;
  color: var(--text-secondary);
}

.bar-container {
  height: 10px;
  background-color: #f3f4f6;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: var(--accent-lime-hover);
  border-radius: 5px;
  transition: width 1s ease-out;
}

/* Cashier Performance style */
.cashier-performance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.perf-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #f9fafb;
  border: 1px solid var(--border-color);
  padding: 10px 14px;
  border-radius: var(--radius-md);
}

.perf-avatar {
  width: 36px;
  height: 36px;
  background-color: rgba(184, 241, 90, 0.15);
  color: #557c11;
  font-weight: 700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}

.perf-meta {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.perf-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary);
}

.perf-sub {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.perf-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.perf-total-sales {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text-primary);
}

.perf-count {
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Invoice table registry */
.table-container {
  overflow-x: auto;
}

.premium-table-wrapper {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
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
  font-size: 0.88rem;
}

.report-table th {
  background-color: #f9fafb;
  color: var(--text-secondary);
  font-weight: 700;
}

.report-table tr:last-child td {
  border-bottom: none;
}

.report-table tr:hover {
  background-color: #fdfdfd;
}

.cashier-tag {
  background-color: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.payment-method-chip {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

.payment-method-chip.cash { background-color: rgba(16, 185, 129, 0.1); color: var(--accent-success); }
.payment-method-chip.card { background-color: rgba(99, 102, 241, 0.1); color: #4f46e5; }
.payment-method-chip.mobile_pay { background-color: rgba(245, 158, 11, 0.1); color: var(--accent-warning); }

.text-right { text-align: right; }
.text-danger { color: var(--accent-danger); }
.font-bold { font-weight: 700; }
.text-total { color: var(--text-primary); }

.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 40px !important;
}

.reports-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
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
</style>
