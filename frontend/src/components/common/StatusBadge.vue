<template>
  <span class="status-badge" :class="`status-${normalizedType}`">
    <i aria-hidden="true"></i>
    {{ displayLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'info' },
  label: { type: String, default: '' },
})

const defaultLabels = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  handled: '已处理',
  pending: '待处理',
  normal: '正常',
  disabled: '禁用',
  success: '成功',
  warning: '提醒',
  danger: '异常',
  info: '信息',
  video: '视频分析',
  image: '图片识别',
  camera: '摄像头',
}

const normalizedType = computed(() => props.type || 'info')
const displayLabel = computed(() => props.label || defaultLabels[normalizedType.value] || normalizedType.value)
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  max-width: 100%;
  min-height: 26px;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  border: 1px solid var(--mh-line);
  border-radius: 999px;
  background: var(--mh-info-soft);
  color: var(--mh-info);
  font-size: 12px;
  font-weight: 720;
  line-height: 1.5;
  white-space: nowrap;
}

i {
  width: 7px;
  height: 7px;
  flex: none;
  border-radius: 999px;
  background: currentColor;
}

.status-low,
.status-success,
.status-handled,
.status-normal {
  border-color: #c8dfcb;
  background: var(--mh-green-soft);
  color: var(--mh-green);
}

.status-medium,
.status-warning,
.status-pending,
.status-video {
  border-color: #efd4a6;
  background: var(--mh-warning-soft);
  color: var(--mh-warning);
}

.status-high,
.status-danger,
.status-disabled {
  border-color: #e8bbb3;
  background: var(--mh-danger-soft);
  color: var(--mh-danger);
}

.status-image,
.status-camera {
  border-color: #bed8df;
  background: var(--mh-info-soft);
  color: var(--mh-sky);
}
</style>
