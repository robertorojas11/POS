<template>
  <div class="products-container">
    <div class="header-actions">
      <!-- Search & Category Filters -->
      <div class="filters">
        <input 
          type="text" 
          v-model="search" 
          placeholder="Search products..." 
          class="pos-input search-box"
          @input="fetchData"
        />
        <select v-model="selectedCategory" class="pos-input category-select" @change="fetchData">
          <option :value="null">All Categories</option>
          <option v-for="cat in productsStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      
      <button class="pos-btn pos-btn-primary" @click="openAddModal">
        + Add New Product
      </button>
    </div>

    <!-- Product Table -->
    <div class="pos-card table-panel">
      <div class="table-container" v-if="!loading">
        <table class="report-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Barcode</th>
              <th>Name</th>
              <th>Category</th>
              <th class="text-right">Price</th>
              <th class="text-right">Cost Price</th>
              <th class="text-right">Stock Qty</th>
              <th class="text-right">Min Stock</th>
              <th>Status</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prod in productsStore.products" :key="prod.id">
              <td><code>{{ prod.sku }}</code></td>
              <td>{{ prod.barcode || 'N/A' }}</td>
              <td><strong>{{ prod.name }}</strong></td>
              <td>{{ prod.category_name || 'Unassigned' }}</td>
              <td class="text-right text-green font-bold">${{ prod.price.toFixed(2) }}</td>
              <td class="text-right">${{ prod.cost_price.toFixed(2) }}</td>
              <td class="text-right" :class="{ 'text-rose font-bold': prod.stock_quantity <= prod.min_stock_level }">
                {{ prod.stock_quantity }} <span class="text-muted text-xs">{{ prod.uom }}</span>
              </td>
              <td class="text-right">{{ prod.min_stock_level }} <span class="text-muted text-xs">{{ prod.uom }}</span></td>
              <td>
                <span class="status-badge" :class="prod.is_active ? 'active' : 'inactive'">
                  {{ prod.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="text-center">
                <button class="pos-btn pos-btn-secondary sm-btn" @click="openEditModal(prod)">
                  Edit
                </button>
              </td>
            </tr>
            <tr v-if="productsStore.products.length === 0">
              <td colspan="10" class="empty-row">No products matching the selected criteria.</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="loading-state" v-else>
        <div class="spinner"></div>
      </div>
    </div>

    <!-- Modal: Add / Edit Product -->
    <div class="modal-overlay" v-if="showModal">
      <div class="modal-content pos-card product-modal">
        <h3>{{ isEditMode ? 'Edit Product Details' : 'Add New Product' }}</h3>
        
        <form @submit.prevent="saveProduct" class="product-form">
          <div class="form-grid">
            <div class="form-group">
              <label>SKU</label>
              <input type="text" v-model="formData.sku" class="pos-input" :disabled="isEditMode" required />
            </div>
            
            <div class="form-group">
              <label>Barcode</label>
              <input type="text" v-model="formData.barcode" class="pos-input" />
            </div>
            
            <div class="form-group span-2">
              <label>Product Name</label>
              <input type="text" v-model="formData.name" class="pos-input" required />
            </div>

            <div class="form-group span-2">
              <label>Description</label>
              <textarea v-model="formData.description" class="pos-input text-area"></textarea>
            </div>

            <div class="form-group">
              <label>Retail Price ($)</label>
              <input type="number" v-model="formData.price" class="pos-input" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label>Cost Price ($)</label>
              <input type="number" v-model="formData.cost_price" class="pos-input" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label>Stock Quantity</label>
              <input type="number" v-model="formData.stock_quantity" class="pos-input" min="0" step="any" required />
            </div>

            <div class="form-group">
              <label>Min Alert Level</label>
              <input type="number" v-model="formData.min_stock_level" class="pos-input" min="0" step="any" required />
            </div>

            <div class="form-group">
              <label>Unit of Measurement</label>
              <select v-model="formData.uom" class="pos-input">
                <option value="pieces">Pieces (pcs)</option>
                <option value="liters">Liters (L)</option>
                <option value="gallons">Gallons (gal)</option>
                <option value="kilograms">Kilograms (kg)</option>
                <option value="grams">Grams (g)</option>
                <option value="pounds">Pounds (lb)</option>
                <option value="ounces">Ounces (oz)</option>
              </select>
            </div>

            <div class="form-group">
              <label>Category</label>
              <select v-model="formData.category_id" class="pos-input">
                <option :value="null">None</option>
                <option v-for="cat in productsStore.categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group checkbox-group" v-if="isEditMode">
              <label>
                <input type="checkbox" v-model="formData.is_active" />
                Product Active
              </label>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="pos-btn pos-btn-secondary" @click="showModal = false">Cancel</button>
            <button type="submit" class="pos-btn pos-btn-primary">Save Product</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductsStore } from '@/store/products'

const productsStore = useProductsStore()
const loading = ref(false)
const search = ref('')
const selectedCategory = ref(null)

// Modal setup
const showModal = ref(false)
const isEditMode = ref(false)
const editProductId = ref(null)

const formData = ref({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  price: 0,
  cost_price: 0,
  stock_quantity: 0,
  min_stock_level: 5,
  uom: 'pieces',
  category_id: null,
  is_active: true
})

const fetchData = async () => {
  loading.value = true
  const params = {}
  if (search.value) params.search = search.value
  if (selectedCategory.value !== null) params.category_id = selectedCategory.value
  
  await productsStore.fetchProducts(params)
  loading.value = false
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
    uom: prod.uom || 'pieces',
    category_id: prod.category_id,
    is_active: prod.is_active
  }
  showModal.value = true
}

const saveProduct = async () => {
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
</script>

<style scoped>
.products-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 16px;
}

.search-box {
  width: 250px;
}

.category-select {
  width: 200px;
}

.table-panel {
  padding: 16px;
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
.text-center { text-align: center; }
.text-green { color: var(--accent-success); }
.text-rose { color: var(--accent-danger); }
.font-bold { font-weight: 600; }

.status-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.status-badge.active { background-color: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.inactive { background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; }

.sm-btn {
  padding: 6px 12px;
  font-size: 0.8rem;
}

.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 40px !important;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 250px;
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

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.product-modal {
  width: 550px;
}

.product-form {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.span-2 {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.text-area {
  min-height: 80px;
  resize: vertical;
}

.checkbox-group {
  grid-column: span 2;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
