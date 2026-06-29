<template>
  <el-container class="campus-shell" :class="`variant-${variant}`">
    <el-aside width="252px" class="campus-aside">
      <div class="shell-brand">
        <AppLogo />
      </div>

      <el-menu class="shell-menu" :default-active="route.path" router>
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>

      <section class="aside-note">
        <span>{{ noteLabel }}</span>
        <strong>{{ noteTitle }}</strong>
        <p>{{ noteText }}</p>
      </section>
    </el-aside>

    <el-container class="campus-workspace">
      <el-header class="campus-topbar">
        <div class="topbar-title">
          <span>{{ roleLabel }}</span>
          <strong>{{ title }}</strong>
        </div>
        <div class="topbar-actions">
          <div class="sync-pill">
            <i></i>
            <span>{{ statusText }}</span>
          </div>
          <div class="user-chip">{{ user?.real_name || user?.username || userFallback }}</div>
          <el-button type="danger" size="small" :icon="SwitchButton" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-main class="campus-main">
        <div class="campus-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppLogo from '@/components/AppLogo.vue'
import { SwitchButton } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

defineProps({
  variant: { type: String, default: 'student' },
  title: { type: String, default: '基于物联网数据分析的心理健康监测系统' },
  roleLabel: { type: String, default: '工作台' },
  statusText: { type: String, default: '数据同步' },
  userFallback: { type: String, default: '用户' },
  noteLabel: { type: String, default: 'Campus Care' },
  noteTitle: { type: String, default: '心理健康服务' },
  noteText: { type: String, default: '识别、记录、趋势与预警保持同一业务流程。' },
  menuItems: { type: Array, required: true },
})

const router = useRouter()
const route = useRoute()
const user = JSON.parse(localStorage.getItem('user') || '{}')

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.campus-shell {
  min-height: 100vh;
  padding: 16px;
  gap: 16px;
  background:
    linear-gradient(90deg, rgba(20, 118, 109, 0.04) 1px, transparent 1px),
    linear-gradient(0deg, rgba(20, 118, 109, 0.04) 1px, transparent 1px),
    linear-gradient(135deg, #f6faf5 0%, #edf6f1 52%, #f8faf4 100%);
  background-size: 42px 42px, 42px 42px, auto;
}

.variant-admin {
  background:
    linear-gradient(90deg, rgba(51, 127, 149, 0.045) 1px, transparent 1px),
    linear-gradient(0deg, rgba(51, 127, 149, 0.04) 1px, transparent 1px),
    linear-gradient(135deg, #f5f8f7 0%, #eef5f4 52%, #faf8f3 100%);
  background-size: 42px 42px, 42px 42px, auto;
}

.campus-aside {
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  border: 1px solid var(--mh-line-strong);
  border-radius: var(--mh-radius-lg);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--mh-shadow);
}

.shell-brand {
  padding: 4px 6px 18px;
}

.shell-menu {
  flex: 1;
  border-right: none;
  background: transparent;
}

:deep(.shell-menu.el-menu) {
  border-right: none;
  background: transparent;
}

:deep(.shell-menu .el-menu-item) {
  height: 44px;
  margin: 6px 0;
  border-radius: var(--mh-radius);
  color: var(--mh-text);
  font-weight: 720;
  letter-spacing: 0;
}

:deep(.shell-menu .el-menu-item:hover) {
  background: var(--mh-primary-soft);
  color: var(--mh-primary-dark);
}

:deep(.shell-menu .el-menu-item.is-active) {
  background: #dcefe9;
  color: var(--mh-primary-dark);
  box-shadow: inset 4px 0 0 var(--mh-primary);
}

.variant-admin :deep(.shell-menu .el-menu-item:hover) {
  background: var(--mh-info-soft);
  color: var(--mh-sky);
}

.variant-admin :deep(.shell-menu .el-menu-item.is-active) {
  background: #e2eff2;
  color: var(--mh-sky);
  box-shadow: inset 4px 0 0 var(--mh-sky);
}

:deep(.shell-menu .el-icon) {
  width: 20px;
  margin-right: 10px;
  font-size: 17px;
}

.aside-note {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background:
    linear-gradient(180deg, rgba(225, 242, 238, 0.84), rgba(255, 255, 255, 0.92));
}

.variant-admin .aside-note {
  background:
    linear-gradient(180deg, rgba(232, 240, 243, 0.9), rgba(255, 255, 255, 0.94));
}

.aside-note span {
  color: var(--mh-warm);
  font-size: 11px;
  font-weight: 820;
}

.aside-note strong {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 15px;
}

.aside-note p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.7;
}

.campus-workspace {
  min-width: 0;
}

.campus-topbar {
  height: auto;
  min-height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--mh-space-4);
  padding: 12px 18px;
  border: 1px solid var(--mh-line-strong);
  border-radius: var(--mh-radius-lg);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--mh-shadow-soft);
}

.topbar-title {
  min-width: 0;
}

.topbar-title span {
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 760;
}

.topbar-title strong {
  display: block;
  max-width: min(62vw, 820px);
  overflow: hidden;
  margin-top: 4px;
  color: var(--mh-ink);
  font-size: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.sync-pill,
.user-chip {
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--mh-line);
  border-radius: 999px;
  background: var(--mh-surface-soft);
  color: var(--mh-text);
  font-size: 13px;
  font-weight: 720;
}

.sync-pill {
  gap: 8px;
  padding: 0 12px;
}

.sync-pill i {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--mh-green);
}

.user-chip {
  max-width: 180px;
  overflow: hidden;
  padding: 0 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.campus-main {
  padding: 16px 0 0;
  overflow: auto;
}

.campus-content {
  min-height: calc(100vh - 116px);
  padding: 22px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-lg);
  background: rgba(255, 255, 255, 0.66);
}

@media (max-width: 980px) {
  .campus-shell {
    flex-direction: column;
    padding: 10px;
  }

  .campus-aside {
    width: 100% !important;
  }

  .shell-menu {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
  }

  :deep(.shell-menu .el-menu-item) {
    margin: 0;
  }

  .aside-note {
    display: none;
  }

  .topbar-title strong {
    max-width: 100%;
    white-space: normal;
  }
}

@media (max-width: 640px) {
  .shell-menu {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .campus-topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .topbar-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .campus-content {
    padding: 16px 12px;
  }
}
</style>
