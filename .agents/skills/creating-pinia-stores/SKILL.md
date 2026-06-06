---
name: creating-pinia-stores
description: Creates new Pinia state management stores for the ApexPOS Vue 3 frontend. Use when adding a new store module, managing new domain state, or connecting a new API resource to the frontend.
---

# Creating Pinia Stores

## When to use this skill
- Adding a new domain store for a frontend feature.
- Connecting a new backend API resource to the frontend state layer.
- Managing shared state that multiple views or components need.

## Workflow
1. [ ] **Identify state shape**: Determine the data, loading, and error states needed.
2. [ ] **Create store file** in `frontend/src/store/`.
3. [ ] **Implement actions** for API communication.
4. [ ] **Connect store** to views/components.
5. [ ] **Build verify** with `npm run build`.

## Instructions

### 1. File Naming
- File: `frontend/src/store/<entity>.js` (singular camelCase).
- Export: `use<Entity>Store` (e.g., `useProductsStore`, `useAuthStore`).

### 2. Store Template
All stores use the **Options API** style (not Composition API `setup()`):

```javascript
import { defineStore } from 'pinia'
import axios from 'axios'

export const useEntityStore = defineStore('entity', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  getters: {
    activeItems: (state) => state.items.filter(i => i.is_active),
    itemCount: (state) => state.items.length
  },
  actions: {
    async fetchItems() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('/api/entities')
        this.items = response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load items'
      } finally {
        this.loading = false
      }
    },
    async createItem(data) {
      this.loading = true
      try {
        const response = await axios.post('/api/entities', data)
        this.items.push(response.data)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to create item'
        return null
      } finally {
        this.loading = false
      }
    },
    async updateItem(id, data) {
      this.loading = true
      try {
        const response = await axios.put(`/api/entities/${id}`, data)
        const index = this.items.findIndex(i => i.id === id)
        if (index > -1) {
          this.items[index] = response.data
        }
        return response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to update item'
        return null
      } finally {
        this.loading = false
      }
    },
    async deleteItem(id) {
      this.loading = true
      try {
        await axios.delete(`/api/entities/${id}`)
        this.items = this.items.filter(i => i.id !== id)
        return true
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to delete item'
        return false
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 3. Critical Rules
- **Always use relative URLs**: `/api/...` — Vite proxy forwards to Flask backend.
- **Never import axios with baseURL**: The global interceptors in `main.js` handle auth headers.
- **Error extraction**: Always use `err.response?.data?.error || 'fallback message'`.
- **Loading state**: Set `loading = true` at start, reset in `finally` block.
- **Null returns on error**: CRUD actions return `null`/`false` on failure so views can react.
- **No API calls in components**: ALL axios calls must live in store actions.

### 4. IndexedDB Integration (Optional)
For stores that need offline support, integrate with `utils/indexedDb.js`:

```javascript
import { dbGetAll, dbPutAll, dbPut } from '@/utils/indexedDb'

// In state:
localDbLoaded: false

// Action to load from local DB first:
async loadFromLocalDb() {
  if (this.localDbLoaded) return
  try {
    this.items = await dbGetAll('store_name')
    this.localDbLoaded = true
  } catch (err) {
    console.error('Failed to load from IndexedDB', err)
  }
}
```

### 5. Existing Stores Reference
| Store | File | State Fields | Key Patterns |
|-------|------|-------------|---------------|
| `useAuthStore` | `auth.js` | token, user, loading, error | localStorage persistence, axios header management |
| `useProductsStore` | `products.js` | products, categories, loading, error, localDbLoaded | IndexedDB cache, barcode search fallback |
| `useCartStore` | `cart.js` | items, discount, taxRate, selectedCustomer, isOnline, offlineSalesQueue | Offline checkout, connectivity monitoring, UOM quantity steps |

## Why This Skill Exists
- **Protects**: Uniform store structure, consistent error handling, API-via-store-only pattern.
- **Prevents**: Inline axios calls in components, missing loading states, inconsistent error formats.
- **Evolution**: Consider migrating to Composition API `setup()` stores if the team prefers; the pattern would change but the conventions remain.
