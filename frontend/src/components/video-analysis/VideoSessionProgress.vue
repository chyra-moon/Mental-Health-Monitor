<template>
  <div v-if="phase === 'running'" class="progress-container">
    <div class="progress-header">
      <span class="status-badge">
        <span class="pulse-dot"></span>
        正在分析人脸帧表情数据...
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
    list.push('初始化视频抽帧解码器成功')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.25)) {
    list.push('成功加载 MTCNN 人脸网格追踪模型')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.5)) {
    list.push('面部细微肌肉动作编码提取 (AUs) 完成')
  }
  if (props.completedFrameCount >= Math.floor(props.frameCount * 0.75)) {
    list.push('负向情绪权重与概率融合分析中')
  }
  if (props.completedFrameCount === props.frameCount) {
    list.push('抽帧会话序列结束，正在生成心理评估报告')
  }
  
  // 只返回最后两条日志，保持简洁
  return list.slice(-2)
})
</script>

<style scoped>
.progress-container {
  padding: 16px;
  background: rgba(15, 23, 42, 0.03);
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
  box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
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
  color: var(--mh-primary);
  font-weight: 600;
  opacity: 1;
}

.log-icon {
  font-size: 14px;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(99, 102, 241, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
}
</style>
