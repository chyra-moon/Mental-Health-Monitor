<template>
  <header class="page-header">
    <div class="header-content">
      <span v-if="eyebrow" class="eyebrow">{{ eyebrow }}</span>
      <h2 class="title">{{ title }}</h2>
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
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--mh-surface);
  border-bottom: 1px solid var(--mh-line);
  margin-bottom: 16px;
  border-radius: var(--mh-radius-md);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.eyebrow {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--mh-primary);
}

.title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--mh-ink);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
