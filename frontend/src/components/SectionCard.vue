<template>
  <div class="section-card premium-card">
    <div v-if="title || $slots.header" class="card-header">
      <div v-if="title" class="header-text-group">
        <h4 class="card-title">{{ title }}</h4>
        <p v-if="description" class="card-desc">{{ description }}</p>
      </div>
      <slot name="header"></slot>
    </div>
    
    <div class="card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.section-card {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.card-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.card-body {
  flex-grow: 1;
}

.card-footer {
  margin-top: 20px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}
</style>
