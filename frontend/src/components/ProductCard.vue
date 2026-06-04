<template>
  <div class="product-card" @click="$emit('add')">
    <div class="product-image-container">
      <div class="product-placeholder">
        <span class="product-initials">{{ initials }}</span>
      </div>
      <div class="stock-badge" :class="stockClass">
        {{ formattedStock }} {{ uom }}
      </div>
    </div>
    <div class="product-info">
      <div class="product-meta">
        <h4 class="product-name" :title="name">{{ name }}</h4>
        <span class="product-sku">{{ sku }}</span>
      </div>
      <div class="product-action-row">
        <div class="price-group">
          <span class="product-price">${{ priceWithTax.toFixed(2) }}</span>
          <span class="product-price-tax">Excl. tax: ${{ Number(price).toFixed(2) }}</span>
        </div>
        <button class="add-btn" @click.stop="$emit('add')">
          <Plus class="add-icon" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus } from 'lucide-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  sku: {
    type: String,
    required: true
  },
  price: {
    type: [Number, String],
    required: true
  },
  stock: {
    type: [Number, String],
    required: true
  },
  uom: {
    type: String,
    default: 'pieces'
  }
})

defineEmits(['add'])

const initials = computed(() => {
  return props.name?.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase() || 'P'
})

const formattedStock = computed(() => {
  const s = parseFloat(props.stock)
  return Number.isInteger(s) ? s.toString() : s.toFixed(3)
})

const stockClass = computed(() => {
  const s = parseFloat(props.stock)
  if (s <= 0) return 'out-of-stock'
  if (s <= 5) return 'low-stock'
  return 'in-stock'
})

const priceWithTax = computed(() => {
  return parseFloat(props.price) * 1.0825
})
</script>

<style scoped>
.product-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal), border-color var(--transition-fast);
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--text-muted);
}

.product-image-container {
  height: 120px;
  background-color: #f9fafb;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid #f3f4f6;
}

.product-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-initials {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.stock-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 12px;
}

.stock-badge.in-stock {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.stock-badge.low-stock {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--accent-warning);
}

.stock-badge.out-of-stock {
  background-color: rgba(255, 94, 94, 0.1);
  color: var(--accent-danger);
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-grow: 1;
}

.product-meta {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-sku {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 1px;
}

.product-action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.product-price {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.add-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-lime);
  color: var(--accent-lime-text);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.add-btn:hover {
  background-color: var(--accent-lime-hover);
  transform: scale(1.05);
}

.add-icon {
  width: 16px;
  height: 16px;
  stroke-width: 3px;
}

.price-group {
  display: flex;
  flex-direction: column;
}

.product-price-tax {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  margin-top: 1px;
}
</style>
