<template>
  <section class="chart-frame">
    <div class="chart-frame-head">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      <slot name="meta" />
    </div>
    <div class="chart-frame-body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.chart-frame {
  min-width: 0;
  padding: var(--mh-space-4);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: var(--mh-surface);
  box-shadow: var(--mh-shadow-soft);
}

.chart-frame-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--mh-space-3);
  margin-bottom: var(--mh-space-3);
}

h3 {
  margin: 0;
  color: var(--mh-ink);
  font-size: 15px;
  font-weight: 760;
}

p {
  margin: 5px 0 0;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.5;
}

.chart-frame-body {
  min-width: 0;
}
</style>
