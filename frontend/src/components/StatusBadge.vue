<template>
  <span class="status-badge" :class="statusType">
    <span class="dot"></span>
    <span class="text">{{ text }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const text = computed(() => {
  return props.status.charAt(0).toUpperCase() + props.status.slice(1).toLowerCase()
})

const statusType = computed(() => {
  const s = props.status.toLowerCase()
  if (s === 'active' || s === 'open') return 'active'
  if (s === 'idle') return 'idle'
  if (s === 'break') return 'break'
  return 'offline'
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

/* Color States */
.status-badge.active {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.status-badge.idle {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--accent-warning);
}

.status-badge.break {
  background-color: rgba(79, 70, 229, 0.1);
  color: #6366f1;
}

.status-badge.offline {
  background-color: rgba(255, 94, 94, 0.1);
  color: var(--accent-danger);
}
</style>
