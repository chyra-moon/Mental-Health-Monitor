<template>
  <section class="metric-card" :class="`accent-${accent}`">
    <div class="metric-icon" v-if="$slots.icon">
      <slot name="icon" />
    </div>
    <div class="metric-copy">
      <span class="metric-label">{{ label }}</span>
      <strong class="metric-value">
        {{ value }}
        <small v-if="unit">{{ unit }}</small>
      </strong>
      <p v-if="caption">{{ caption }}</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '-' },
  unit: { type: String, default: '' },
  caption: { type: String, default: '' },
  accent: { type: String, default: 'teal' },
})
</script>

<style scoped>
.metric-card {
  min-height: 120px;
  display: flex;
  gap: var(--mh-space-4);
  align-items: flex-start;
  padding: var(--mh-space-5);
  border: 1px solid var(--mh-line);
  border-left-width: 5px;
  border-radius: var(--mh-radius);
  background: var(--mh-surface);
  box-shadow: var(--mh-shadow-soft);
}

.accent-teal {
  border-left-color: var(--mh-primary);
}

.accent-sky {
  border-left-color: var(--mh-sky);
}

.accent-warm {
  border-left-color: var(--mh-warm);
}

.accent-danger {
  border-left-color: var(--mh-danger);
}

.accent-green {
  border-left-color: var(--mh-green);
}

.metric-icon {
  width: 42px;
  height: 42px;
  display: grid;
  flex: none;
  place-items: center;
  border-radius: var(--mh-radius);
  color: var(--mh-primary-dark);
  background: var(--mh-primary-soft);
  font-size: 20px;
}

.accent-sky .metric-icon {
  color: var(--mh-sky);
  background: var(--mh-info-soft);
}

.accent-warm .metric-icon {
  color: var(--mh-warning);
  background: var(--mh-warm-soft);
}

.accent-danger .metric-icon {
  color: var(--mh-danger);
  background: var(--mh-danger-soft);
}

.accent-green .metric-icon {
  color: var(--mh-green);
  background: var(--mh-green-soft);
}

.metric-copy {
  min-width: 0;
}

.metric-label {
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 700;
}

.metric-value {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 30px;
  font-weight: 780;
  line-height: 1.1;
}

.metric-value small {
  margin-left: 4px;
  color: var(--mh-muted);
  font-size: 14px;
  font-weight: 700;
}

p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.6;
}
</style>
