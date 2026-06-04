import { defineStore } from 'pinia'
import axios from 'axios'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: JSON.parse(localStorage.getItem('cached_products')) || [],
    categories: JSON.parse(localStorage.getItem('cached_categories')) || [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchProducts(searchParams = {}) {
      this.loading = true
      try {
        const response = await axios.get('/api/products', { params: searchParams })
        this.products = response.data
        localStorage.setItem('cached_products', JSON.stringify(response.data))
        return this.products
      } catch (err) {
        this.error = 'Failed to load products'
        const cached = localStorage.getItem('cached_products')
        if (cached) {
          this.products = JSON.parse(cached)
        }
        return this.products
      } finally {
        this.loading = false
      }
    },
    async fetchCategories() {
      try {
        const response = await axios.get('/api/products/categories')
        this.categories = response.data
        localStorage.setItem('cached_categories', JSON.stringify(response.data))
      } catch (err) {
        this.error = 'Failed to load categories'
        const cached = localStorage.getItem('cached_categories')
        if (cached) {
          this.categories = JSON.parse(cached)
        }
      }
    },
    async searchByBarcode(barcode) {
      this.loading = true
      try {
        const response = await axios.get(`/api/products/barcode/${barcode}`)
        return response.data
      } catch (err) {
        // Offline search fallback
        const localProduct = this.products.find(p => p.barcode === barcode || p.sku === barcode)
        if (localProduct) return localProduct
        return null
      } finally {
        this.loading = false
      }
    },
    async createProduct(productData) {
      this.loading = true
      try {
        const response = await axios.post('/api/products', productData)
        this.products.push(response.data)
        // Refresh local cache
        localStorage.setItem('cached_products', JSON.stringify(this.products))
        return response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to create product'
        return null
      } finally {
        this.loading = false
      }
    },
    async updateProduct(productId, productData) {
      this.loading = true
      try {
        const response = await axios.put(`/api/products/${productId}`, productData)
        const index = this.products.findIndex(p => p.id === productId)
        if (index > -1) {
          this.products[index] = response.data
        }
        localStorage.setItem('cached_products', JSON.stringify(this.products))
        return response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to update product'
        return null
      } finally {
        this.loading = false
      }
    }
  }
})
