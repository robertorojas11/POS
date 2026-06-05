<template>
  <div class="pos-register-layout">
    <!-- Left Panel: Catalog Browser -->
    <div class="pos-catalog-panel">
      <!-- Search and Scanner Header -->
      <div class="pos-search-header premium-card">
        <div class="search-input-group">
          <Search class="search-icon" />
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search catalog by name, SKU..." 
            class="pos-input with-left-icon"
            @input="filterProducts"
          />
        </div>
        
        <div class="barcode-input-group">
          <Barcode class="barcode-icon" />
          <input 
            type="text" 
            v-model="barcodeQuery" 
            placeholder="Scan barcode scan..." 
            class="pos-input with-left-icon"
            @keyup.enter="scanBarcode"
          />
        </div>
      </div>

      <!-- Horizontal Categories Pills -->
      <div class="categories-container">
        <button 
          class="category-pill"
          :class="{ active: selectedCategoryId === null }"
          @click="selectCategory(null)"
        >
          All Products
        </button>
        <button 
          v-for="cat in productsStore.categories" 
          :key="cat.id"
          class="category-pill"
          :class="{ active: selectedCategoryId === cat.id }"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
      </div>

      <!-- Dynamic Product Grid -->
      <div class="catalog-grid-wrapper">
        <div class="product-grid" v-if="!loading && filteredProducts.length">
          <ProductCard 
            v-for="prod in filteredProducts" 
            :key="prod.id"
            :name="prod.name"
            :sku="prod.sku"
            :price="prod.price"
            :stock="prod.stock_quantity"
            :uom="prod.uom"
            @add="addToCart(prod)"
          />
        </div>
        
        <div class="loading-state" v-else-if="loading">
          <div class="spinner"></div>
          <p>Syncing product list...</p>
        </div>

        <div class="empty-state" v-else>
          <Package class="empty-state-icon" />
          <p>No products match your active search filters.</p>
        </div>
      </div>
    </div>

    <!-- Right Panel: Transaction Console -->
    <div class="pos-transaction-panel premium-card">
      <div class="transaction-header">
        <div class="header-title-group">
          <h3>Current Cart</h3>
          <span class="items-count-badge">{{ cartStore.items.length }} Items</span>
        </div>
        <button 
          class="clear-cart-btn" 
          @click="cartStore.clearCart" 
          :disabled="!cartStore.itemsCount"
        >
          <Trash2 class="clear-icon" />
          Clear Cart
        </button>
      </div>

      <!-- Customer Loyalty Section -->
      <div class="customer-dock">
        <div class="customer-info-row" v-if="cartStore.selectedCustomer">
          <div class="customer-avatar-box">
            <UserCheck class="customer-avatar-icon" />
          </div>
          <div class="customer-meta-text">
            <span class="customer-name">{{ cartStore.selectedCustomer.name }}</span>
            <span class="customer-points">{{ cartStore.selectedCustomer.loyalty_points }} Loyalty Points</span>
          </div>
          <button class="detach-customer-btn" @click="cartStore.selectCustomer(null)">
            <X class="detach-icon" />
          </button>
        </div>
        
        <button class="attach-customer-btn" v-else @click="showCustomerModal = true">
          <UserPlus class="attach-icon" />
          Attach Customer to Order
        </button>
      </div>

      <!-- Transaction Line Items -->
      <div class="cart-items-scroller">
        <div v-if="cartStore.items.length">
          <TransactionItem 
            v-for="item in cartStore.items" 
            :key="item.product_id"
            :name="item.name"
            :sku="item.sku"
            :price="item.price"
            :quantity="item.quantity"
            :uom="item.uom"
            @increase="cartStore.updateQuantity(item.product_id, item.quantity + (item.uom && item.uom !== 'pieces' ? 0.1 : 1))"
            @decrease="cartStore.updateQuantity(item.product_id, item.quantity - (item.uom && item.uom !== 'pieces' ? 0.1 : 1))"
                        @remove="cartStore.removeFromCart(item.product_id)"
          />
        </div>
        
        <div class="cart-empty-state" v-else>
          <ShoppingCart class="empty-cart-icon" />
          <p>Scanning registry empty. Add items to begin.</p>
        </div>
      </div>

      <!-- Applied Discount Pill Bar -->
      <div class="promo-feedback-bar" v-if="cartStore.appliedDiscount">
        <div class="applied-coupon-badge">
          <Tag class="coupon-icon" />
          <span>{{ cartStore.appliedDiscount.code }} ({{ cartStore.appliedDiscount.discount_type === 'percent' ? cartStore.appliedDiscount.value + '%' : '$' + cartStore.appliedDiscount.value }})</span>
          <button @click="handleRemovePromo" class="remove-coupon-action">&times;</button>
        </div>
      </div>

      <!-- Transaction Calculators -->
      <div class="transaction-summary-card">
        <div class="summary-line">
          <span class="line-label">Subtotal</span>
          <span class="line-val">${{ cartStore.subtotal.toFixed(2) }}</span>
        </div>
        
        <div class="summary-line inline-discount">
          <span class="line-label">Direct Discount ($)</span>
          <input 
            type="number" 
            v-model="discountInput" 
            class="pos-input discount-line-input"
            @input="updateDiscount"
            min="0"
            :max="cartStore.subtotal"
            step="0.01"
          />
        </div>

        <div class="summary-line promo-code-line">
          <span class="line-label">Promo Code</span>
          <div class="promo-inline-group">
            <input 
              type="text" 
              v-model="promoCode" 
              placeholder="Code" 
              class="pos-input promo-inline-input"
              :disabled="cartStore.loading"
              @keyup.enter="handleApplyPromo"
            />
            <button 
              type="button" 
              @click="handleApplyPromo" 
              class="pos-btn pos-btn-accent promo-inline-btn"
              :disabled="cartStore.loading || !promoCode.trim()"
            >
              Apply
            </button>
          </div>
        </div>

        <div v-if="promoError" class="promo-error-badge">
          <span>{{ promoError }}</span>
        </div>

        <div class="summary-line">
          <span class="line-label">Tax (8.25%)</span>
          <span class="line-val">${{ cartStore.taxAmount.toFixed(2) }}</span>
        </div>

        <div class="divider-line"></div>

        <div class="summary-line total-line">
          <span class="total-label">Total</span>
          <span class="total-val">${{ cartStore.total.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Checkout & Payment Method -->
      <div class="payment-setup">
        <span class="payment-setup-title">Select Payment Method</span>
        <PaymentSelector v-model="paymentMethod" />
        
        <button 
          class="checkout-trigger-btn"
          :disabled="!cartStore.itemsCount"
          @click="openCheckoutModal"
        >
          Complete Sale
        </button>
      </div>

      <!-- Offline Queue Mini-Widget -->
      <div class="offline-queue-widget" v-if="cartStore.offlineSalesQueue.length > 0">
        <div class="widget-row">
          <span class="widget-title">Queued Offline Orders</span>
          <span class="widget-count">{{ cartStore.offlineSalesQueue.length }} Unsynced</span>
        </div>
        <p class="widget-desc">Transactions will sync automatically once network returns.</p>
      </div>
    </div>

    <!-- Modal: Checkout Payment Finalizer -->
    <div class="modal-overlay" v-if="showCheckoutModal">
      <div class="checkout-finalize-modal premium-card">
        <h3>Finalize Registry Checkout</h3>
        
        <div class="finalize-summary">
          <div class="finalize-row">
            <span>Payment Method</span>
            <span class="method-tag">{{ paymentMethod.toUpperCase() }}</span>
          </div>
          <div class="finalize-row total">
            <span>Total Due</span>
            <span class="total-bold">${{ cartStore.total.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Cash Calculator -->
        <div class="cash-calc-pane" v-if="paymentMethod === 'cash'">
          <label class="calc-label">Cash Received From Customer</label>
          <input 
            type="number" 
            v-model="cashReceived" 
            class="pos-input cash-received-input"
            step="0.01"
            min="0"
          />
          <div class="change-calc-row">
            <span>Expected Change:</span>
            <span class="change-value" :class="{ negative: cashChange < 0 }">
              ${{ cashChange.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="finalize-actions">
          <button class="pos-btn pos-btn-secondary" @click="showCheckoutModal = false">Cancel</button>
          <button 
            class="pos-btn pos-btn-accent finalize-submit-btn" 
            :disabled="paymentMethod === 'cash' && cashChange < 0"
            @click="submitPayment"
          >
            Confirm & Print
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Customer Search & Add -->
    <div class="modal-overlay" v-if="showCustomerModal">
      <div class="customer-search-modal premium-card">
        <div class="modal-header">
          <h3>Loyalty Accounts</h3>
          <button class="modal-close-x" @click="showCustomerModal = false">&times;</button>
        </div>
        
        <div class="search-search-box">
          <input 
            type="text" 
            v-model="customerPhoneQuery" 
            placeholder="Search by phone number..." 
            class="pos-input"
            @input="lookupCustomer"
          />
        </div>

        <div class="customer-results-box" v-if="lookupResults.length">
          <div 
            v-for="c in lookupResults" 
            :key="c.id" 
            class="search-customer-row" 
            @click="attachCustomer(c)"
          >
            <div>
              <span class="search-cust-name">{{ c.name }}</span>
              <span class="search-cust-phone">{{ c.phone }}</span>
            </div>
            <span class="search-cust-points">{{ c.loyalty_points }} PTS</span>
          </div>
        </div>

        <div class="register-customer-pane">
          <h4>Register New Loyalty Customer</h4>
          <div class="pane-inputs">
            <input type="text" v-model="newCustomer.name" placeholder="Full Name" class="pos-input" />
            <input type="text" v-model="newCustomer.phone" placeholder="Phone Number" class="pos-input" />
            <input type="email" v-model="newCustomer.email" placeholder="Email Address" class="pos-input" />
          </div>
          <button class="pos-btn pos-btn-accent register-cust-submit" @click="createNewCustomer">
            Register Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '@/store/products'
import { useCartStore } from '@/store/cart'
import ProductCard from '@/components/ProductCard.vue'
import TransactionItem from '@/components/TransactionItem.vue'
import PaymentSelector from '@/components/PaymentSelector.vue'
import axios from 'axios'
import { Search, Barcode, Trash2, UserPlus, UserCheck, X, ShoppingCart, Tag, Package } from 'lucide-vue-next'

const productsStore = useProductsStore()
const cartStore = useCartStore()

const loading = ref(false)
const searchQuery = ref('')
const barcodeQuery = ref('')
const discountInput = ref(0)
const promoCode = ref('')
const promoError = ref('')

// Modal states
const showCheckoutModal = ref(false)
const showCustomerModal = ref(false)
const showSuspendedModal = ref(false)

// Checkout values
const paymentMethod = ref('cash')
const cashReceived = ref(0)

// Customer values
const customerPhoneQuery = ref('')
const lookupResults = ref([])
const newCustomer = ref({ name: '', phone: '', email: '' })

const filteredProducts = ref([])
const selectedCategoryId = ref(null)

const filterProducts = () => {
  let list = productsStore.products
  if (selectedCategoryId.value !== null) {
    list = list.filter(p => p.category_id === selectedCategoryId.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p => 
      p.name.toLowerCase().includes(q) || 
      p.sku.toLowerCase().includes(q)
    )
  }
  filteredProducts.value = list
}

const selectCategory = (catId) => {
  selectedCategoryId.value = catId
  filterProducts()
}

const addToCart = (product) => {
  if (product.stock_quantity <= 0) return
  cartStore.addToCart(product)
}

const scanBarcode = async () => {
  if (!barcodeQuery.value) return
  const prod = await productsStore.searchByBarcode(barcodeQuery.value)
  if (prod) {
    addToCart(prod)
    barcodeQuery.value = ''
  } else {
    alert('Product with barcode not found')
  }
}

const updateDiscount = () => {
  cartStore.setDiscount(discountInput.value)
}

const handleApplyPromo = async () => {
  promoError.value = ''
  if (!promoCode.value.trim()) return
  
  const discountObj = await cartStore.applyDiscountCode(promoCode.value)
  if (discountObj) {
    discountInput.value = cartStore.discount
    promoCode.value = ''
  } else {
    promoError.value = cartStore.error || 'Invalid discount code'
  }
}

const handleRemovePromo = () => {
  cartStore.setDiscount(0)
  discountInput.value = 0
  promoCode.value = ''
  promoError.value = ''
}

// Checkout Modal Actions
const openCheckoutModal = () => {
  paymentMethod.value = 'cash'
  cashReceived.value = cartStore.total
  showCheckoutModal.value = true
}

const cashChange = computed(() => {
  if (paymentMethod.value !== 'cash') return 0
  return parseFloat(cashReceived.value || 0) - cartStore.total
})

const submitPayment = async () => {
  const sale = await cartStore.checkout(paymentMethod.value)
  if (sale) {
    alert(`Checkout Completed! Invoice: ${sale.invoice_number}`)
    showCheckoutModal.value = false
    discountInput.value = 0
    promoCode.value = ''
    promoError.value = ''
    await productsStore.fetchProducts({}, true) // refresh stock levels
    filterProducts()
  } else {
    alert('Checkout failed: ' + cartStore.error)
  }
}

// Customer Lookup
const lookupCustomer = async () => {
  if (customerPhoneQuery.value.length < 3) return
  try {
    const response = await axios.get(`/api/sales/customers?phone=${customerPhoneQuery.value}`)
    if (response.data && response.data.id) {
      lookupResults.value = [response.data]
    } else {
      lookupResults.value = []
    }
  } catch (err) {
    lookupResults.value = []
  }
}

const attachCustomer = (customer) => {
  cartStore.selectCustomer(customer)
  showCustomerModal.value = false
  customerPhoneQuery.value = ''
  lookupResults.value = []
}

const createNewCustomer = async () => {
  if (!newCustomer.value.name || !newCustomer.value.phone) {
    alert('Name and Phone required')
    return
  }
  try {
    const response = await axios.post('/api/sales/customers', newCustomer.value)
    attachCustomer(response.data)
    newCustomer.value = { name: '', phone: '', email: '' }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to register customer')
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    productsStore.fetchProducts(),
    productsStore.fetchCategories()
  ])
  filterProducts()
  loading.value = false
})
</script>

<style scoped>
.pos-register-layout {
  display: flex;
  gap: 24px;
  height: calc(100vh - 120px);
}

@media (max-width: 1024px) {
  .pos-register-layout {
    flex-direction: column;
    height: auto;
  }
}

/* Left panel: Catalog */
.pos-catalog-panel {
  flex: 1.7;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.pos-search-header {
  display: flex;
  gap: 16px;
  padding: 16px !important;
}

.search-input-group, .barcode-input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-group {
  flex: 1.8;
}

.barcode-input-group {
  flex: 1;
}

.search-icon, .barcode-icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.pos-input.with-left-icon {
  padding-left: 44px;
}

/* Categories container */
.categories-container {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.category-pill {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.category-pill:hover {
  background-color: #f9fafb;
  border-color: var(--text-muted);
}

.category-pill.active {
  background-color: var(--bg-sidebar);
  color: #ffffff;
  border-color: var(--bg-sidebar);
}

.catalog-grid-wrapper {
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

/* Right Panel: Transaction */
.pos-transaction-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px !important;
  gap: 16px;
  overflow-y: auto;
  max-width: 440px;
  min-width: 360px;
}

@media (max-width: 1024px) {
  .pos-transaction-panel {
    max-width: 100%;
    min-width: 100%;
  }
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title-group h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.items-count-badge {
  background-color: #f3f4f6;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

.clear-cart-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color var(--transition-fast);
}

.clear-cart-btn:hover:not(:disabled) {
  color: var(--accent-danger);
}

.clear-cart-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-icon {
  width: 14px;
  height: 14px;
}

/* Customer Dock */
.customer-dock {
  background-color: #f9fafb;
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px;
}

.attach-customer-btn {
  width: 100%;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}

.attach-customer-btn:hover {
  color: var(--text-primary);
}

.attach-icon, .customer-avatar-icon {
  width: 16px;
  height: 16px;
}

.customer-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.customer-avatar-box {
  width: 32px;
  height: 32px;
  background-color: rgba(184, 241, 90, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #557c11;
}

.customer-meta-text {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.customer-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
}

.customer-points {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.detach-customer-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
}

.detach-customer-btn:hover {
  color: var(--accent-danger);
}

.detach-icon {
  width: 14px;
  height: 14px;
}

/* Cart Items Scroller */
.cart-items-scroller {
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 2px;
  min-height: 150px;
}

.cart-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--text-muted);
  gap: 8px;
  height: 100%;
}

.empty-cart-icon {
  width: 32px;
  height: 32px;
  stroke-width: 1.5px;
}

.promo-feedback-bar {
  display: flex;
}

.applied-coupon-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: rgba(184, 241, 90, 0.15);
  color: #557c11;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.coupon-icon {
  width: 12px;
  height: 12px;
}

.remove-coupon-action {
  background: none;
  border: none;
  font-size: 0.95rem;
  cursor: pointer;
  color: inherit;
  font-weight: 700;
  line-height: 1;
  display: flex;
  align-items: center;
}

/* Summary Card */
.transaction-summary-card {
  background-color: #f9fafb;
  border-radius: var(--radius-md);
  padding: 16px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.line-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.line-val {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
}

.discount-line-input {
  width: 90px;
  padding: 4px 8px;
  text-align: right;
  font-size: 0.82rem;
  font-weight: 700;
}

.promo-inline-group {
  display: flex;
  gap: 4px;
}

.promo-inline-input {
  width: 90px;
  padding: 4px 8px;
  font-size: 0.82rem;
}

.promo-inline-btn {
  padding: 4px 10px;
  font-size: 0.75rem;
  border-radius: var(--radius-sm);
}

.promo-error-badge {
  background-color: rgba(255, 94, 94, 0.05);
  border: 1px solid rgba(255, 94, 94, 0.2);
  color: var(--accent-danger);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  text-align: right;
}

.divider-line {
  height: 1px;
  background-color: var(--border-color);
}

.total-line {
  margin-top: 4px;
}

.total-label {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
}

.total-val {
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--text-primary);
}

/* Payment setup and trigger */
.payment-setup {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-setup-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.checkout-trigger-btn {
  width: 100%;
  height: 56px;
  border-radius: var(--radius-md);
  background-color: var(--accent-lime);
  color: var(--accent-lime-text);
  border: none;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 14px rgba(184, 241, 90, 0.2);
}

.checkout-trigger-btn:hover:not(:disabled) {
  background-color: var(--accent-lime-hover);
  transform: translateY(-1px);
}

.checkout-trigger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.offline-queue-widget {
  background-color: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.widget-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  font-weight: 700;
}

.widget-title {
  color: var(--text-secondary);
}

.widget-count {
  color: var(--accent-warning);
}

.widget-desc {
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Modals overlays styling */
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

.checkout-finalize-modal, .customer-search-modal {
  width: 440px;
  max-width: 90%;
  padding: 32px !important;
  animation: modalFade 0.25s ease-out;
}

@keyframes modalFade {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.checkout-finalize-modal h3, .customer-search-modal h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.finalize-summary {
  background-color: #f9fafb;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.finalize-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.finalize-row.total {
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
  margin-top: 4px;
}

.method-tag {
  background-color: #ffffff;
  border: 1px solid var(--border-color);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
}

.total-bold {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
}

.cash-calc-pane {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.calc-label {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.cash-received-input {
  font-size: 1.2rem;
  font-weight: 700;
  text-align: center;
}

.change-calc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-weight: 700;
  font-size: 0.95rem;
}

.change-value {
  font-size: 1.2rem;
  color: var(--accent-success);
}

.change-value.negative {
  color: var(--accent-danger);
}

.finalize-actions {
  display: flex;
  gap: 12px;
}

.finalize-actions button {
  flex: 1;
}

.finalize-submit-btn {
  background-color: var(--accent-lime);
  color: var(--accent-lime-text);
  font-weight: 700;
}

/* Customer loyalty search modal */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-close-x {
  background: none;
  border: none;
  font-size: 1.45rem;
  cursor: pointer;
  color: var(--text-muted);
}

.modal-close-x:hover {
  color: var(--text-primary);
}

.search-search-box {
  margin-bottom: 16px;
}

.customer-results-box {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  max-height: 180px;
  overflow-y: auto;
  margin-bottom: 20px;
  background-color: #f9fafb;
}

.search-customer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.search-customer-row:hover {
  background-color: #f3f4f6;
}

.search-cust-name {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary);
}

.search-cust-phone {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.search-cust-points {
  font-size: 0.78rem;
  font-weight: 700;
  color: #557c11;
  background-color: rgba(184, 241, 90, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
}

.register-customer-pane {
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.register-customer-pane h4 {
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.pane-inputs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.register-cust-submit {
  width: 100%;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-lime-hover);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}
</style>
