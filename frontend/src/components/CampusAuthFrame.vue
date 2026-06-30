<template>
  <div class="auth-wrapper">
    <div class="auth-mesh"></div>
    <div class="auth-container">
      <div class="auth-brand">
        <div class="brand-logo">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h1 class="brand-title">{{ title }}</h1>
      </div>
      
      <div class="auth-card">
        <div class="card-header">
          <h2 :id="formTitleId" class="card-title">{{ formTitle }}</h2>
          <p class="card-desc">{{ formDescription }}</p>
        </div>
        <div class="card-body">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  mode: {
    type: String,
    default: 'login'
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  formTitle: {
    type: String,
    required: true
  },
  formDescription: {
    type: String,
    default: ''
  },
  formTitleId: {
    type: String,
    default: 'auth-form-title'
  },
  contextItems: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.auth-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  min-height: 100vh;
  padding: 24px;
  background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
              linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  overflow-x: hidden;
  box-sizing: border-box;
}

.auth-mesh {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 32px 32px;
  opacity: 0.8;
  pointer-events: none;
  z-index: 1;
}

.auth-container {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 440px;
  gap: 32px;
  animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.auth-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.brand-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1, #8b95f6);
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
}

.brand-title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 0.02em;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.auth-card {
  width: 100%;
  padding: 40px;
  background: rgba(30, 41, 59, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  box-sizing: border-box;
}

.card-header {
  margin-bottom: 28px;
  text-align: center;
}

.card-title {
  margin: 0;
  font-size: 24px;
  font-weight: 750;
  color: #ffffff;
}

.card-desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.5;
}

.card-body :deep(.el-form-item__label) {
  color: #94a3b8 !important;
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 6px;
}

.card-body :deep(.el-input__wrapper) {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
}

.card-body :deep(.el-input__inner) {
  color: #ffffff !important;
  height: 42px;
}

.card-body :deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1 !important;
}

.card-body :deep(.el-button--primary) {
  background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
  border: none !important;
  height: 44px;
  border-radius: 12px !important;
  font-weight: 700;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.25);
  transition: all 0.2s ease;
}

.card-body :deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(99, 102, 241, 0.35);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 24px;
  }
}
</style>
