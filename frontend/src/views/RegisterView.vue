<template>
  <div class="register-layout">
    <!-- Left Column: Products -->
    <section class="products-panel">
      <!-- Search & Barcode Scan -->
      <div class="search-bar">
        <div class="input-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search products by name or SKU..." 
            class="pos-input"
            @input="filterProducts"
          />
        </div>
        <div class="input-wrapper barcode-wrapper">
          <span class="barcode-icon">║▌</span>
          <input 
            type="text" 
            v-model="barcodeQuery" 
            placeholder="Scan barcode..." 
            class="pos-input"
            @keyup.enter="scanBarcode"
          />
        </div>
      </div>

      <!-- Categories Tabs -->
      <div class="categories-tabs">
        <button 
          class="tab" 
          :class="{ active: selectedCategoryId === null }"
          @click="selectCategory(null)"
        >
          All Items
        </button>
        <button 
          v-for="cat in productsStore.categories" 
          :key="cat.id"
          class="tab"
          :class="{ active: selectedCategoryId === cat.id }"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
      </div>

      <!-- Product Grid -->
      <div class="product-grid" v-if="!loading">
        <div 
          v-for="prod in filteredProducts" 
          :key="prod.id"
          class="product-card"
          :class="{ 'out-of-stock': prod.stock_quantity <= 0 }"
          @click="addToCart(prod)"
        >
          <div class="prod-badge" :class="prod.stock_quantity > 5 ? 'in' : 'low'" v-if="prod.stock_quantity > 0">
            {{ prod.stock_quantity }} {{ prod.uom }}
          </div>
          <div class="prod-badge out" v-else>OUT</div>
          
          <div class="prod-details">
            <h4 class="prod-name">{{ prod.name }}</h4>
            <span class="prod-sku">{{ prod.sku }}</span>
            <div class="prod-footer">
              <span class="prod-price">${{ prod.price.toFixed(2) }}</span>
              <span class="add-indicator">+</span>
            </div>
          </div>
        </div>
        
        <div class="empty-state" v-if="filteredProducts.length === 0">
          <p>No products found matching filters.</p>
        </div>
      </div>
      
      <div class="loading-state" v-else>
        <div class="spinner"></div>
      </div>
    </section>

    <!-- Right Column: Cart Panel -->
    <aside class="cart-panel pos-card">
      <div class="cart-header">
        <h3>Current Cart</h3>
        <button class="clear-btn" @click="cartStore.clearCart" :disabled="!cartStore.itemsCount">
          Clear
        </button>
      </div>

      <!-- Customer Selector -->
      <div class="customer-selector">
        <div class="customer-row" v-if="cartStore.selectedCustomer">
          <div class="customer-info">
            <span class="name">{{ cartStore.selectedCustomer.name }}</span>
            <span class="pts">{{ cartStore.selectedCustomer.loyalty_points }} pts</span>
          </div>
          <button class="remove-cust" @click="cartStore.selectCustomer(null)">✕</button>
        </div>
        <div class="customer-row select-trigger" v-else @click="showCustomerModal = true">
          <span class="trigger-text">👤 Attach Customer to Order</span>
        </div>
      </div>

      <!-- Cart Items List -->
      <div class="cart-items">
        <div v-for="item in cartStore.items" :key="item.product_id" class="cart-item">
          <div class="item-left">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-price">${{ item.price.toFixed(2) }}</span>
          </div>
          
          <div class="item-right">
            <div class="qty-controls">
              <button class="qty-btn" @click="cartStore.updateQuantity(item.product_id, item.quantity - (item.uom && item.uom !== 'pieces' ? 0.1 : 1))">-</button>
              <input 
                type="number" 
                :value="item.quantity" 
                @input="e => cartStore.updateQuantity(item.product_id, e.target.value)"
                class="qty-input"
                :step="item.uom && item.uom !== 'pieces' ? '0.001' : '1'"
                min="0.001"
              />
              <span class="qty-uom-label">{{ item.uom }}</span>
              <button class="qty-btn" @click="cartStore.updateQuantity(item.product_id, item.quantity + (item.uom && item.uom !== 'pieces' ? 0.1 : 1))">+</button>
            </div>
            <span class="item-total">${{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="cart-empty" v-if="cartStore.items.length === 0">
          <span class="cart-icon">🛒</span>
          <p>Cart is currently empty</p>
        </div>
      </div>

      <!-- Cart Calculations -->
      <div class="cart-summary">
        <div class="summary-row">
          <span>Subtotal</span>
          <span>${{ cartStore.subtotal.toFixed(2) }}</span>
        </div>
        <div class="summary-row">
          <span>Discount ($)</span>
          <input 
            type="number" 
            v-model="discountInput" 
            class="discount-input"
            @input="updateDiscount"
            min="0"
            :max="cartStore.subtotal"
            step="0.01"
          />
        </div>

        <div class="promo-code-container">
          <div class="summary-row promo-row">
            <span>Promo Code</span>
            <div class="promo-input-group">
              <input 
                type="text" 
                v-model="promoCode" 
                placeholder="Enter code" 
                class="promo-input"
                :disabled="cartStore.loading"
                @keyup.enter="handleApplyPromo"
              />
              <button 
                type="button" 
                @click="handleApplyPromo" 
                class="promo-btn"
                :disabled="cartStore.loading || !promoCode.trim()"
              >
                Apply
              </button>
            </div>
          </div>
          <div v-if="cartStore.appliedDiscount" class="applied-discount-info">
            <span class="discount-badge">
              🏷️ {{ cartStore.appliedDiscount.code }} 
              ({{ cartStore.appliedDiscount.discount_type === 'percent' ? cartStore.appliedDiscount.value + '%' : '$' + cartStore.appliedDiscount.value }})
              <button @click="handleRemovePromo" class="remove-promo-btn" title="Remove promo">&times;</button>
            </span>
          </div>
          <div v-if="promoError" class="promo-error-text">
            {{ promoError }}
          </div>
        </div>
        <div class="summary-row">
          <span>Tax (8.25%)</span>
          <span>${{ cartStore.taxAmount.toFixed(2) }}</span>
        </div>
        <div class="summary-row total-row">
          <span>Total</span>
          <span>${{ cartStore.total.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Suspended Carts Drawer and Action Area -->
      <div class="cart-actions">
        <button 
          class="pos-btn pos-btn-secondary flex-grow" 
          @click="suspendCurrentCart"
          :disabled="!cartStore.itemsCount"
        >
          Hold Order
        </button>
        <button 
          class="pos-btn pos-btn-secondary" 
          @click="openSuspensionModal"
        >
          Recall
        </button>
      </div>

      <button 
        class="pos-btn pos-btn-success checkout-btn" 
        :disabled="!cartStore.itemsCount"
        @click="openCheckoutModal"
      >
        PROCEED TO PAY
      </button>
    </aside>

    <!-- Modal: Checkout Payment -->
    <div class="modal-overlay" v-if="showCheckoutModal">
      <div class="modal-content pos-card">
        <h3>Finalize Payment</h3>
        <p class="invoice-amount">Total Due: <strong>${{ cartStore.total.toFixed(2) }}</strong></p>

        <div class="payment-methods">
          <button 
            class="method-btn" 
            :class="{ active: paymentMethod === 'cash' }"
            @click="selectPaymentMethod('cash')"
          >
            💵 Cash
          </button>
          <button 
            class="method-btn" 
            :class="{ active: paymentMethod === 'card' }"
            @click="selectPaymentMethod('card')"
          >
            💳 Card
          </button>
          <button 
            class="method-btn" 
            :class="{ active: paymentMethod === 'mobile_pay' }"
            @click="selectPaymentMethod('mobile_pay')"
          >
            📱 Mobile Pay
          </button>
        </div>

        <!-- Cash Details -->
        <div class="cash-calculator" v-if="paymentMethod === 'cash'">
          <label>Cash Received</label>
          <input 
            type="number" 
            v-model="cashReceived" 
            class="pos-input cash-input"
            step="0.01"
            min="0"
          />
          <div class="change-display">
            <span>Change:</span>
            <span class="change-amount" :class="{ negative: cashChange < 0 }">
              ${{ cashChange.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="modal-actions">
          <button class="pos-btn pos-btn-secondary" @click="showCheckoutModal = false">Cancel</button>
          <button 
            class="pos-btn pos-btn-success" 
            :disabled="paymentMethod === 'cash' && cashChange < 0"
            @click="submitPayment"
          >
            Confirm Payment
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Customer Selector -->
    <div class="modal-overlay" v-if="showCustomerModal">
      <div class="modal-content pos-card customer-modal">
        <div class="modal-header">
          <h3>Search Customer</h3>
          <button class="close-btn" @click="showCustomerModal = false">✕</button>
        </div>
        
        <input 
          type="text" 
          v-model="customerPhoneQuery" 
          placeholder="Look up phone number..." 
          class="pos-input"
          @input="lookupCustomer"
        />

        <div class="customer-results" v-if="lookupResults.length">
          <div 
            v-for="c in lookupResults" 
            :key="c.id" 
            class="customer-item" 
            @click="attachCustomer(c)"
          >
            <div class="c-info">
              <span class="c-name">{{ c.name }}</span>
              <span class="c-phone">{{ c.phone }}</span>
            </div>
            <span class="c-points">{{ c.loyalty_points }} pts</span>
          </div>
        </div>

        <div class="new-customer-form">
          <h4>Or Add New Customer</h4>
          <input type="text" v-model="newCustomer.name" placeholder="Full Name" class="pos-input" />
          <input type="text" v-model="newCustomer.phone" placeholder="Phone Number" class="pos-input" />
          <input type="email" v-model="newCustomer.email" placeholder="Email Address" class="pos-input" />
          <button class="pos-btn pos-btn-primary" @click="createNewCustomer">Register & Attach</button>
        </div>
      </div>
    </div>

    <!-- Modal: Suspended Carts Recall -->
    <div class="modal-overlay" v-if="showSuspendedModal">
      <div class="modal-content pos-card suspension-modal">
        <div class="modal-header">
          <h3>Suspended Transactions</h3>
          <button class="close-btn" @click="showSuspendedModal = false">✕</button>
        </div>
        
        <div class="suspension-list" v-if="Object.keys(suspendedCarts).length">
          <div 
            v-for="(cart, cid) in suspendedCarts" 
            :key="cid" 
            class="suspension-item"
          >
            <div class="s-info">
              <span class="s-id">Hold ID: {{ cid }}</span>
              <span class="s-summary">{{ cart.items.length }} items • Total: ${{ getCartTotal(cart).toFixed(2) }}</span>
            </div>
            <div class="s-actions">
              <button class="pos-btn pos-btn-success sm-btn" @click="resumeSuspendedCart(cid, cart)">Resume</button>
              <button class="pos-btn pos-btn-danger sm-btn" @click="discardSuspendedCart(cid)">Delete</button>
            </div>
          </div>
        </div>
        <p class="empty-text" v-else>No suspended orders currently stored in cache.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '@/store/products'
import { useCartStore } from '@/store/cart'
import axios from 'axios'

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

// Suspended carts values
const suspendedCarts = ref({})

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

const selectPaymentMethod = (method) => {
  paymentMethod.value = method
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
    await productsStore.fetchProducts() // refresh stock levels
    filterProducts()
  } else {
    alert('Checkout failed: ' + cartStore.error)
  }
}

// Suspension Logic
const suspendCurrentCart = async () => {
  const cartId = 'sus-' + Date.now()
  const ok = await cartStore.suspendCart(cartId)
  if (ok) {
    alert('Cart suspended successfully')
    discountInput.value = 0
    promoCode.value = ''
    promoError.value = ''
  }
}

const openSuspensionModal = async () => {
  try {
    const response = await axios.get('/api/sales/suspend')
    suspendedCarts.value = response.data
    showSuspendedModal.value = true
  } catch (err) {
    console.error('Failed to get suspended carts', err)
  }
}

const resumeSuspendedCart = (cid, cart) => {
  cartStore.clearCart()
  cartStore.items = cart.items
  cartStore.discount = cart.discount
  discountInput.value = cart.discount
  cartStore.selectedCustomer = cart.selectedCustomer
  
  // delete suspend cart from cache
  axios.delete(`/api/sales/suspend/${cid}`)
  showSuspendedModal.value = false
}

const discardSuspendedCart = async (cid) => {
  if (confirm('Discard this suspended order?')) {
    await axios.delete(`/api/sales/suspend/${cid}`)
    delete suspendedCarts.value[cid]
  }
}

const getCartTotal = (cart) => {
  const sub = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  const taxable = Math.max(0, sub - cart.discount)
  return taxable + (taxable * 0.0825)
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
.register-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  height: calc(100vh - 120px);
}

@media (max-width: 1024px) {
  .register-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}

.products-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.search-bar {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.input-wrapper {
  position: relative;
}

.search-icon, .barcode-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.pos-input {
  padding-left: 40px;
}

.categories-tabs {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.tab {
  padding: 8px 16px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  white-space: nowrap;
  font-family: inherit;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.tab:hover {
  background-color: var(--bg-tertiary);
  color: #fff;
}

.tab.active {
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #fff;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 16px;
  overflow-y: auto;
  padding-right: 4px;
  flex-grow: 1;
}

.product-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  cursor: pointer;
  position: relative;
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.product-card:hover:not(.out-of-stock) {
  transform: translateY(-4px);
  border-color: var(--accent-primary);
}

.product-card.out-of-stock {
  opacity: 0.5;
  cursor: not-allowed;
}

.prod-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.prod-badge.in { background-color: rgba(16, 185, 129, 0.15); color: #34d399; }
.prod-badge.low { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.prod-badge.out { background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; }

.prod-details {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  height: calc(100% - 16px);
  justify-content: space-between;
}

.prod-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
}

.prod-sku {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.prod-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.prod-price {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent-success);
}

.add-indicator {
  width: 22px;
  height: 22px;
  background-color: var(--bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-weight: bold;
  font-size: 0.85rem;
}

.product-card:hover .add-indicator {
  background-color: var(--accent-primary);
  color: #fff;
}

.cart-panel {
  display: flex;
  flex-direction: column;
  padding: 20px;
  height: 100%;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.clear-btn {
  background: transparent;
  border: none;
  color: var(--accent-danger);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
}
.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.customer-selector {
  margin-bottom: 20px;
}

.customer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.select-trigger {
  cursor: pointer;
  color: var(--text-secondary);
  justify-content: center;
}
.select-trigger:hover {
  background-color: var(--border-color);
  color: #fff;
}

.customer-info {
  display: flex;
  flex-direction: column;
}
.customer-info .name { font-weight: 600; color: #fff; }
.customer-info .pts { font-size: 0.75rem; color: var(--accent-warning); }

.remove-cust {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}
.remove-cust:hover { color: #fff; }

.cart-items {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.item-left {
  display: flex;
  flex-direction: column;
}
.item-name { font-size: 0.9rem; font-weight: 600; color: #fff; }
.item-price { font-size: 0.8rem; color: var(--text-muted); }

.item-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.qty-controls {
  display: flex;
  align-items: center;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.qty-btn {
  background: transparent;
  border: none;
  width: 24px;
  height: 24px;
  color: var(--text-primary);
  font-weight: bold;
  cursor: pointer;
}
.qty-btn:hover { background-color: var(--border-color); }

.qty-val {
  padding: 0 8px;
  font-size: 0.85rem;
  font-weight: 600;
}

.item-total {
  font-size: 0.95rem;
  font-weight: 700;
  width: 60px;
  text-align: right;
}

.cart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: var(--text-muted);
}
.cart-empty .cart-icon { font-size: 2.5rem; margin-bottom: 12px; }

.cart-summary {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.discount-input {
  width: 70px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: #fff;
  text-align: right;
  padding: 2px 6px;
  font-family: inherit;
}

.promo-code-container {
  margin-top: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.promo-row {
  align-items: center !important;
}

.promo-input-group {
  display: flex;
  gap: 8px;
}

.promo-input {
  width: 110px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: #fff;
  padding: 4px 8px;
  font-size: 0.85rem;
  text-transform: uppercase;
  font-family: inherit;
}

.promo-input::placeholder {
  color: var(--text-muted);
  text-transform: none;
}

.promo-btn {
  background-color: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 4px 10px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.promo-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.promo-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.applied-discount-info {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.discount-badge {
  background-color: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remove-promo-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.promo-error-text {
  color: var(--accent-danger);
  font-size: 0.75rem;
  text-align: right;
  margin-top: 4px;
}

.total-row {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  padding-top: 10px;
  border-top: 1px dashed var(--border-color);
}

.cart-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
.flex-grow { flex-grow: 1; }

.checkout-btn {
  margin-top: 16px;
  width: 100%;
  padding: 14px;
  font-size: 1.05rem;
  font-weight: 700;
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

.modal-content {
  width: 440px;
  max-width: 90%;
  padding: 24px;
}

.modal-content h3 { font-size: 1.25rem; margin-bottom: 16px; color: #fff; }

.invoice-amount {
  font-size: 1.1rem;
  margin-bottom: 24px;
}

.payment-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.method-btn {
  padding: 16px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-fast);
}
.method-btn.active {
  border-color: var(--accent-primary);
  background-color: rgba(79, 70, 229, 0.15);
  color: #fff;
}

.cash-calculator {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.cash-input {
  font-size: 1.25rem;
  text-align: right;
  padding: 12px;
}

.change-display {
  display: flex;
  justify-content: space-between;
  font-size: 1.1rem;
}
.change-amount { font-weight: 700; color: var(--accent-success); }
.change-amount.negative { color: var(--accent-danger); }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Customer Modal Custom styling */
.customer-modal {
  width: 480px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.close-btn {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: var(--text-muted);
  cursor: pointer;
}

.customer-results {
  margin-top: 12px;
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-secondary);
}

.customer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
}
.customer-item:hover { background-color: var(--bg-tertiary); }
.c-info { display: flex; flex-direction: column; }
.c-name { font-weight: 600; color: #fff; }
.c-phone { font-size: 0.8rem; color: var(--text-muted); }
.c-points { font-size: 0.85rem; color: var(--accent-warning); font-weight: bold; }

.new-customer-form {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Suspension list modal customization */
.suspension-modal {
  width: 500px;
}
.suspension-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}
.suspension-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}
.s-info { display: flex; flex-direction: column; gap: 4px; }
.s-id { font-weight: 600; color: #fff; font-size: 0.9rem; }
.s-summary { font-size: 0.8rem; color: var(--text-muted); }
.s-actions { display: flex; gap: 8px; }
.sm-btn { padding: 6px 12px; font-size: 0.8rem; }
.empty-text { text-align: center; color: var(--text-muted); padding: 20px 0; }

.qty-input {
  width: 65px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: #fff;
  text-align: center;
  padding: 4px 6px;
  font-family: inherit;
  font-size: 0.9rem;
}

.qty-input::-webkit-outer-spin-button,
.qty-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.qty-uom-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  margin-left: 2px;
  margin-right: 2px;
  min-width: 20px;
  text-align: center;
}
</style>
