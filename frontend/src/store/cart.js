import { defineStore } from 'pinia'
import axios from 'axios'
import { useProductsStore } from './products'
import { dbGetAll, dbPut, dbDelete, dbPutAll } from '@/utils/indexedDb'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    discount: 0.00,
    appliedDiscount: null,
    taxRate: 0.0825,
    selectedCustomer: null,
    loading: false,
    error: null,
    isOnline: navigator.onLine,
    offlineSalesQueue: [],
    localDbLoaded: false,
    isSyncing: false
  }),
  getters: {
    subtotal: (state) => {
      return state.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    },
    taxAmount: (state) => {
      const taxable = Math.max(0, state.subtotal - state.discount)
      return taxable * state.taxRate
    },
    total: (state) => {
      const taxable = Math.max(0, state.subtotal - state.discount)
      return taxable + (taxable * state.taxRate)
    },
    itemsCount: (state) => {
      return state.items.reduce((sum, item) => sum + item.quantity, 0)
    }
  },
  actions: {
    calculateDiscountAmount() {
      if (!this.appliedDiscount) {
        return
      }
      const val = parseFloat(this.appliedDiscount.value)
      if (this.appliedDiscount.discount_type === 'percent') {
        this.discount = parseFloat(((this.subtotal * val) / 100).toFixed(2))
      } else {
        this.discount = Math.min(this.subtotal, val)
      }
    },
    addToCart(product) {
      const isContinuous = ['kilograms', 'liters', 'litters', 'pounds', 'ounces'].includes(product.uom?.toLowerCase())
      const initialQty = isContinuous ? 0.25 : 1.00
      
      const existing = this.items.find(item => item.product_id === product.id)
      if (existing) {
        if (existing.quantity < product.stock_quantity) {
          const step = isContinuous ? 0.25 : 1.00
          existing.quantity = parseFloat(Math.min(existing.quantity + step, product.stock_quantity).toFixed(3))
        }
      } else {
        this.items.push({
          product_id: product.id,
          sku: product.sku,
          name: product.name,
          price: product.price,
          quantity: initialQty,
          uom: product.uom || 'pieces',
          stock_available: product.stock_quantity
        })
      }
      this.calculateDiscountAmount()
    },
    removeFromCart(productId) {
      const index = this.items.findIndex(item => item.product_id === productId)
      if (index > -1) {
        this.items.splice(index, 1)
      }
      this.calculateDiscountAmount()
    },
    updateQuantity(productId, qty) {
      const item = this.items.find(item => item.product_id === productId)
      if (item) {
        const parsedQty = parseFloat(qty)
        const isContinuous = ['kilograms', 'liters', 'litters', 'pounds', 'ounces'].includes(item.uom?.toLowerCase())
        const minQty = isContinuous ? 0.25 : 1.00
        
        if (isNaN(parsedQty) || parsedQty < minQty) {
          this.removeFromCart(productId)
        } else {
          item.quantity = parseFloat(Math.min(parsedQty, item.stock_available).toFixed(3))
        }
      }
      this.calculateDiscountAmount()
    },
    setDiscount(discountAmount) {
      this.appliedDiscount = null
      this.discount = Math.max(0, parseFloat(discountAmount) || 0)
    },
    selectCustomer(customer) {
      this.selectedCustomer = customer
    },
    clearCart() {
      this.items = []
      this.discount = 0.00
      this.appliedDiscount = null
      this.selectedCustomer = null
      this.error = null
    },
    async suspendCart(cartId) {
      this.loading = true
      try {
        await axios.post('/api/sales/suspend', {
          cart_id: cartId,
          cart_data: {
            items: this.items,
            discount: this.discount,
            selectedCustomer: this.selectedCustomer
          }
        })
        this.clearCart()
        return true
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to suspend cart'
        return false
      } finally {
        this.loading = false
      }
    },
    async loadFromLocalDb() {
      if (this.localDbLoaded) return
      try {
        this.offlineSalesQueue = await dbGetAll('sales_queue')
        this.localDbLoaded = true
      } catch (err) {
        console.error('Failed to load offline sales queue from IndexedDB', err)
      }
    },
    async checkout(paymentMethod) {
      this.loading = true
      this.error = null
      
      const payload = {
        items: this.items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        })),
        payment_method: paymentMethod,
        customer_id: this.selectedCustomer?.id || null,
        discount: this.discount,
        tax_rate: this.taxRate
      }
      
      // If we are offline, save directly to offline queue
      if (!this.isOnline) {
        const offlineSale = await this.saveOfflineSale(payload)
        this.loading = false
        return offlineSale
      }

      try {
        const response = await axios.post('/api/sales/checkout', payload)
        this.clearCart()
        return response.data.sale
      } catch (err) {
        const isNetworkError = !err.response || err.message === 'Network Error' || err.code === 'ERR_NETWORK'
        if (isNetworkError) {
          console.warn('Network error during checkout, queueing transaction offline.', err)
          const offlineSale = await this.saveOfflineSale(payload)
          return offlineSale
        } else {
          this.error = err.response?.data?.error || 'Checkout transaction failed'
          return null
        }
      } finally {
        this.loading = false
      }
    },
    async saveOfflineSale(payload) {
      await this.loadFromLocalDb()
      const productsStore = useProductsStore()
      await productsStore.loadFromLocalDb()
      const tempInvoice = `OFFLINE-INV-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`
      
      const saleItems = this.items.map(item => {
        const product = productsStore.products.find(p => p.id === item.product_id)
        if (product) {
          product.stock_quantity = Math.max(0, product.stock_quantity - item.quantity)
        }
        return {
          id: `offline-item-${Date.now()}-${Math.random()}`,
          product_id: item.product_id,
          product_name: item.name,
          product_sku: item.sku,
          quantity: item.quantity,
          unit_price: item.price,
          total_price: item.price * item.quantity
        }
      })
      
      try {
        await dbPutAll('products', productsStore.products)
      } catch (err) {
        console.error('Failed to update local products stock in IndexedDB', err)
      }
      
      const offlineSale = {
        id: `offline-${Date.now()}-${Math.random()}`,
        invoice_number: tempInvoice,
        subtotal: this.subtotal,
        tax: this.taxAmount,
        discount: this.discount,
        total: this.total,
        payment_method: payload.payment_method,
        cashier_id: JSON.parse(localStorage.getItem('user'))?.id || 1,
        cashier_name: JSON.parse(localStorage.getItem('user'))?.username || 'Offline Cashier',
        customer_id: payload.customer_id,
        customer_name: this.selectedCustomer?.name || null,
        created_at: new Date().toISOString(),
        items: saleItems,
        is_offline: true,
        payload: payload
      }
      
      this.offlineSalesQueue.push(offlineSale)
      try {
        await dbPut('sales_queue', offlineSale)
      } catch (err) {
        console.error('Failed to save offline sale to IndexedDB', err)
      }
      
      this.clearCart()
      return offlineSale
    },
    async syncOfflineSales() {
      await this.loadFromLocalDb()
      if (this.isSyncing || this.offlineSalesQueue.length === 0) return
      this.isSyncing = true
      
      const queue = [...this.offlineSalesQueue]
      let successfulCount = 0
      
      for (const sale of queue) {
        try {
          await axios.post('/api/sales/checkout', sale.payload)
          this.offlineSalesQueue = this.offlineSalesQueue.filter(s => s.id !== sale.id)
          await dbDelete('sales_queue', sale.id)
          successfulCount++
        } catch (err) {
          const isNetworkError = !err.response || err.message === 'Network Error' || err.code === 'ERR_NETWORK'
          if (isNetworkError) {
            console.error('Network still offline, halting sync.', err)
            break
          } else {
            console.error(`Invalid transaction skipped: ${sale.invoice_number}`, err.response?.data?.error)
            this.offlineSalesQueue = this.offlineSalesQueue.filter(s => s.id !== sale.id)
            await dbDelete('sales_queue', sale.id)
          }
        }
      }
      
      this.isSyncing = false
      if (successfulCount > 0) {
        const productsStore = useProductsStore()
        await productsStore.fetchProducts()
      }
    },
    async fetchDiscounts() {
      try {
        const response = await axios.get('/api/sales/discounts')
        await dbPutAll('discounts', response.data)
        return response.data
      } catch (err) {
        console.error('Failed to fetch discounts from API', err)
        return await dbGetAll('discounts')
      }
    },
    async applyDiscountCode(code) {
      this.loading = true
      this.error = null
      const codeCleaned = String(code || '').trim().toUpperCase()
      if (!codeCleaned) {
        this.appliedDiscount = null
        this.discount = 0.00
        this.loading = false
        return null
      }
      
      try {
        let discountObj = null
        if (this.isOnline) {
          try {
            const response = await axios.get(`/api/sales/discounts/validate/${codeCleaned}`)
            discountObj = response.data
            await dbPut('discounts', discountObj)
          } catch (err) {
            const isNetworkError = !err.response || err.message === 'Network Error' || err.code === 'ERR_NETWORK'
            if (isNetworkError) {
              const localDiscounts = await dbGetAll('discounts')
              discountObj = localDiscounts.find(d => d.code === codeCleaned && d.is_active)
            } else {
              throw err
            }
          }
        } else {
          const localDiscounts = await dbGetAll('discounts')
          discountObj = localDiscounts.find(d => d.code === codeCleaned && d.is_active)
        }
        
        if (!discountObj) {
          this.error = 'Invalid or inactive discount code'
          this.appliedDiscount = null
          this.discount = 0.00
          return null
        }
        
        this.appliedDiscount = discountObj
        this.calculateDiscountAmount()
        return discountObj
      } catch (err) {
        this.error = err.response?.data?.error || 'Invalid discount code'
        this.appliedDiscount = null
        this.discount = 0.00
        return null
      } finally {
        this.loading = false
      }
    },
    initConnection() {
      this.isOnline = navigator.onLine
      
      window.addEventListener('online', () => {
        this.isOnline = true
        this.syncOfflineSales()
        this.fetchDiscounts()
      })
      window.addEventListener('offline', () => {
        this.isOnline = false
      })
      
      this.loadFromLocalDb().then(() => {
        if (this.isOnline) {
          this.syncOfflineSales()
          this.fetchDiscounts()
        }
      })
      
      // Periodic check
      setInterval(async () => {
        await this.loadFromLocalDb()
        if (this.offlineSalesQueue.length > 0) {
          try {
            const response = await axios.get('/api/auth/me')
            if (response.status === 200) {
              this.isOnline = true
              this.syncOfflineSales()
            }
          } catch (err) {
            if (err.response) {
              this.isOnline = true
              this.syncOfflineSales()
            } else {
              this.isOnline = false
            }
          }
        }
      }, 30000)
    }
  }
})
