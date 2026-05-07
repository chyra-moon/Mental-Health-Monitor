<template>
  <svg
    class="app-logo"
    viewBox="0 0 220 56"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="logoBadgeGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#2f7df6" />
        <stop offset="100%" stop-color="#35c6e8" />
      </linearGradient>
      <linearGradient id="logoRingGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#2f7df6" stop-opacity="0.35" />
        <stop offset="100%" stop-color="#35c6e8" stop-opacity="0.12" />
      </linearGradient>
      <radialGradient id="logoGlow" cx="0.5" cy="0.45" r="0.5">
        <stop offset="0%" stop-color="#2f7df6" stop-opacity="0.18" />
        <stop offset="100%" stop-color="#2f7df6" stop-opacity="0" />
      </radialGradient>
    </defs>

    <!-- Glow behind badge -->
    <circle cx="26" cy="28" r="20" fill="url(#logoGlow)" />

    <!-- Outer ring -->
    <circle cx="26" cy="28" r="16.5" stroke="url(#logoRingGrad)" stroke-width="1.5" fill="none" />

    <!-- Badge background -->
    <circle cx="26" cy="28" r="14" fill="url(#logoBadgeGrad)" />

    <!-- IoT nodes: 4 sensor dots around the badge -->
    <circle cx="26" cy="6" r="2" fill="#35c6e8" opacity="0.7" />
    <circle cx="26" cy="6" r="4" fill="#35c6e8" opacity="0.15" />

    <circle cx="48" cy="22" r="2" fill="#2f7df6" opacity="0.6" />
    <circle cx="48" cy="22" r="4" fill="#2f7df6" opacity="0.12" />

    <circle cx="46" cy="38" r="2" fill="#35c6e8" opacity="0.55" />
    <circle cx="46" cy="38" r="4" fill="#35c6e8" opacity="0.1" />

    <circle cx="8" cy="16" r="1.8" fill="#2f7df6" opacity="0.65" />
    <circle cx="8" cy="16" r="3.6" fill="#2f7df6" opacity="0.13" />

    <!-- Connection arcs from nodes toward badge -->
    <path
      d="M 26 10 A 16 16 0 0 1 45 22"
      stroke="#35c6e8"
      stroke-width="0.6"
      stroke-dasharray="3 3"
      opacity="0.3"
      fill="none"
    />
    <path
      d="M 44 38 A 16 16 0 0 0 11 17"
      stroke="#2f7df6"
      stroke-width="0.6"
      stroke-dasharray="3 3"
      opacity="0.25"
      fill="none"
    />

    <!-- Pulse wave (ECG) inside badge -->
    <path
      d="M 13 28 L 19 28 L 21 28 L 23 22 L 25 22 L 27 34 L 29 28 L 35 28"
      stroke="#ffffff"
      stroke-width="2.2"
      stroke-linecap="round"
      stroke-linejoin="round"
      fill="none"
      opacity="0.95"
    />
    <!-- Glowing peak dot -->
    <circle cx="25" cy="22" r="2.8" fill="#ffffff" opacity="0.95" />
    <circle cx="25" cy="22" r="5" fill="#ffffff" opacity="0.12" />

    <!-- Text: subtitle -->
    <text x="54" y="22" fill="#8aa0c3" font-size="11" font-family="system-ui, -apple-system, sans-serif" font-weight="500" letter-spacing="0.8">
      基于物联网数据分析的
    </text>

    <!-- Text: main title -->
    <text x="54" y="42" fill="#17315f" font-size="15" font-family="system-ui, -apple-system, sans-serif" font-weight="700" letter-spacing="1.2">
      心理健康监测系统
    </text>

    <!-- Subtle underline accent -->
    <rect x="54" y="46" width="30" height="2" rx="1" fill="url(#logoBadgeGrad)" opacity="0.5" />
  </svg>
</template>

<script setup>
// No logic needed — pure visual component
</script>

<style scoped>
.app-logo {
  display: block;
  width: 210px;
  height: 56px;
  flex-shrink: 0;
}
</style>
