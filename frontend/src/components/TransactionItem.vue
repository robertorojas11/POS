<template>
  <div class="transaction-item">
    <div class="product-thumb">
      <span class="thumb-initial">{{ name.charAt(0) }}</span>
    </div>
    
    <div class="item-details">
      <h5 class="item-name" :title="name">{{ name }}</h5>
      <div class="item-meta">
        <span class="item-sku">{{ sku }}</span>
        <span class="item-uom-chip">{{ uom }}</span>
      </div>
    </div>
    
    <div class="quantity-controls">
      <button class="qty-btn" @click="$emit('decrease')">
        <Minus class="qty-icon" />
      </button>
      <span class="qty-val">{{ formattedQty }}</span>
      <button class="qty-btn" @click="$emit('increase')">
        <Plus class="qty-icon" />
      </button>
    </div>
    
    <div class="item-pricing">
      <span class="item-total-price">${{ Number(totalPrice).toFixed(2) }}</span>
      <span class="item-total-price-tax">with tax: ${{ totalPriceWithTax.toFixed(2) }}</span>
      <span class="item-unit-price">${{ Number(price).toFixed(2) }} (with tax: ${{ unitPriceWithTax.toFixed(2) }}) / {{ uom }}</span>
    </div>
    
    <button class="remove-btn" @click="$emit('remove')">
      <Trash2 class="remove-icon" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Minus, Trash2 } from 'lucide-vue-next'

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
  quantity: {
    type: [Number, String],
    required: true
  },
  uom: {
    type: String,
    default: 'pieces'
  }
})

defineEmits(['increase', 'decrease', 'remove'])

const formattedQty = computed(() => {
  const q = parseFloat(props.quantity)
  return Number.isInteger(q) ? q.toString() : q.toFixed(3)
})

const totalPrice = computed(() => {
  return parseFloat(props.price) * parseFloat(props.quantity)
})

const unitPriceWithTax = computed(() => {
  return parseFloat(props.price) * 1.0825
})

const totalPriceWithTax = computed(() => {
  return totalPrice.value * 1.0825
})
</script>

<style scoped>
.transaction-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.product-thumb {
  width: 40px;
  height: 40px;
  background-color: #f3f4f6;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.thumb-initial {
  font-size: 1.1rem;
}

.item-details {
  flex-grow: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.item-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 1px;
}

.item-sku {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.item-uom-chip {
  font-size: 0.65rem;
  background-color: #f3f4f6;
  color: var(--text-secondary);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f9fafb;
  padding: 4px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  flex-shrink: 0;
}

.qty-btn {
  width: 26px;
  height: 26px;
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

.qty-btn:hover {
  background-color: var(--accent-lime-hover);
}

.qty-icon {
  width: 12px;
  height: 12px;
  stroke-width: 3px;
}

.qty-val {
  font-size: 0.85rem;
  font-weight: 700;
  min-width: 36px;
  text-align: center;
  color: var(--text-primary);
}

.item-pricing {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 85px;
  flex-shrink: 0;
}

.item-total-price {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.item-total-price-tax {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
}

.item-unit-price {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-align: right;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.remove-btn:hover {
  color: var(--accent-danger);
  background-color: rgba(255, 94, 94, 0.1);
}

.remove-icon {
  width: 16px;
  height: 16px;
}
</style>
