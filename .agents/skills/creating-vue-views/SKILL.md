---
name: creating-vue-views
description: Creates new page-level Vue 3 views for the ApexPOS frontend. Use when adding a new page, screen, or section to the application.
---

# Creating Vue Views

## When to use this skill
- Adding a new page to the ApexPOS application.
- Building a new management screen (e.g., Suppliers, Reports, Settings).
- Creating a new section within the authenticated layout.

## Workflow
1. [ ] **Define page scope**: Data displayed, actions available, role access.
2. [ ] **Create view file** in `frontend/src/views/`.
3. [ ] **Connect Pinia store** for data management.
4. [ ] **Add route** to `frontend/src/router/index.js`.
5. [ ] **Add sidebar link** to `AppSidebar.vue`.
6. [ ] **Build verify** with `npm run build`.

## Instructions

### 1. File Naming
- Location: `frontend/src/views/<PascalName>View.vue`
- Convention: Always ends with `View` suffix.
- Examples: `ProductsView.vue`, `ReportsView.vue`, `AdminView.vue`, `RegisterView.vue`.

### 2. View Template
```vue
<template>
  <div class="entity-view">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">Entity Management</h2>
        <p class="page-subtitle">Manage your entities</p>
      </div>
      <button class="pos-btn pos-btn-accent" @click="showCreateModal = true">
        <Plus :size="18" />
        Add Entity
      </button>
    </div>

    <!-- Content Area -->
    <div class="content-grid">
      <!-- Search/Filter Bar -->
      <div class="filter-row">
        <div class="search-container">
          <Search :size="18" class="search-icon" />
          <input
            v-model="searchQuery"
            class="pos-input with-left-icon"
            placeholder="Search entities..."
          />
        </div>
      </div>

      <!-- Data Table -->
      <div class="premium-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>{{ item.name }}</td>
              <td>
                <StatusBadge :status="item.is_active ? 'active' : 'inactive'" />
              </td>
              <td>
                <button class="pos-btn pos-btn-secondary" @click="editItem(item)">
                  Edit
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <h3 class="modal-title">{{ editingItem ? 'Edit' : 'Add' }} Entity</h3>
        <form @submit.prevent="saveItem">
          <div class="form-group">
            <label class="form-label">Name</label>
            <input v-model="form.name" class="pos-input" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="pos-btn pos-btn-secondary" @click="closeModal">
              Cancel
            </button>
            <button type="submit" class="pos-btn pos-btn-accent">
              {{ editingItem ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import { useEntityStore } from '@/store/entity'
import StatusBadge from '@/components/StatusBadge.vue'

const entityStore = useEntityStore()

const searchQuery = ref('')
const showCreateModal = ref(false)
const editingItem = ref(null)
const form = ref({ name: '' })

const filteredItems = computed(() => {
  if (!searchQuery.value) return entityStore.items
  const q = searchQuery.value.toLowerCase()
  return entityStore.items.filter(i => i.name.toLowerCase().includes(q))
})

onMounted(() => {
  entityStore.fetchItems()
})

const editItem = (item) => {
  editingItem.value = item
  form.value = { name: item.name }
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  editingItem.value = null
  form.value = { name: '' }
}

const saveItem = async () => {
  if (editingItem.value) {
    await entityStore.updateItem(editingItem.value.id, form.value)
  } else {
    await entityStore.createItem(form.value)
  }
  closeModal()
}
</script>

<style scoped>
.entity-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.filter-row {
  margin-bottom: 16px;
}

.search-container {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: 32px;
  width: 100%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
```

### 3. Route Registration
Add the view as a child of the MainLayout route in `frontend/src/router/index.js`:
```javascript
{
    path: 'entities',
    name: 'entities',
    component: () => import('@/views/EntitiesView.vue')
    // Add meta: { requiresAdmin: true } for admin-only pages
}
```

### 4. Layout Integration
All authenticated views render inside `MainLayout.vue` which provides:
- `AppSidebar` (85px fixed left rail)
- `AppHeader` (top bar with connection status)
- `<router-view>` content area with fade transitions

### 5. Existing Views Reference
| View | File | Size | Key Features |
|------|------|------|--------------|
| Login | `LoginView.vue` | 597 lines | Split-screen, standalone (no MainLayout) |
| Dashboard | `Dashboard.vue` | 787 lines | KPI grid, shift monitor, alerts |
| POS Register | `RegisterView.vue` | 1633 lines | Split catalog+cart, offline support |
| Products | `ProductsView.vue` | 973 lines | Catalog grid, detail drawer |
| Reports | `ReportsView.vue` | 1320 lines | Analytics + custom report generator |
| Admin | `AdminView.vue` | 1023 lines | Employees + stores tabs |

## Why This Skill Exists
- **Protects**: Consistent page layout, modal pattern, store integration, design system adherence.
- **Prevents**: Views without search/filter, missing modal close handlers, direct API calls in views.
- **Evolution**: Consider splitting large views (>800 lines) into sub-components or tabs.
