import { defineStore } from 'pinia'
import axios from 'axios'
import { dbGetAll, dbPutAll, dbPut } from '@/utils/indexedDb'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    categories: [],
    loading: false,
    error: null,
    localDbLoaded: false
  }),
  actions: {
    async loadFromLocalDb() {
      if (this.localDbLoaded) return
      try {
        this.products = await dbGetAll('products')
        this.categories = await dbGetAll('categories')
        this.localDbLoaded = true
      } catch (err) {
        console.error('Failed to load products from IndexedDB', err)
      }
    },
    async fetchProducts(searchParams = {}) {
      this.loading = true
      await this.loadFromLocalDb()
      try {
        const response = await axios.get('/api/products', { params: searchParams })
        this.products = response.data
        await dbPutAll('products', response.data)
        return this.products
      } catch (err) {
        this.error = 'Failed to load products'
        return this.products
      } finally {
        this.loading = false
      }
    },
    async fetchCategories() {
      await this.loadFromLocalDb()
      try {
        const response = await axios.get('/api/products/categories')
        this.categories = response.data
        await dbPutAll('categories', response.data)
      } catch (err) {
        this.error = 'Failed to load categories'
      }
    },
    async searchByBarcode(barcode) {
      this.loading = true
      try {
        const response = await axios.get(`/api/products/barcode/${barcode}`)
        return response.data
      } catch (err) {
        await this.loadFromLocalDb()
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
        await dbPut('products', response.data)
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
        await dbPut('products', response.data)
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
