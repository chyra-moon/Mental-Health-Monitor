<template>
  <header class="page-heading" :class="`tone-${tone}`">
    <div class="heading-mark" aria-hidden="true"></div>
    <div class="heading-copy">
      <span v-if="eyebrow" class="heading-eyebrow">{{ eyebrow }}</span>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="heading-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  tone: { type: String, default: 'student' },
})
</script>

<style scoped>
.page-heading {
  display: flex;
  align-items: stretch;
  gap: var(--mh-space-4);
  margin-bottom: var(--mh-space-5);
}

.heading-mark {
  width: 6px;
  border-radius: var(--mh-radius-sm);
  background: var(--mh-primary);
}

.tone-admin .heading-mark {
  background: var(--mh-sky);
}

.heading-copy {
  min-width: 0;
  flex: 1;
}

.heading-eyebrow {
  display: block;
  margin-bottom: 4px;
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 700;
}

h1 {
  margin: 0;
  color: var(--mh-ink);
  font-size: 24px;
  font-weight: 760;
  line-height: 1.25;
  letter-spacing: 0;
}

p {
  max-width: 760px;
  margin: 6px 0 0;
  color: var(--mh-muted);
  font-size: 14px;
  line-height: 1.7;
}

.heading-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: var(--mh-space-2);
}

@media (max-width: 720px) {
  .page-heading {
    flex-wrap: wrap;
  }

  .heading-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
