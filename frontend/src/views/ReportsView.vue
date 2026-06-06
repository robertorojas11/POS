<template>
  <div class="reports-layout">
    <!-- Sub-menu Navigation -->
    <div class="admin-tabs premium-card">
      <button 
        class="tab-btn" 
        :class="{ active: activeSubTab === 'dashboard' }" 
        @click="activeSubTab = 'dashboard'"
      >
        <TrendingUp class="tab-icon" />
        Analytics Dashboard
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeSubTab === 'generator' }" 
        @click="activeSubTab = 'generator'"
      >
        <FileSpreadsheet class="tab-icon" />
        Custom Report Generator
      </button>
    </div>

    <!-- ANALYTICS DASHBOARD VIEW -->
    <div v-if="activeSubTab === 'dashboard'" class="tab-content-wrapper">
      <!-- Filters Header Bar -->
      <FilterBar 
        v-model:selectedDateRange="selectedDateRange"
        v-model:selectedCashier="selectedCashier"
        v-model:selectedCategory="selectedCategory"
        :cashiers="cashiersList"
        :categories="productsStore.categories"
      />

      <!-- Executive KPI Row -->
      <div class="kpi-grid" v-if="!loading">
        <MetricCard 
          title="Gross Sales Revenue" 
          :value="'$' + dashboardRevenue.toFixed(2)"
          :icon="DollarSign"
          iconBg="rgba(184, 241, 90, 0.15)"
          iconColor="var(--text-primary)"
        />
        <MetricCard 
          title="Total Checkouts" 
          :value="dashboardCheckouts"
          :icon="ShoppingCart"
          iconBg="rgba(99, 102, 241, 0.1)"
          iconColor="#4f46e5"
        />
        <MetricCard 
          title="Average Ticket Value" 
          :value="'$' + dashboardAvgTicket.toFixed(2)"
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

      <div class="reports-loading-state premium-card" v-else>
        <div class="spinner"></div>
        <p>Generating analytics datasets...</p>
      </div>

      <!-- Charts and Performance Section -->
      <div class="reports-dashboard-grid" v-if="!loading">
        
        <!-- Chart Row: Sales Trend -->
        <SectionCard title="Sales Trend Analysis" description="Visual overview of hourly transactions and sales growth index.">
          <div class="chart-placeholder-box">
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

        <!-- Cashier Performance (Real data calculated from invoices) -->
        <SectionCard title="Cashier Operations Ledger" description="Aggregated transactions processing speed and value metrics.">
          <div class="cashier-performance-list">
            <div class="perf-row" v-for="c in cashierPerformance" :key="c.name">
              <div class="perf-avatar">
                {{ c.name.charAt(0).toUpperCase() }}
              </div>
              <div class="perf-meta">
                <span class="perf-name">{{ c.name }}</span>
                <span class="perf-sub">Terminal Operator</span>
              </div>
              <div class="perf-values">
                <span class="perf-total-sales">${{ c.total.toFixed(2) }}</span>
                <span class="perf-count">{{ c.count }} orders</span>
              </div>
            </div>
            <div class="empty-state" v-if="cashierPerformance.length === 0">
              <p>No active shifts or operator checkouts registered.</p>
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
                  <tr v-for="sale in filteredSalesHistory" :key="sale.id">
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
                  <tr v-if="filteredSalesHistory.length === 0">
                    <td colspan="8" class="empty-row">No orders matching selected criteria recorded in register history.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>

    <!-- CUSTOM REPORT GENERATOR VIEW -->
    <div v-if="activeSubTab === 'generator'" class="generator-content">
      <!-- Customizable Criteria Card -->
      <div class="criteria-card premium-card">
        <div class="card-header-bar">
          <div>
            <h3 class="criteria-title">Custom Report Criteria</h3>
            <p class="criteria-desc">Select report parameters, time frames, and locations to analyze performance.</p>
          </div>
          <FileSpreadsheet class="criteria-header-icon" />
        </div>

        <form @submit.prevent="generateCustomReport" class="criteria-form">
          <div class="filters-grid">
            <div class="form-group">
              <label class="filter-label">Report Metric / Type</label>
              <select v-model="customReportFilters.metric" class="pos-input" required>
                <option value="sales_per_user">Sales per Cashier / User</option>
                <option value="day_checkouts">Daily Checkouts / Transaction Volume</option>
                <option value="shift_sales">Shift Sales Records</option>
                <option value="sales_per_month">Monthly Revenue Summary</option>
                <option value="sales_per_store">Sales per Store Location</option>
                <option value="sales_by_category">Sales by Product Category</option>
              </select>
            </div>

            <div class="form-group">
              <label class="filter-label">Sucursal / Store Location</label>
              <select v-model="customReportFilters.store_id" class="pos-input">
                <option value="">All Store Locations</option>
                <option v-for="st in storesList" :key="st.id" :value="st.id">
                  {{ st.name }} ({{ st.code.toUpperCase() }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="filter-label">Operator / Cashier</label>
              <select v-model="customReportFilters.cashier_id" class="pos-input">
                <option value="">All Cashiers / Users</option>
                <option v-for="u in cashiersList" :key="u.id" :value="u.id">
                  {{ u.username }} ({{ u.role.toUpperCase() }})
                </option>
              </select>
            </div>

            <div class="form-group date-range-group">
              <div class="date-input-wrapper">
                <label class="filter-label">Start Date</label>
                <input type="date" v-model="customReportFilters.start_date" class="pos-input" required />
              </div>
              <div class="date-input-wrapper">
                <label class="filter-label">End Date</label>
                <input type="date" v-model="customReportFilters.end_date" class="pos-input" required />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="pos-btn pos-btn-accent generate-btn" :disabled="customReportLoading">
              <TrendingUp class="btn-icon" v-if="!customReportLoading" />
              <span class="spinner-small" v-else></span>
              {{ customReportLoading ? 'Processing Query...' : 'Generate Performance Report' }}
            </button>
          </div>
        </form>
      </div>

      <!-- LOADING PREVIEW STATE -->
      <div class="reports-loading-state premium-card" v-if="customReportLoading">
        <div class="spinner"></div>
        <p>Compiling database aggregates and building report views...</p>
      </div>

      <!-- CUSTOM REPORT RESULTS CARD -->
      <div v-else-if="customReportResult" class="results-container">
        <!-- Summary Cards row -->
        <div class="kpi-grid">
          <MetricCard 
            title="Aggregated Count" 
            :value="summaryStats.count"
            :icon="ShoppingCart"
            iconBg="rgba(99, 102, 241, 0.1)"
            iconColor="#4f46e5"
          />
          <MetricCard 
            title="Total Sales Value" 
            :value="'$' + summaryStats.total.toFixed(2)"
            :icon="DollarSign"
            iconBg="rgba(184, 241, 90, 0.15)"
            iconColor="var(--text-primary)"
          />
          <MetricCard 
            title="Discounts Applied" 
            :value="'$' + summaryStats.discount.toFixed(2)"
            :icon="Award"
            iconBg="rgba(239, 68, 68, 0.1)"
            iconColor="var(--accent-danger)"
          />
          <MetricCard 
            title="Average Ticket Size" 
            :value="'$' + summaryStats.avgTicket.toFixed(2)"
            :icon="Package"
            iconBg="rgba(16, 185, 129, 0.1)"
            iconColor="var(--accent-success)"
          />
        </div>

        <!-- Report Result Detail Card -->
        <div class="report-result-card premium-card">
          <div class="result-card-header">
            <div>
              <h3 class="result-title">{{ reportTitle }}</h3>
              <p class="result-desc">
                Data period from <strong>{{ customReportResult.start_date }}</strong> to <strong>{{ customReportResult.end_date }}</strong>. 
                Filtered by store: <strong>{{ storeFilterName }}</strong>, cashier: <strong>{{ cashierFilterName }}</strong>.
              </p>
            </div>
            <div class="export-actions">
              <button class="pos-btn pos-btn-secondary" @click="exportCSV">
                <Download class="btn-icon" />
                Export to CSV
              </button>
              <button class="pos-btn pos-btn-secondary" @click="exportPDF">
                <Printer class="btn-icon" />
                Print / Save PDF
              </button>
            </div>
          </div>

          <!-- Dynamic Columns Result Table -->
          <div class="table-container">
            <div class="premium-table-wrapper">
              <table class="report-table">
                <thead>
                  <tr>
                    <th v-for="col in currentColumns" :key="col.key" :style="{ textAlign: col.align || 'left' }">
                      {{ col.label }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in customReportResult.data" :key="idx">
                    <td 
                      v-for="col in currentColumns" 
                      :key="col.key" 
                      :style="{ textAlign: col.align || 'left' }"
                      :class="{ 'font-bold': col.bold }"
                    >
                      {{ col.format ? col.format(row[col.key]) : row[col.key] }}
                    </td>
                  </tr>
                  <tr v-if="customReportResult.data.length === 0">
                    <td :colspan="currentColumns.length" class="empty-row">
                      No report records matching criteria found in this period.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- INITIAL BLANK STATE -->
      <div class="empty-generator-state premium-card" v-else>
        <FileText class="empty-state-icon" />
        <h4>Custom Report Generator</h4>
        <p>Select your desired performance metrics and date filters above, then click generate to review detailed analytical logs, export spreadsheet sheets, or download formatted PDF prints.</p>
      </div>
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
import { 
  DollarSign, ShoppingCart, Award, Package, 
  TrendingUp, FileSpreadsheet, Download, Printer, 
  Calendar, Filter, Users, Building, FileText 
} from 'lucide-vue-next'

const productsStore = useProductsStore()

const activeSubTab = ref('dashboard')

// Analytics Dashboard States
const salesByCategory = ref([])
const salesHistory = ref([])
const productsCount = ref(0)
const loading = ref(true)

// Filter binds for Dashboard
const selectedDateRange = ref('today')
const selectedCashier = ref('')
const selectedCategory = ref('')

// Real Lists fetched from backend
const storesList = ref([])
const cashiersList = ref([])

// Custom Report Generator States
const customReportLoading = ref(false)
const customReportResult = ref(null)

const todayStr = new Date().toISOString().split('T')[0]
const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
const thirtyDaysAgoStr = thirtyDaysAgo.toISOString().split('T')[0]

const customReportFilters = ref({
  metric: 'sales_per_user',
  store_id: '',
  cashier_id: '',
  start_date: thirtyDaysAgoStr,
  end_date: todayStr
})

const loadReports = async () => {
  loading.value = true
  try {
    const [catRes, historyRes, prodList, storesRes, usersRes] = await Promise.all([
      axios.get('/api/reports/sales-by-category'),
      axios.get('/api/sales/history'),
      productsStore.fetchProducts(),
      axios.get('/api/stores'),
      axios.get('/api/auth/users')
    ])
    
    salesByCategory.value = catRes.data
    salesHistory.value = historyRes.data
    productsCount.value = prodList.length
    storesList.value = storesRes.data
    cashiersList.value = usersRes.data
  } catch (err) {
    console.error('Failed to load reports data', err)
  } finally {
    loading.value = false
  }
}

// Compute filtered history for the dashboard view
const filteredSalesHistory = computed(() => {
  return salesHistory.value.filter(sale => {
    // Filter by Cashier
    if (selectedCashier.value && sale.cashier_id !== parseInt(selectedCashier.value)) {
      return false
    }
    
    // Filter by Date Range
    const saleDate = new Date(sale.created_at)
    const now = new Date()
    
    if (selectedDateRange.value === 'today') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      if (saleDate < today) return false
    } else if (selectedDateRange.value === 'yesterday') {
      const yesterdayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1)
      const yesterdayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      if (saleDate < yesterdayStart || saleDate >= yesterdayEnd) return false
    } else if (selectedDateRange.value === 'week') {
      // Start of current week (Sunday)
      const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay())
      startOfWeek.setHours(0,0,0,0)
      if (saleDate < startOfWeek) return false
    } else if (selectedDateRange.value === 'month') {
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      if (saleDate < startOfMonth) return false
    }
    
    return true
  })
})

