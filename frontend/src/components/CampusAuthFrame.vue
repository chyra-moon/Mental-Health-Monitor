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
  background-color: #f1f5f9; /* Simple clean light gray background */
  overflow-x: hidden;
  box-sizing: border-box;
}

.auth-mesh {
  display: none; /* Removed heavy background mesh pattern */
}

.auth-container {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 420px;
  gap: 24px;
  animation: fadeIn 0.4s ease-out forwards;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.brand-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--mh-primary);
  color: #ffffff;
}

.brand-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--mh-ink);
}

.auth-card {
  width: 100%;
  padding: 32px;
  background: #ffffff; /* Clean white card */
  border: 1px solid var(--mh-line);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
  box-sizing: border-box;
}

.card-header {
  margin-bottom: 24px;
  text-align: center;
}

.card-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--mh-ink);
}

.card-desc {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--mh-muted);
  line-height: 1.5;
}

.card-body :deep(.el-form-item__label) {
  color: var(--mh-text) !important;
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 4px;
}

.card-body :deep(.el-input__wrapper) {
  background: #ffffff !important;
  border: 1px solid var(--mh-line) !important;
  box-shadow: none !important;
}

.card-body :deep(.el-input__inner) {
  color: var(--mh-ink) !important;
  height: 40px;
}

.card-body :deep(.el-input__wrapper.is-focus) {
  border-color: var(--mh-primary) !important;
}

.card-body :deep(.el-button--primary) {
  background: var(--mh-primary) !important;
  border: none !important;
  height: 40px;
  border-radius: var(--mh-radius-md) !important;
  font-weight: 700;
  box-shadow: none;
  width: 100%;
}

.card-body :deep(.el-button--primary:hover) {
  background: var(--mh-primary-strong) !important;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
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
