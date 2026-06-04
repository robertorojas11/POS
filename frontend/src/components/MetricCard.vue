<template>
  <div class="metric-card premium-card">
    <div class="card-content">
      <span class="card-title">{{ title }}</span>
      <h3 class="card-value">{{ value }}</h3>
      <p v-if="trend" class="card-trend" :class="trendType">
        <span class="trend-indicator">{{ trendIcon }}</span>
        {{ trend }}
      </p>
    </div>
    <div class="card-icon-wrapper" :style="{ backgroundColor: iconBg }">
      <component :is="icon" class="card-icon" :style="{ color: iconColor }" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  trend: {
    type: String,
    default: ''
  },
  trendType: {
    type: String,
    default: 'neutral' // positive, negative, neutral
  },
  icon: {
    type: Object,
    required: true
  },
  iconColor: {
    type: String,
    default: '#111827'
  },
  iconBg: {
    type: String,
    default: '#f3f4f6'
  }
})

const trendIcon = computed(() => {
  if (props.trendType === 'positive') return '↑'
  if (props.trendType === 'negative') return '↓'
  return '•'
})
</script>

<style scoped>
.metric-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.card-value {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
}

.card-trend {
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-trend.positive {
  color: var(--accent-success);
}

.card-trend.negative {
  color: var(--accent-danger);
}

.card-trend.neutral {
  color: var(--text-muted);
}

.card-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon {
  width: 22px;
  height: 22px;
}
</style>
