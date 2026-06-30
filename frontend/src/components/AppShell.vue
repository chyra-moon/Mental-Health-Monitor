<template>
  <div class="shell-container">
    <!-- Layer 1: Top Bar (Slim height, premium branding & user profile) -->
    <header class="shell-header">
      <div class="header-left">
        <AppLogo />
        <span class="system-title">基于物联网数据分析的心理健康监测系统</span>
      </div>
      <div class="header-right">
        <div class="user-profile">
          <el-avatar :size="28" class="user-avatar">{{ avatarInitial }}</el-avatar>
          <span class="user-name">{{ userDisplayName }}</span>
          <span class="role-badge">{{ userRoleLabel }}</span>
        </div>
        <el-button type="danger" size="default" class="logout-btn" @click="handleLogout">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="logout-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </el-button>
      </div>
    </header>

    <!-- Layer 2: Nav Bar (Slim horizontal menu) -->
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

    <!-- Layer 3: Main Page Content Container (100% remaining space, scrolls internally) -->
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
  return user.value.role === 'admin' ? '系统管理员' : '在校学生'
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
  height: 100vh;
  overflow: hidden;
  background-color: var(--mh-bg);
}

/* Layer 1: Slim Header */
.shell-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 20px;
  background-color: #0f172a; /* Slate 900 for premium branding bar */
  color: #ffffff;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-title {
  font-size: 15px;
  font-weight: 750;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  font-weight: 700;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #f1f5f9;
}

.role-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 650;
  background: rgba(239, 68, 68, 0.12) !important;
  border: 1px solid rgba(239, 68, 68, 0.25) !important;
  color: #f87171 !important;
  border-radius: 6px !important;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2) !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  color: #ef4444 !important;
}

.logout-icon {
  transition: transform 0.2s ease;
}

.logout-btn:hover .logout-icon {
  transform: translateX(2px);
}

/* Layer 2: Slim Nav Bar */
.shell-nav {
  display: flex;
  align-items: center;
  height: 42px;
  padding: 0 20px;
  background-color: #ffffff;
  border-bottom: 1px solid var(--mh-line);
  z-index: 9;
}

.nav-links {
  display: flex;
  height: 100%;
  gap: 4px;
}

.nav-link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
  padding: 0 16px;
  text-decoration: none;
  color: var(--mh-muted);
  font-size: 13px;
  font-weight: 650;
  border-bottom: 2px solid transparent;
  transition: all 0.18s ease;
}

.nav-link-item:hover {
  color: var(--mh-primary);
  background-color: rgba(99, 102, 241, 0.03);
}

.nav-link-item.is-active {
  color: var(--mh-primary);
  border-bottom-color: var(--mh-primary);
  font-weight: 750;
}

.nav-icon {
  font-size: 16px;
}

/* Layer 3: Main Scroll Area */
.shell-main {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 16px;
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
</style>
