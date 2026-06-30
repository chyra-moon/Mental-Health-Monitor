<template>
  <div v-if="phase === 'running'" class="progress-container">
    <div class="progress-header">
      <span class="status-badge">
        <span class="pulse-dot"></span>
        正在生成分析报告...
      </span>
      <span class="count-text">{{ completedFrameCount }} / {{ frameCount }} 帧</span>
    </div>
    <el-progress
      :percentage="progressPercentage"
      :stroke-width="12"
      striped
      striped-flow
      :duration="15"
      color="var(--mh-primary)"
    />
    <div class="step-log">
      <div v-for="(log, idx) in logEntries" :key="idx" class="log-entry" :class="{ 'is-last': idx === logEntries.length - 1 }">
        <el-icon class="log-icon"><CircleCheck /></el-icon>
        <span>{{ log }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  phase: String,
  completedFrameCount: Number,
  frameCount: Number,
  progressPercentage: Number,
  hasFrameResults: Boolean
})

const logEntries = computed(() => {
  const list = []
  if (props.completedFrameCount > 0) {
    list.push('会话画面读取完成')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.25)) {
    list.push('面部状态识别中')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.5)) {
    list.push('情绪变化趋势生成中')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.75)) {
    list.push('风险等级复核中')
  }
  if (props.completedFrameCount === props.frameCount) {
    list.push('报告整理完成')
  }
  
  // 只返回最后两条日志，保持简洁
  return list.slice(-2)
})
</script>

<style scoped>
.progress-container {
  padding: 16px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  margin-top: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: var(--mh-ink);
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--mh-primary);
  box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.36);
  animation: pulse 1.2s infinite;
}

.count-text {
  font-weight: 700;
  color: var(--mh-muted);
}

.step-log {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--mh-muted);
  opacity: 0.7;
}

.log-entry.is-last {
  color: var(--mh-ink);
  font-weight: 600;
  opacity: 1;
}

.log-icon {
  font-size: 14px;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.36);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(124, 58, 237, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(124, 58, 237, 0);
  }
}
</style>
