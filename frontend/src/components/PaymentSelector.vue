<template>
  <div class="payment-grid">
    <button 
      v-for="method in methods" 
      :key="method.id"
      class="payment-option-card"
      :class="{ 'selected': modelValue === method.id }"
      @click="$emit('update:modelValue', method.id)"
    >
      <component :is="method.icon" class="payment-icon" />
      <span class="payment-label">{{ method.name }}</span>
    </button>
  </div>
</template>

<script setup>
import { 
  Banknote, 
  CreditCard, 
  Smartphone 
} from 'lucide-vue-next'

defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

defineEmits(['update:modelValue'])

const methods = [
  { id: 'cash', name: 'Cash', icon: Banknote },
  { id: 'card', name: 'Card', icon: CreditCard },
  { id: 'mobile_pay', name: 'Mobile Pay', icon: Smartphone }
]
</script>

<style scoped>
.payment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.payment-option-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}

.payment-option-card:hover {
  background-color: #f9fafb;
  border-color: var(--text-muted);
}

.payment-option-card.selected {
  background-color: rgba(184, 241, 90, 0.15);
  border-color: var(--accent-lime-hover);
  box-shadow: 0 0 0 1px var(--accent-lime-hover);
}

.payment-icon {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.payment-option-card.selected .payment-icon {
  color: var(--text-primary);
}

.payment-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.payment-option-card.selected .payment-label {
  color: var(--text-primary);
}
</style>
