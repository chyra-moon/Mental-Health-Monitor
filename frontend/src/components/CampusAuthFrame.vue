<template>
  <main class="auth-shell">
    <section class="auth-aside" aria-label="系统信息">
      <div class="brand-mark">
        <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.3">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 17h6l3-8 4 14 3-7h4" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 8h20M6 25h16" />
        </svg>
      </div>
      <div class="brand-copy">
        <p class="brand-kicker">Mental Health Monitor</p>
        <h1 class="brand-title">{{ title }}</h1>
        <p v-if="description" class="brand-desc">{{ description }}</p>
      </div>
      <div class="aside-footer">
        <span>学生端</span>
        <span>管理端</span>
        <span>风险跟进</span>
      </div>
    </section>

    <section class="auth-panel" :aria-labelledby="formTitleId">
      <div class="auth-card">
        <div class="card-header">
          <h2 :id="formTitleId" class="card-title">{{ formTitle }}</h2>
          <p v-if="formDescription" class="card-desc">{{ formDescription }}</p>
        </div>
        <slot></slot>
      </div>
    </section>
  </main>
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
.auth-shell {
  display: grid;
  grid-template-columns: minmax(420px, 1.05fr) minmax(420px, 0.95fr);
  width: 100vw;
  min-height: 100dvh;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0)),
    var(--mh-bg);
  box-sizing: border-box;
}

.auth-aside {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(40px, 6vw, 76px);
  border-right: 1px solid var(--mh-line);
  background:
    linear-gradient(180deg, #ffffff 0%, #fafafa 54%, #f4f4f5 100%);
  overflow: hidden;
}

.auth-aside::after {
  content: "";
  position: absolute;
  inset: auto -18% -18% auto;
  width: 56%;
  aspect-ratio: 1;
  border: 1px solid var(--mh-line);
  border-radius: 50%;
  opacity: 0.7;
}

.brand-mark {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid var(--mh-line);
  border-radius: 12px;
  background: var(--mh-surface);
  color: var(--mh-ink);
}

.brand-copy {
  max-width: 520px;
  margin-top: auto;
  margin-bottom: auto;
}

.brand-kicker {
  margin: 0 0 14px;
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 750;
  text-transform: uppercase;
}

.brand-title {
  margin: 0;
  color: var(--mh-ink);
  font-size: clamp(34px, 4vw, 56px);
  line-height: 1.08;
  font-weight: 800;
  letter-spacing: 0;
}

.brand-desc {
  max-width: 420px;
  margin: 18px 0 0;
  color: var(--mh-muted);
  font-size: 15px;
  line-height: 1.8;
}

.aside-footer {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.aside-footer span {
  padding: 7px 10px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: rgba(255, 255, 255, 0.72);
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 650;
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(28px, 5vw, 72px);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 36px;
  background: #ffffff;
  border: 1px solid var(--mh-line);
  border-radius: 10px;
  box-shadow: var(--mh-shadow);
  box-sizing: border-box;
}

.card-header {
  margin-bottom: 26px;
  text-align: left;
}

.card-title {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: var(--mh-ink);
}

.card-desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--mh-muted);
  line-height: 1.7;
}

:deep(.el-form-item__label) {
  color: var(--mh-text) !important;
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 4px;
}

:deep(.el-input__wrapper) {
  background: #ffffff !important;
  border: 1px solid var(--mh-line) !important;
  box-shadow: none !important;
}

:deep(.el-input__inner) {
  color: var(--mh-ink) !important;
  height: 42px;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--mh-primary) !important;
}

:deep(.el-button--primary) {
  background: var(--mh-primary) !important;
  border: none !important;
  height: 42px;
  border-radius: var(--mh-radius-md) !important;
  font-weight: 700;
  box-shadow: none;
  width: 100%;
}

:deep(.el-button--primary:hover) {
  background: var(--mh-primary-strong) !important;
}

@media (max-width: 920px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-aside {
    min-height: 230px;
    padding: 28px;
  }

  .brand-copy {
    margin: 28px 0;
  }

  .auth-panel {
    align-items: flex-start;
    padding: 24px;
  }
}

@media (max-width: 520px) {
  .brand-title {
    font-size: 30px;
  }

  .auth-card {
    padding: 24px;
  }
}
</style>
