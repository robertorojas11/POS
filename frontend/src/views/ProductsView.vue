<template>
  <div class="products-catalog-layout">
    <!-- Header Control Bar -->
    <div class="catalog-control-header premium-card">
      <div class="catalog-filters">
        <div class="search-box">
          <Search class="search-icon" />
          <input 
            type="text" 
            v-model="search" 
            placeholder="Search catalog SKU, name..." 
            class="pos-input with-left-icon"
          />
        </div>
        
        <select v-model="selectedCategory" class="pos-input category-select">
          <option :value="null">All Categories</option>
          <option v-for="cat in productsStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <div class="catalog-actions" v-if="isAdminOrManager">
        <button class="pos-btn pos-btn-accent" @click="openAddModal">
          <Plus class="action-icon" />
          Add Product
        </button>
      </div>
    </div>

    <!-- Card-Based Catalog Browser -->
    <div class="catalog-cards-panel" v-if="!loading">
      <div class="catalog-grid" v-if="filteredProducts.length">
        <div 
          v-for="prod in filteredProducts" 
          :key="prod.id"
          class="product-card"
          @click="openDetailsDrawer(prod)"
        >
          <div class="product-image-container">
            <div class="product-placeholder">
              <span class="product-initials">{{ getInitials(prod.name) }}</span>
            </div>
            <div class="stock-badge" :class="getStockClass(prod)">
              {{ formatDecimal(prod.stock_quantity) }} {{ shortUom(prod.uom) }}
            </div>
          </div>
          
          <div class="product-info">
            <div class="product-meta">
              <h4 class="product-name" :title="prod.name">{{ prod.name }}</h4>
              <span class="product-sku">{{ prod.sku }}</span>
              <span class="product-category">{{ prod.category_name || 'Unassigned' }}</span>
            </div>
            
            <div class="product-action-row">
              <div class="price-group">
                <span class="product-price">${{ Number(prod.price).toFixed(2) }}</span>
                <span class="product-price-tax">Cost: ${{ Number(prod.cost_price).toFixed(2) }}</span>
              </div>
              
              <button 
                class="add-btn edit-btn" 
                @click.stop="openEditModal(prod)" 
                v-if="isAdminOrManager"
                title="Edit Product"
              >
                <Edit2 class="add-icon" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="empty-catalog-state" v-else>
        <Package class="empty-state-icon" />
        <p>No products found matching filters.</p>
      </div>
    </div>

    <div class="catalog-loading-state" v-else>
      <div class="spinner"></div>
      <p>Synchronizing local catalog...</p>
    </div>

    <!-- Slide-Over Product Detail Drawer -->
    <div class="drawer-overlay" v-if="showDetailDrawer" @click="showDetailDrawer = false">
      <div class="slide-over-drawer" @click.stop>
        <div class="drawer-header">
          <h3>Product Parameters</h3>
          <button class="drawer-close-x" @click="showDetailDrawer = false">
            <X class="close-icon" />
          </button>
        </div>
        
        <div class="drawer-body" v-if="selectedProductDetails">
          <div class="drawer-img-pane">
            <div class="drawer-large-initials">
              {{ selectedProductDetails.name.charAt(0) }}
            </div>
          </div>

          <div class="drawer-section">
            <h4 class="drawer-prod-name">{{ selectedProductDetails.name }}</h4>
            <span class="drawer-prod-sku">{{ selectedProductDetails.sku }}</span>
          </div>

          <div class="drawer-section card-info-box">
            <div class="info-row">
              <span class="info-label">Barcode</span>
              <span class="info-val"><code>{{ selectedProductDetails.barcode || 'None' }}</code></span>
            </div>
            <div class="info-row">
              <span class="info-label">Category</span>
              <span class="info-val">{{ selectedProductDetails.category_name || 'Unassigned' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Selling Unit</span>
              <span class="info-val uom-val">{{ shortUom(selectedProductDetails.uom) }}</span>
            </div>
          </div>

          <div class="drawer-section">
            <h5 class="section-subtitle">Stock & Inventory</h5>
            <div class="drawer-grid-kpis">
              <div class="drawer-kpi-pill">
                <span class="kpi-label">Current Stock</span>
                <span class="kpi-val" :class="{ 'text-danger': selectedProductDetails.stock_quantity <= selectedProductDetails.min_stock_level }">
                  {{ formatDecimal(selectedProductDetails.stock_quantity) }}
                </span>
              </div>
              <div class="drawer-kpi-pill">
                <span class="kpi-label">Min Alert Level</span>
                <span class="kpi-val">{{ formatDecimal(selectedProductDetails.min_stock_level) }}</span>
              </div>
              <div class="drawer-kpi-pill">
                <span class="kpi-label">Min Sale Qty</span>
                <span class="kpi-val">{{ formatDecimal(selectedProductDetails.min_sale_qty) }}</span>
              </div>
            </div>
          </div>

          <div class="drawer-section">
            <h5 class="section-subtitle">Financial Margins</h5>
            <div class="drawer-grid-kpis">
              <div class="drawer-kpi-pill">
                <span class="kpi-label">Retail Price</span>
                <span class="kpi-val">${{ Number(selectedProductDetails.price).toFixed(2) }}</span>
              </div>
              <div class="drawer-kpi-pill">
                <span class="kpi-label">Cost Price</span>
                <span class="kpi-val">${{ Number(selectedProductDetails.cost_price).toFixed(2) }}</span>
              </div>
            </div>
            <div class="margin-analytics-card">
              <span>Gross Profit Margin</span>
              <strong>{{ calculateMargin(selectedProductDetails) }}%</strong>
            </div>
          </div>

          <div class="drawer-section" v-if="selectedProductDetails.description">
            <h5 class="section-subtitle">Description</h5>
            <p class="drawer-description-text">{{ selectedProductDetails.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Add / Edit Product -->
    <div class="modal-overlay" v-if="showModal">
      <div class="modal-content premium-card product-modal">
        <h3>{{ isEditMode ? 'Modify Product Parameters' : 'Register New Product' }}</h3>
        
        <form @submit.prevent="saveProduct" class="product-form">
          <div class="form-grid">
            <div class="form-group">
              <label class="pos-label">SKU (Unique)</label>
              <input type="text" v-model="formData.sku" class="pos-input" :disabled="isEditMode" required />
            </div>
            
            <div class="form-group">
              <label class="pos-label">Barcode</label>
              <input type="text" v-model="formData.barcode" class="pos-input" />
            </div>
            
            <div class="form-group span-2">
              <label class="pos-label">Product Name</label>
              <input type="text" v-model="formData.name" class="pos-input" required />
            </div>

            <div class="form-group span-2">
              <label class="pos-label">Description</label>
              <textarea v-model="formData.description" class="pos-input text-area"></textarea>
            </div>

            <div class="form-group">
              <label class="pos-label">Retail Price ($)</label>
              <input type="number" v-model="formData.price" class="pos-input" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label class="pos-label">Cost Price ($)</label>
              <input type="number" v-model="formData.cost_price" class="pos-input" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label class="pos-label">Initial Stock Level</label>
              <input 
                type="number" 
                v-model.number="formData.stock_quantity" 
                class="pos-input" 
                min="0" 
                step="any" 
                @keypress="handleStockKeyPress"
                required 
              />
            </div>

            <div class="form-group">
              <label class="pos-label">Min Warning Level</label>
              <input 
                type="number" 
                v-model.number="formData.min_stock_level" 
                class="pos-input" 
                min="0" 
                step="any" 
                @keypress="handleStockKeyPress"
                required 
              />
            </div>

            <div class="form-group">
              <label class="pos-label">Min Sale Quantity (Step)</label>
              <input 
                type="number" 
                v-model.number="formData.min_sale_qty" 
                class="pos-input" 
                min="0.001" 
                step="any" 
                @keypress="handleStockKeyPress"
                required 
              />
            </div>

            <div class="form-group">
              <label class="pos-label">Unit of Measurement (UOM)</label>
              <select v-model="formData.uom" class="pos-input">
                <option value="pieces">pieces - pz</option>
                <option value="kilograms">kilograms - kg</option>
                <option value="pounds">pounds - lb</option>
                <option value="liters">liters - l</option>
                <option value="meters">meters - m</option>
              </select>
            </div>

            <div class="form-group">
              <label class="pos-label">Category</label>
              <select v-model="formData.category_id" class="pos-input">
                <option :value="null">None</option>
                <option v-for="cat in productsStore.categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group checkbox-group" v-if="isEditMode">
              <label class="checkbox-container">
                <input type="checkbox" v-model="formData.is_active" />
                <span class="checkmark"></span>
                Product Active in Catalog
              </label>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="pos-btn pos-btn-secondary" @click="showModal = false">Cancel</button>
            <button type="submit" class="pos-btn pos-btn-accent">Save Parameters</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useProductsStore } from '@/store/products'
import { useAuthStore } from '@/store/auth'
import { Search, Plus, Package, Edit2, X } from 'lucide-vue-next'

const productsStore = useProductsStore()
const authStore = useAuthStore()

const isAdminOrManager = computed(() => ['admin', 'manager'].includes(authStore.user?.role?.toLowerCase()))
const loading = ref(false)
const search = ref('')
const selectedCategory = ref(null)

// Modal setup
const showModal = ref(false)
const isEditMode = ref(false)
const editProductId = ref(null)

// Slide drawer details
const showDetailDrawer = ref(false)
const selectedProductDetails = ref(null)

const formData = ref({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  price: 0,
  cost_price: 0,
  stock_quantity: 0,
  min_stock_level: 5,
  min_sale_qty: 1.0,
  uom: 'pieces',
  category_id: null,
  is_active: true
})

const getInitials = (name) => {
  return name?.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase() || 'P'
}

const formatDecimal = (val) => {
  const v = parseFloat(val)
  return Number.isInteger(v) ? v.toString() : v.toFixed(3)
}

const getStockClass = (prod) => {
  const stock = parseFloat(prod.stock_quantity)
  if (stock <= 0) return 'out-of-stock'
  if (stock <= prod.min_stock_level) return 'low-stock'
  return 'in-stock'
}

const calculateMargin = (prod) => {
  const p = parseFloat(prod.price)
  const c = parseFloat(prod.cost_price)
  if (p === 0) return '0.00'
  return (((p - c) / p) * 100).toFixed(2)
}

const filteredProducts = computed(() => {
  let list = productsStore.products
  if (selectedCategory.value !== null) {
    list = list.filter(p => p.category_id === selectedCategory.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(p => 
      p.name.toLowerCase().includes(q) || 
      p.sku.toLowerCase().includes(q) || 
      (p.barcode && p.barcode.toLowerCase().includes(q))
    )
  }
  return list
})

const fetchData = async () => {
  loading.value = true
  await productsStore.fetchProducts()
  loading.value = false
}

const openDetailsDrawer = (prod) => {
  selectedProductDetails.value = prod
  showDetailDrawer.value = true
}

const openAddModal = () => {
  isEditMode.value = false
  editProductId.value = null
  formData.value = {
    sku: '',
    barcode: '',
    name: '',
    description: '',
    price: 0,
    cost_price: 0,
    stock_quantity: 0,
    min_stock_level: 5,
    min_sale_qty: 1.0,
    uom: 'pieces',
    category_id: null,
    is_active: true
  }
  showModal.value = true
}

const openEditModal = (prod) => {
  isEditMode.value = true
  editProductId.value = prod.id
  formData.value = {
    sku: prod.sku,
    barcode: prod.barcode || '',
    name: prod.name,
    description: prod.description || '',
    price: prod.price,
    cost_price: prod.cost_price,
    stock_quantity: prod.stock_quantity,
    min_stock_level: prod.min_stock_level,
    min_sale_qty: prod.min_sale_qty || 1.0,
    uom: prod.uom || 'pieces',
    category_id: prod.category_id,
    is_active: prod.is_active
  }
  showModal.value = true
}

const handleStockKeyPress = (event) => {
  const charCode = event.which ? event.which : event.keyCode
  const charStr = String.fromCharCode(charCode)
  
  // Block negative sign (-), plus sign (+), and exponent (e, E)
  if (['-', '+', 'e', 'E'].includes(charStr)) {
    event.preventDefault()
    return
  }
  
  // Block decimal separator if pieces UOM is selected
  const isPieces = formData.value.uom?.toLowerCase() === 'pieces'
  if (isPieces && ['.', ','].includes(charStr)) {
    event.preventDefault()
  }
}

const saveProduct = async () => {
  // Validate stock_quantity, min_stock_level, min_sale_qty
  let stock = parseFloat(formData.value.stock_quantity)
  let minStock = parseFloat(formData.value.min_stock_level)
  let minSale = parseFloat(formData.value.min_sale_qty)
  
  if (isNaN(stock) || stock < 0) {
    alert('Stock quantity must be a non-negative number')
    return
  }
  if (isNaN(minStock) || minStock < 0) {
    alert('Min warning level must be a non-negative number')
    return
  }
  if (isNaN(minSale) || minSale <= 0) {
    alert('Min sale quantity must be a positive number')
    return
  }
  
  // If product UOM is pieces, we don't accept fractional numbers!
  const isPieces = formData.value.uom?.toLowerCase() === 'pieces'
  if (isPieces) {
    if (stock % 1 !== 0) {
      alert('Stock quantity must be an integer for pieces UOM')
      return
    }
    if (minStock % 1 !== 0) {
      alert('Min warning level must be an integer for pieces UOM')
      return
    }
    if (minSale % 1 !== 0) {
      alert('Min sale quantity must be an integer for pieces UOM')
      return
    }
  }
  
  // Ensure formatted values are set in formData
  formData.value.stock_quantity = stock
  formData.value.min_stock_level = minStock
  formData.value.min_sale_qty = minSale

  let result = null
  if (isEditMode.value) {
    result = await productsStore.updateProduct(editProductId.value, formData.value)
  } else {
    result = await productsStore.createProduct(formData.value)
  }
  
  if (result) {
    showModal.value = false
    await fetchData()
  } else {
    alert(productsStore.error || 'Failed to save product details')
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    productsStore.fetchCategories(),
    fetchData()
  ])
  loading.value = false
})

const shortUom = (uom) => {
  const map = {
    'pieces': 'pz',
    'kilograms': 'kg',
    'liters': 'l',
    'litters': 'l',
    'pounds': 'lb',
    'ounces': 'oz',
    'meters': 'm'
  }
  return map[uom?.toLowerCase()] || uom
}
</script>

<style scoped>
.products-catalog-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Control header */
.catalog-control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px !important;
}

.catalog-filters {
  display: flex;
  gap: 16px;
  flex-grow: 1;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 13px;
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.category-select {
  width: 200px;
}

/* Catalog grids */
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.product-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal), border-color var(--transition-fast);
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--text-muted);
}

