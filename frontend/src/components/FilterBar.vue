<template>
  <div class="filter-bar premium-card">
    <div class="filter-group">
      <label class="filter-label">Date Range</label>
      <div class="pill-selector">
        <button 
          v-for="range in dateRanges" 
          :key="range.id"
          class="pill-btn"
          :class="{ 'active': selectedDateRange === range.id }"
          @click="$emit('update:selectedDateRange', range.id)"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
    
    <div class="filter-inputs">
      <div class="filter-field">
        <label class="filter-label">Cashier</label>
        <select 
          :value="selectedCashier" 
          @change="$emit('update:selectedCashier', $event.target.value)"
          class="filter-select"
        >
          <option value="">All Cashiers</option>
          <option v-for="c in cashiers" :key="c.id" :value="c.id">
            {{ c.username }}
          </option>
        </select>
      </div>
      
      <div class="filter-field">
        <label class="filter-label">Category</label>
        <select 
          :value="selectedCategory" 
          @change="$emit('update:selectedCategory', $event.target.value)"
          class="filter-select"
        >
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedDateRange: {
    type: String,
    required: true
  },
  selectedCashier: {
    type: String,
    default: ''
  },
  selectedCategory: {
    type: String,
    default: ''
  },
  cashiers: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  }
})

defineEmits([
  'update:selectedDateRange',
  'update:selectedCashier',
  'update:selectedCategory'
])

const dateRanges = [
  { id: 'today', label: 'Today' },
  { id: 'yesterday', label: 'Yesterday' },
  { id: 'week', label: 'This Week' },
  { id: 'month', label: 'This Month' }
]
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 16px 24px;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.pill-selector {
  display: flex;
  background-color: #f3f4f6;
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  gap: 2px;
}

.pill-btn {
  background: none;
  border: none;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-fast);
}

.pill-btn:hover {
  color: var(--text-primary);
}

.pill-btn.active {
  background-color: var(--bg-card);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.filter-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-grow: 1;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .filter-inputs {
    justify-content: flex-start;
  }
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 140px;
}

.filter-select {
  padding: 8px 12px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-select:focus {
  outline: none;
  border-color: var(--border-focus);
}
</style>
