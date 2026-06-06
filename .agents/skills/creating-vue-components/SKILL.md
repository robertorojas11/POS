---
name: creating-vue-components
description: Creates new reusable Vue 3 components for the ApexPOS frontend. Use when building UI elements, widgets, cards, modals, or other reusable interface pieces.
---

# Creating Vue Components

## When to use this skill
- Building a new reusable UI element (card, badge, modal, selector, etc.).
- Extracting repeated markup from a view into a component.
- Creating a layout component.

## Workflow
1. [ ] **Identify component purpose** and its props/emits interface.
2. [ ] **Create component file** in `frontend/src/components/`.
3. [ ] **Implement** using `<script setup>` + `<style scoped>`.
4. [ ] **Import and use** in the target view.
5. [ ] **Build verify** with `npm run build`.

## Instructions

### 1. File Location & Naming
- Reusable components: `frontend/src/components/<PascalName>.vue`
- Layout components: `frontend/src/components/layouts/<PascalName>.vue`
- Naming: PascalCase, descriptive (e.g., `ProductCard.vue`, `MetricCard.vue`, `StatusBadge.vue`)

### 2. Component Template
```vue
<template>
  <div class="your-component">
    <!-- Component markup -->
    <h4 class="component-title">{{ title }}</h4>
    <p class="component-text">{{ description }}</p>
    <button class="pos-btn pos-btn-accent" @click="$emit('action')">
      <IconComponent class="btn-icon" />
      Action
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { IconComponent } from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: 'active'
  }
})

defineEmits(['action'])

const statusClass = computed(() => {
  const map = {
    'active': 'status-active',
    'inactive': 'status-inactive',
    'pending': 'status-pending'
  }
  return map[props.status] || 'status-default'
})
</script>

<style scoped>
.your-component {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 16px;
  transition: transform var(--transition-normal),
              box-shadow var(--transition-normal);
}

.your-component:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.component-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.component-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.btn-icon {
  width: 16px;
  height: 16px;
}
</style>
```

### 3. Design System Rules
- **Always use CSS variables** from `style.css` — never hardcode colors, radii, or shadows.
- **Font**: `Outfit` is set globally — do not override `font-family`.
- **Color palette**:
  - Primary: `--text-primary` (#111827), `--text-secondary` (#4b5563), `--text-muted` (#9ca3af)
  - Accent: `--accent-lime` (#B8F15A), `--accent-success` (#10b981), `--accent-warning` (#f59e0b), `--accent-danger` (#ff5e5e)
  - Surfaces: `--bg-app` (#f3f4f6), `--bg-card` (#ffffff), `--bg-sidebar` (#111111)
- **Spacing**: Multiples of 4px (4, 8, 12, 16, 20, 24, 32).
- **Border radius**: Use CSS variables (`--radius-sm/md/lg/xl`).
- **Transitions**: Use `var(--transition-fast)` or `var(--transition-normal)`.
- **Buttons**: Use `.pos-btn`, `.pos-btn-accent`, `.pos-btn-secondary`, `.pos-btn-danger`.
- **Cards**: Use `.premium-card` for card containers.
- **Inputs**: Use `.pos-input` class.
- **Icons**: Always import from `lucide-vue-next`, size 16-20px.

### 4. v-model Pattern
For components that wrap form elements:
```vue
<script setup>
defineProps({ modelValue: { type: String, default: '' } })
defineEmits(['update:modelValue'])
</script>

<template>
  <input
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
    class="pos-input"
  />
</template>
```

### 5. Existing Components Reference
| Component | Props | Purpose |
|-----------|-------|---------|
| `ProductCard` | name, sku, price, stock, uom, minSaleQty | Product tile in POS grid |
| `TransactionItem` | name, sku, price, quantity, uom | Cart line item |
| `MetricCard` | title, value, trend, icon, iconColor | KPI display card |
| `SectionCard` | title, description | Generic wrapper with slots |
| `StatusBadge` | status | Dot + text status indicator |
| `FilterBar` | selectedDateRange, cashiers, categories | Report filter controls |
| `PaymentSelector` | modelValue | Cash/Card/Mobile selector |
| `AppHeader` | title, isOnline, pendingSyncCount | Top navigation bar |
| `AppSidebar` | — | Left nav rail (85px) |

## Why This Skill Exists
- **Protects**: Design system consistency, scoped CSS isolation, Composition API standard.
- **Prevents**: Inline styles, hardcoded colors, non-scoped CSS leaks, inconsistent prop typing.
- **Evolution**: Consider extracting a shared composables directory if computed logic is frequently reused across components.