const dashboardRevenue = computed(() => {
  return filteredSalesHistory.value.reduce((sum, sale) => sum + sale.total, 0)
})

const dashboardCheckouts = computed(() => {
  return filteredSalesHistory.value.length
})

const dashboardAvgTicket = computed(() => {
  if (dashboardCheckouts.value === 0) return 0
  return dashboardRevenue.value / dashboardCheckouts.value
})

const cashierPerformance = computed(() => {
  const ledger = {}
  filteredSalesHistory.value.forEach(sale => {
    const name = sale.cashier_name || 'Unknown'
    if (!ledger[name]) {
      ledger[name] = { name, total: 0, count: 0 }
    }
    ledger[name].total += sale.total
    ledger[name].count += 1
  })
  
  if (Object.keys(ledger).length === 0) {
    return cashiersList.value
      .filter(u => u.role !== 'admin')
      .map(c => ({ name: c.username, total: 0, count: 0 }))
  }
  return Object.values(ledger).sort((a, b) => b.total - a.total)
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

// Custom Report Logic
const generateCustomReport = async () => {
  customReportLoading.value = true
  try {
    const response = await axios.get('/api/reports/custom', {
      params: {
        metric: customReportFilters.value.metric,
        store_id: customReportFilters.value.store_id || null,
        cashier_id: customReportFilters.value.cashier_id || null,
        start_date: customReportFilters.value.start_date,
        end_date: customReportFilters.value.end_date
      }
    })
    customReportResult.value = response.data
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to generate custom report')
    console.error(err)
  } finally {
    customReportLoading.value = false
  }
}

// Columns configuration per metric
const reportCols = {
  sales_per_user: [
    { key: 'cashier', label: 'Cashier Username', bold: true },
    { key: 'store', label: 'Store Location' },
    { key: 'sales_count', label: 'Checkouts Count', align: 'right' },
    { key: 'subtotal', label: 'Subtotal', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'discount', label: 'Discounts', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'tax', label: 'Tax', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'total', label: 'Gross Total', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ],
  day_checkouts: [
    { key: 'date', label: 'Checkout Date', bold: true },
    { key: 'sales_count', label: 'Transactions', align: 'right' },
    { key: 'subtotal', label: 'Subtotal', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'discount', label: 'Discounts', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'tax', label: 'Tax', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'average_ticket', label: 'Avg Ticket Value', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'total', label: 'Total Revenue', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ],
  shift_sales: [
    { key: 'shift_id', label: 'Shift ID', bold: true },
    { key: 'cashier', label: 'Cashier Name' },
    { key: 'start_time', label: 'Open Time', format: (v) => v ? new Date(v).toLocaleString() : '-' },
    { key: 'end_time', label: 'Close Time', format: (v) => v ? new Date(v).toLocaleString() : 'ACTIVE' },
    { key: 'start_cash', label: 'Starting Cash', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'end_cash', label: 'Closing Cash', align: 'right', format: (v) => v ? '$' + v.toFixed(2) : '-' },
    { key: 'status', label: 'Status' },
    { key: 'sales_count', label: 'Sales Count', align: 'right' },
    { key: 'total_sales', label: 'Total Sales', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ],
  sales_per_month: [
    { key: 'month', label: 'Month Period', bold: true },
    { key: 'sales_count', label: 'Checkouts', align: 'right' },
    { key: 'subtotal', label: 'Subtotal', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'discount', label: 'Discounts Given', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'tax', label: 'Tax', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'average_ticket', label: 'Avg Checkout Value', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'total', label: 'Monthly Revenue', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ],
  sales_per_store: [
    { key: 'store_name', label: 'Store Name', bold: true },
    { key: 'store_code', label: 'Code' },
    { key: 'sales_count', label: 'Checkouts Count', align: 'right' },
    { key: 'subtotal', label: 'Subtotal', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'discount', label: 'Discounts', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'tax', label: 'Tax', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'average_ticket', label: 'Avg Ticket Value', align: 'right', format: (v) => '$' + v.toFixed(2) },
    { key: 'total', label: 'Gross Revenue', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ],
  sales_by_category: [
    { key: 'category', label: 'Category Name', bold: true },
    { key: 'items_sold_count', label: 'Items Count', align: 'right' },
    { key: 'total_quantity', label: 'Total Qty Sold', align: 'right', format: (v) => v.toFixed(2) },
    { key: 'revenue', label: 'Total Category Revenue', align: 'right', format: (v) => '$' + v.toFixed(2), bold: true }
  ]
}

const currentColumns = computed(() => {
  if (!customReportResult.value) return []
  return reportCols[customReportResult.value.metric] || []
})

const reportTitle = computed(() => {
  if (!customReportResult.value) return ''
  const titles = {
    sales_per_user: 'Operator Performance & Sales Audit Ledger',
    day_checkouts: 'Daily Transaction Checkouts Volume Register',
    shift_sales: 'Audit Shift Logs & Cash Drawers Ledger',
    sales_per_month: 'Monthly Gross Revenue Growth Report',
    sales_per_store: 'Sucursales / Store Performance Comparative Analysis',
    sales_by_category: 'Product Catalog Sales Distribution by Category'
  }
  return titles[customReportResult.value.metric] || 'Detailed Performance Analysis'
})

const storeFilterName = computed(() => {
  if (!customReportFilters.value.store_id) return 'All Store Locations'
  const store = storesList.value.find(s => s.id === parseInt(customReportFilters.value.store_id))
  return store ? `${store.name} (${store.code})` : 'Specific Location'
})

const cashierFilterName = computed(() => {
  if (!customReportFilters.value.cashier_id) return 'All Cashiers'
  const user = cashiersList.value.find(u => u.id === parseInt(customReportFilters.value.cashier_id))
  return user ? user.username : 'Specific Cashier'
})

const summaryStats = computed(() => {
  if (!customReportResult.value || !customReportResult.value.data.length) {
    return { count: 0, total: 0, discount: 0, avgTicket: 0 }
  }
  
  const data = customReportResult.value.data
  const m = customReportResult.value.metric
  
  if (m === 'sales_by_category') {
    const qty = data.reduce((sum, item) => sum + (item.total_quantity || 0), 0)
    const rev = data.reduce((sum, item) => sum + (item.revenue || 0), 0)
    return {
      count: data.length, // total categories count
      total: rev,
      discount: 0,
      avgTicket: qty > 0 ? rev / qty : 0
    }
  }
  
  const count = data.reduce((sum, item) => sum + (item.sales_count || 0), 0)
  const total = data.reduce((sum, item) => sum + (item.total || item.total_sales || 0), 0)
  const discount = data.reduce((sum, item) => sum + (item.discount || 0), 0)
  const avgTicket = count > 0 ? total / count : 0
  
  return {
    count,
    total,
    discount,
    avgTicket
  }
})

// Export CSV Spreadsheet
const exportCSV = () => {
  if (!customReportResult.value) return
  const cols = currentColumns.value
  const data = customReportResult.value.data
  
  const escapeCSV = (val) => {
    if (val === null || val === undefined) return ''
    let str = String(val)
    if (str.includes(',') || str.includes('\n') || str.includes('"')) {
      str = '"' + str.replace(/"/g, '""') + '"'
    }
    return str
  }

  // Format headers
  const header = cols.map(c => escapeCSV(c.label)).join(',')
  
  // Format rows
  const rows = data.map(row => {
    return cols.map(col => {
      const val = row[col.key]
      const formatted = col.format ? col.format(val) : val
      return escapeCSV(formatted)
    }).join(',')
  }).join('\n')
  
  const content = '\uFEFF' + header + '\n' + rows
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement("a")
  link.href = url
  link.setAttribute("download", `report_${customReportResult.value.metric}_${customReportResult.value.start_date}_to_${customReportResult.value.end_date}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export Print-Ready PDF
const exportPDF = () => {
  if (!customReportResult.value) return
  
  const printWindow = window.open('', '_blank')
  
  let html = `
    <html>
    <head>
      <title>ApexPOS Performance Report</title>
      <style>
        body {
          font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
          color: #1f2937;
          padding: 40px;
          background: #fff;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 3px solid #b8f15a;
          padding-bottom: 20px;
          margin-bottom: 30px;
        }
        .title {
          font-size: 22px;
          font-weight: 800;
          margin: 0;
          color: #111827;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .meta {
          font-size: 13px;
          color: #4b5563;
          line-height: 1.6;
        }
        .kpi-row {
          display: flex;
          gap: 20px;
          margin-bottom: 30px;
        }
        .kpi-card {
          flex: 1;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          background: #f9fafb;
        }
        .kpi-title {
          font-size: 10px;
          font-weight: 700;
          color: #6b7280;
          text-transform: uppercase;
          margin-bottom: 6px;
          letter-spacing: 0.5px;
        }
        .kpi-value {
          font-size: 20px;
          font-weight: 800;
          color: #111827;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
          font-size: 13px;
        }
        th, td {
          padding: 12px 14px;
          text-align: left;
          border-bottom: 1px solid #e5e7eb;
        }
        th {
          background-color: #f3f4f6;
          color: #374151;
          font-weight: 700;
          text-transform: uppercase;
          font-size: 10px;
          letter-spacing: 0.5px;
        }
        tr:nth-child(even) td {
          background-color: #f9fafb;
        }
        .text-right { text-align: right; }
        .font-bold { font-weight: 700; }
        .footer {
          margin-top: 60px;
          border-top: 1px solid #e5e7eb;
          padding-top: 20px;
          text-align: center;
          font-size: 11px;
          color: #9ca3af;
        }
        @media print {
          body { padding: 0; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <h1 class="title">ApexPOS Performance Analytics</h1>
          <p class="meta" style="margin-top: 8px; margin-bottom: 0;">
            <strong>Metric:</strong> ${reportTitle.value}<br>
            <strong>Period:</strong> ${customReportResult.value.start_date} to ${customReportResult.value.end_date}
          </p>
        </div>
        <div class="meta" style="text-align: right;">
          <strong>Generated:</strong> ${new Date().toLocaleString()}<br>
          <strong>Store:</strong> ${storeFilterName.value}<br>
          <strong>Operator:</strong> ${cashierFilterName.value}
        </div>
      </div>

      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-title">${customReportResult.value.metric === 'sales_by_category' ? 'Categories Count' : 'Transactions Count'}</div>
          <div class="kpi-value">${summaryStats.value.count}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Gross Revenue</div>
          <div class="kpi-value">$${summaryStats.value.total.toFixed(2)}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Discounts Applied</div>
          <div class="kpi-value">$${summaryStats.value.discount.toFixed(2)}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Average Value</div>
          <div class="kpi-value">$${summaryStats.value.avgTicket.toFixed(2)}</div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            ${cols.map(col => `<th class="${col.align === 'right' ? 'text-right' : ''}">${col.label}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              ${cols.map(col => {
                const val = row[col.key];
                const formatted = col.format ? col.format(val) : val;
                return `<td class="${col.align === 'right' ? 'text-right' : ''} ${col.bold ? 'font-bold' : ''}">${formatted}</td>`;
              }).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>

      <div class="footer">
        ApexPOS POS Management System. System-Generated Official Document. Page 1 of 1.
      </div>

      <script>
        window.onload = function() {
          window.print();
        }
      <\/script>
    </body>
    </html>
  `
  
  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
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

/* Submenu Navigation */
.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  background-color: var(--bg-body);
  color: var(--text-primary);
}

.tab-btn.active {
  background-color: var(--accent-lime);
  color: var(--bg-app);
  font-weight: 600;
}

.tab-icon {
  width: 18px;
  height: 18px;
}

.tab-content-wrapper {
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

/* Custom Report Generator styling */
.criteria-card {
  padding: 24px;
  margin-bottom: 24px;
}

.card-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.criteria-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.criteria-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.criteria-header-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-lime);
}

.criteria-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.date-range-group {
  display: flex;
  gap: 12px;
}

.date-input-wrapper {
  flex: 1;
}

.filter-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  padding: 12px 24px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: var(--bg-app);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.results-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-result-card {
  padding: 24px;
}

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 20px;
  flex-wrap: wrap;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.result-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.export-actions {
  display: flex;
  gap: 10px;
}

.empty-generator-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-generator-state h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 16px 0 8px 0;
}

.empty-generator-state p {
  font-size: 14px;
  max-width: 500px;
  margin: 0;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 24px;
  font-size: 0.9rem;
}
</style>
