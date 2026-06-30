<template>
  <header class="page-header">
    <div class="header-content">
      <span v-if="eyebrow" class="eyebrow">{{ eyebrow }}</span>
      <h2 class="title">{{ title }}</h2>
      <p v-if="description" class="description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="header-actions">
      <slot name="actions"></slot>
    </div>
  </header>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 16px 20px;
  background: var(--mh-surface);
  border-bottom: 1px solid var(--mh-line);
  margin-bottom: 16px;
  border-radius: var(--mh-radius-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.eyebrow {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--mh-primary);
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--mh-ink);
}

.description {
  margin: 0;
  font-size: 13px;
  color: var(--mh-muted);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