.product-image-container {
  height: 120px;
  background-color: #f9fafb;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid #f3f4f6;
}

.product-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-initials {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.stock-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 12px;
}

.stock-badge.in-stock {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.stock-badge.low-stock {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--accent-warning);
}

.stock-badge.out-of-stock {
  background-color: rgba(255, 94, 94, 0.1);
  color: var(--accent-danger);
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-grow: 1;
}

.product-meta {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-sku {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 1px;
}

.product-category {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.product-action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.product-price {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.add-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-lime);
  color: var(--accent-lime-text);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.add-btn:hover {
  background-color: var(--accent-lime-hover);
  transform: scale(1.05);
}

.add-icon {
  width: 16px;
  height: 16px;
  stroke-width: 3px;
}

.price-group {
  display: flex;
  flex-direction: column;
}

.product-price-tax {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  margin-top: 1px;
}

.empty-catalog-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  color: var(--text-muted);
  gap: 12px;
}

.empty-state-icon {
  width: 48px;
  height: 48px;
  stroke-width: 1.5px;
}

.catalog-loading-state {
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

/* Modals inputs checks container styling */
.modal-overlay {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.product-modal {
  width: 540px;
  max-width: 95%;
  animation: modalFade 0.2s ease-out;
}

@keyframes modalFade {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.product-modal h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 24px;
}

.product-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.span-2 {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pos-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.text-area {
  min-height: 80px;
  resize: vertical;
}

.checkbox-group {
  grid-column: span 2;
  margin-top: 8px;
}

/* Custom Checkbox */
.checkbox-container {
  display: block;
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 1px;
  left: 0;
  height: 18px;
  width: 18px;
  background-color: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: var(--accent-lime);
  border-color: var(--accent-lime-hover);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 6px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid var(--accent-lime-text);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

/* Slide-Over Drawer Details */
.drawer-overlay {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0,0,0,0.3);
  z-index: 150;
  display: flex;
  justify-content: flex-end;
}

.slide-over-drawer {
  width: 440px;
  max-width: 90%;
  height: 100%;
  background-color: var(--bg-card);
  box-shadow: -10px 0 30px rgba(0,0,0,0.05);
  animation: drawerSlide 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  padding: 32px;
  overflow-y: auto;
}

@keyframes drawerSlide {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.drawer-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
}

.drawer-close-x {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
}

.drawer-close-x:hover {
  color: var(--text-primary);
}

.close-icon {
  width: 20px;
  height: 20px;
}

.drawer-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.drawer-img-pane {
  height: 140px;
  background-color: #f9fafb;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-large-initials {
  font-size: 3rem;
  font-weight: 800;
  color: var(--text-muted);
}

.drawer-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer-prod-name {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
}

.drawer-prod-sku {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: monospace;
}

.card-info-box {
  background-color: #f9fafb;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
}

.info-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.info-val {
  font-weight: 700;
  color: var(--text-primary);
}

.uom-val {
  text-transform: uppercase;
  background-color: #ffffff;
  border: 1px solid var(--border-color);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.78rem;
}

.section-subtitle {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 6px;
}

.drawer-grid-kpis {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.drawer-kpi-pill {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.kpi-val {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
}

.margin-analytics-card {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(184, 241, 90, 0.15);
  color: #557c11;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 700;
}

.margin-analytics-card strong {
  font-size: 1.1rem;
}

.drawer-description-text {
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-secondary);
}
</style>
