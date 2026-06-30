<template>
  <el-card class="capture-panel-card" shadow="never">
    <div class="camera-stage">
      <div class="hud-overlay">
        <div class="hud-center">
          <div class="camera-status-text">摄像头开启中...</div>
        </div>
      </div>
      
      <video
        ref="videoElement"
        class="underlay-video"
        autoplay
        playsinline
        muted
        @loadedmetadata="$emit('video-meta', $event)"
        @ended="$emit('video-ended', $event)"
      ></video>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['video-element', 'video-meta', 'video-ended'])

const videoElement = ref(null)

onMounted(() => {
  if (videoElement.value) {
    emit('video-element', videoElement.value)
  }
})
</script>

<style scoped>
.capture-panel-card {
  border: none !important;
  background: var(--mh-surface) !important;
  height: 100%;
}

.capture-panel-card :deep(.el-card__body) {
  height: 100%;
}

.camera-stage {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  height: 100%;
  min-height: 286px;
  background-color: #111113;
  border-radius: var(--mh-radius-md);
  overflow: hidden;
  border: 1px solid var(--mh-line);
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.64);
}

.underlay-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.24;
  filter: contrast(1.06) brightness(0.84) grayscale(0.2);
}

.hud-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 16px;
  pointer-events: none;
  z-index: 2;
}

.hud-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.camera-status-text {
  font-size: 16px;
  font-weight: 700;
  color: #f4f4f5;
  letter-spacing: 0;
  text-shadow: 0 1px 18px rgba(255, 255, 255, 0.12);
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
