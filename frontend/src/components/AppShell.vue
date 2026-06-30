<template>
  <div class="shell-container">
    <header class="shell-header">
      <div class="header-left">
        <div class="user-profile">
          <el-avatar :size="28" class="user-avatar">{{ avatarInitial }}</el-avatar>
          <span class="user-name">{{ userDisplayName }}</span>
          <span class="role-badge">{{ userRoleLabel }}</span>
        </div>
      </div>
      <div class="header-center">
        <AppLogo />
      </div>
      <div class="header-right">
        <el-button type="danger" size="default" class="logout-btn" @click="handleLogout">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="logout-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </el-button>
      </div>
    </header>

    <nav class="shell-nav">
      <div class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.index"
          :to="item.index"
          class="nav-link-item"
          :class="{ 'is-active': isLinkActive(item.index) }"
        >
          <el-icon v-if="item.icon" class="nav-icon"><component :is="item.icon" /></el-icon>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <main class="shell-main">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLogo from './AppLogo.vue'
import { useUserStore } from '@/stores/user'

defineProps({
  navItems: {
    type: Array,
    required: true
  },
  sectionLabel: String,
  headline: String,
  statusText: String,
  userFallback: String,
  sideLabel: String,
  sideTitle: String,
  sideDescription: String
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user || {})

const userDisplayName = computed(() => {
  return user.value.real_name || user.value.username || '用户'
})

const avatarInitial = computed(() => {
  const name = userDisplayName.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const userRoleLabel = computed(() => {
  return user.value.role === 'admin' ? '系统管理员' : '学生'
})

const isLinkActive = (path) => {
  if (path === '/student') {
    return route.path === '/student'
  }
  if (path === '/admin') {
    return route.path === '/admin'
  }
  return route.path.startsWith(path)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.shell-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100dvh;
  overflow: hidden;
  background-color: var(--mh-bg);
}

.shell-header {
  display: grid;
  grid-template-columns: minmax(200px, 1fr) auto minmax(200px, 1fr);
  align-items: center;
  height: 56px;
  padding: 0 20px;
  background-color: var(--mh-surface);
  color: var(--mh-ink);
  z-index: 10;
  border-bottom: 1px solid var(--mh-line);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.header-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 0;
  justify-self: center;
}

.header-center :deep(.app-logo) {
  max-width: min(620px, 54vw);
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: var(--mh-primary);
  font-weight: 700;
  color: #ffffff;
  border: 1px solid var(--mh-line);
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--mh-text);
}

.role-badge {
  font-size: 11px;
  padding: 3px 7px;
  border-radius: 4px;
  background: var(--mh-primary-soft);
  color: var(--mh-muted);
  border: 1px solid var(--mh-line);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 96px;
  height: 34px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 650;
  background: var(--mh-danger) !important;
  border: 1px solid var(--mh-danger) !important;
  color: #ffffff !important;
  border-radius: 6px !important;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #b91c1c !important;
  border-color: #b91c1c !important;
  color: #ffffff !important;
}

.logout-icon {
  transition: transform 0.2s ease;
}

.logout-btn:hover .logout-icon {
  transform: translateX(2px);
}

.shell-nav {
  display: flex;
  align-items: center;
  height: 44px;
  padding: 0 18px;
  background-color: #ffffff;
  border-bottom: 1px solid var(--mh-line);
  z-index: 9;
  overflow-x: auto;
  overflow-y: hidden;
}

.nav-links {
  display: flex;
  height: 100%;
  gap: 2px;
  min-width: max-content;
}

.nav-link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
  padding: 0 16px;
  text-decoration: none;
  color: var(--mh-muted);
  font-size: 14px;
  font-weight: 700;
  border-bottom: 2px solid transparent;
  transition: all 0.18s ease;
}

.nav-link-item:hover {
  color: var(--mh-ink);
  background-color: var(--mh-primary-soft);
}

.nav-link-item.is-active {
  color: var(--mh-ink);
  border-bottom-color: var(--mh-accent);
  font-weight: 750;
}

.nav-icon {
  font-size: 18px;
}

.shell-main {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 12px;
  box-sizing: border-box;
}

.content-wrapper {
  width: 100%;
  min-height: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Transitions */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.2s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 760px) {
  .shell-header {
    grid-template-columns: auto minmax(0, 1fr) auto;
    height: auto;
    min-height: 48px;
    gap: 8px;
    padding: 8px 12px;
  }

  .role-badge {
    display: none;
  }

  .header-center :deep(.app-logo) {
    max-width: 58vw;
  }

  .header-right {
    gap: 8px;
  }

  .user-name {
    display: none;
  }

  .shell-nav {
    padding: 0 10px;
  }

  .shell-main {
    padding: 10px;
  }
}
</style>
