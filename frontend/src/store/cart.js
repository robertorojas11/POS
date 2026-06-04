import { defineStore } from 'pinia'
import axios from 'axios'
import { useProductsStore } from './products'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    discount: 0.00,
    taxRate: 0.0825,
    selectedCustomer: null,
    loading: false,
    error: null,
    isOnline: navigator.onLine,
    offlineSalesQueue: JSON.parse(localStorage.getItem('offline_sales_queue')) || [],
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
    addToCart(product) {
      const existing = this.items.find(item => item.product_id === product.id)
      if (existing) {
        if (existing.quantity < product.stock_quantity) {
          existing.quantity++
        }
      } else {
        this.items.push({
          product_id: product.id,
          sku: product.sku,
          name: product.name,
          price: product.price,
          quantity: 1,
          stock_available: product.stock_quantity
        })
      }
    },
    removeFromCart(productId) {
      const index = this.items.findIndex(item => item.product_id === productId)
      if (index > -1) {
        this.items.splice(index, 1)
      }
    },
    updateQuantity(productId, qty) {
      const item = this.items.find(item => item.product_id === productId)
      if (item) {
        if (qty <= 0) {
          this.removeFromCart(productId)
        } else {
          item.quantity = Math.min(qty, item.stock_available)
        }
      }
    },
    setDiscount(discountAmount) {
      this.discount = Math.max(0, parseFloat(discountAmount) || 0)
    },
    selectCustomer(customer) {
      this.selectedCustomer = customer
    },
    clearCart() {
      this.items = []
      this.discount = 0.00
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
        const offlineSale = this.saveOfflineSale(payload)
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
          const offlineSale = this.saveOfflineSale(payload)
          return offlineSale
        } else {
          this.error = err.response?.data?.error || 'Checkout transaction failed'
          return null
        }
      } finally {
        this.loading = false
      }
    },
    saveOfflineSale(payload) {
      const productsStore = useProductsStore()
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
      
      localStorage.setItem('cached_products', JSON.stringify(productsStore.products))
      
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
      localStorage.setItem('offline_sales_queue', JSON.stringify(this.offlineSalesQueue))
      
      this.clearCart()
      return offlineSale
    },
    async syncOfflineSales() {
      if (this.isSyncing || this.offlineSalesQueue.length === 0) return
      this.isSyncing = true
      
      const queue = [...this.offlineSalesQueue]
      let successfulCount = 0
      
      for (const sale of queue) {
        try {
          await axios.post('/api/sales/checkout', sale.payload)
          this.offlineSalesQueue = this.offlineSalesQueue.filter(s => s.id !== sale.id)
          localStorage.setItem('offline_sales_queue', JSON.stringify(this.offlineSalesQueue))
          successfulCount++
        } catch (err) {
          const isNetworkError = !err.response || err.message === 'Network Error' || err.code === 'ERR_NETWORK'
          if (isNetworkError) {
            console.error('Network still offline, halting sync.', err)
            break
          } else {
            console.error(`Invalid transaction skipped: ${sale.invoice_number}`, err.response?.data?.error)
            this.offlineSalesQueue = this.offlineSalesQueue.filter(s => s.id !== sale.id)
            localStorage.setItem('offline_sales_queue', JSON.stringify(this.offlineSalesQueue))
          }
        }
      }
      
      this.isSyncing = false
      if (successfulCount > 0) {
        const productsStore = useProductsStore()
        await productsStore.fetchProducts()
      }
    },
    initConnection() {
      this.isOnline = navigator.onLine
      
      window.addEventListener('online', () => {
        this.isOnline = true
        this.syncOfflineSales()
      })
      window.addEventListener('offline', () => {
        this.isOnline = false
      })
      
      // Periodic check
      setInterval(async () => {
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
