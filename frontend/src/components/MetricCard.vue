<template>
  <article class="metric-card" :class="cardClass">
    <div class="metric-copy">
      <div class="metric-head">
        <span class="metric-label">{{ label }}</span>
        <span class="metric-state" aria-hidden="true"></span>
      </div>
      <div class="metric-value-row">
        <strong class="metric-value" :title="valueText">{{ value }}</strong>
        <span v-if="unit" class="metric-unit">{{ unit }}</span>
      </div>
      <p v-if="note" class="metric-note" :title="note">{{ note }}</p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  unit: {
    type: String,
    default: '',
  },
  note: {
    type: String,
    default: '',
  },
  tone: {
    type: String,
    default: 'neutral',
  },
  icon: {
    type: String,
    default: 'data',
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const valueText = computed(() => String(props.value ?? ''))
const cardClass = computed(() => [
  `tone-${props.tone}`,
  {
    'is-compact': props.compact,
    'is-long-value': valueText.value.length > 7,
  },
])
</script>

<style scoped>
.metric-card {
  --metric-accent: var(--mh-line-strong);
  --metric-accent-soft: var(--mh-surface-muted);
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: stretch;
  min-width: 0;
  min-height: 132px;
  padding: 18px;
  overflow: hidden;
  color: var(--mh-text);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 250, 250, 0.98) 100%);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
}

.metric-card::before {
  position: absolute;
  top: 16px;
  bottom: 16px;
  left: 0;
  width: 3px;
  content: "";
  background: var(--metric-accent);
  border-radius: 0 999px 999px 0;
}

.metric-copy {
  display: flex;
  flex: 1 1 auto;
  min-width: 0;
  align-self: stretch;
  flex-direction: column;
  justify-content: flex-start;
}

.metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
}

.metric-label {
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 720;
  line-height: 1.4;
}

.metric-state {
  flex: 0 0 auto;
  width: 28px;
  height: 4px;
  background: var(--metric-accent);
  border-radius: 999px;
  opacity: 0.92;
}

.metric-value-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  min-width: 0;
  margin-top: 10px;
}

.metric-value {
  min-width: 0;
  overflow: hidden;
  color: var(--mh-ink);
  font-size: 30px;
  font-variant-numeric: tabular-nums;
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: 0;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-card.tone-warning .metric-value,
.metric-card.tone-medium .metric-value {
  color: var(--mh-warning);
}

.metric-card.tone-danger .metric-value,
.metric-card.tone-high .metric-value {
  color: var(--mh-danger);
}

.metric-unit {
  flex: none;
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 720;
}

.metric-note {
  display: -webkit-box;
  min-height: 35px;
  margin: 12px 0 0;
  overflow: hidden;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.metric-card.is-compact {
  min-height: 116px;
  padding-top: 15px;
  padding-bottom: 14px;
}

.metric-card.is-long-value .metric-value {
  font-size: 20px;
  line-height: 1.15;
}

.metric-card.tone-info {
  --metric-accent: var(--mh-info);
  --metric-accent-soft: var(--mh-info-soft);
}

.metric-card.tone-warning,
.metric-card.tone-medium {
  --metric-accent: var(--mh-warning);
  --metric-accent-soft: var(--mh-warning-soft);
}

.metric-card.tone-danger,
.metric-card.tone-high {
  --metric-accent: var(--mh-danger);
  --metric-accent-soft: var(--mh-danger-soft);
}

.metric-card.tone-stable,
.metric-card.tone-low {
  --metric-accent: var(--mh-primary-strong);
  --metric-accent-soft: var(--mh-primary-soft);
}

.metric-card.tone-muted,
.metric-card.tone-neutral {
  --metric-accent: var(--mh-line-strong);
  --metric-accent-soft: var(--mh-surface-muted);
}
</style>
