<template>
  <el-card class="capture-panel-card" shadow="never">
    <div class="camera-stage">
      <!-- Camera HUD VIEWPORT -->
      <div class="hud-overlay">
        <div class="hud-top">
          <div class="rec-indicator">
            <span class="red-dot"></span>
            <span>REC 60FPS</span>
          </div>
          <div class="cam-label">CAM-01</div>
        </div>
        
        <div class="hud-center">
          <div class="focus-reticle"></div>
          <div class="camera-status-text">摄像头开启中...</div>
        </div>
        
        <div class="hud-bottom">
          <div class="hud-time">{{ formattedTime }}</div>
          <div class="hud-mode">FACE_AUTO_DETECT</div>
        </div>
      </div>
      
      <!-- Underlay Video element for frame processing -->
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
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['video-element', 'video-meta', 'video-ended'])

const videoElement = ref(null)
const formattedTime = ref('')

let timeInterval = null

function updateHUDTime() {
  const now = new Date()
  const hh = String(now.getHours()).padStart(2, '0')
  const mm = String(now.getMinutes()).padStart(2, '0')
  const ss = String(now.getSeconds()).padStart(2, '0')
  formattedTime.value = `${hh}:${mm}:${ss}`
}

onMounted(() => {
  if (videoElement.value) {
    emit('video-element', videoElement.value)
  }
  updateHUDTime()
  timeInterval = setInterval(updateHUDTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.capture-panel-card {
  border: none !important;
  background: transparent !important;
}

.camera-stage {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #020617; /* Very dark slate */
  border-radius: var(--mh-radius-lg);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.8);
}

.underlay-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.35; /* Blended with the dark background to look like a low-light security/counseling camera */
  filter: contrast(1.1) brightness(0.9) grayscale(0.2);
}

/* Camera HUD Overlay */
.hud-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  pointer-events: none;
  z-index: 2;
  font-family: monospace;
}

.hud-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ef4444;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 1px;
}

.rec-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.red-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ef4444;
  animation: blink 1s infinite alternate;
}

.cam-label {
  color: rgba(255, 255, 255, 0.6);
}

.hud-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex: 1;
}

.focus-reticle {
  position: relative;
  width: 48px;
  height: 48px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
}

.focus-reticle::before,
.focus-reticle::after {
  content: '';
  position: absolute;
  background-color: rgba(255, 255, 255, 0.3);
}

.focus-reticle::before {
  top: 50%;
  left: -8px;
  right: -8px;
  height: 2px;
  transform: translateY(-50%);
}

.focus-reticle::after {
  left: 50%;
  top: -8px;
  bottom: -8px;
  width: 2px;
  transform: translateX(-50%);
}

.camera-status-text {
  font-size: 16px;
  font-weight: 700;
  color: #38bdf8; /* Sky blue */
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
  animation: pulse 2s infinite ease-in-out;
}

.hud-bottom {
  display: flex;
  justify-content: space-between;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  letter-spacing: 0.5px;
}

@keyframes blink {
  0% { opacity: 0.1; }
  100% { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
