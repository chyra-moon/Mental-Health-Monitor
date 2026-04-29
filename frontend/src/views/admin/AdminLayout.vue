<template>
  <el-container class="layout-shell">
    <el-aside width="248px" class="aside-panel">
      <div class="brand">
        <div class="brand-badge">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="brand-text">
          <strong>心理健康监测系统</strong>
          <span>IoT Mental Monitor</span>
        </div>
      </div>

      <el-menu class="side-menu" :default-active="route.path" router>
        <el-menu-item index="/admin">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/admin/classes">
          <el-icon><OfficeBuilding /></el-icon>
          <span>班级列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/warnings">
          <el-icon><Warning /></el-icon>
          <span>风险预警</span>
        </el-menu-item>
        <el-menu-item index="/admin/students">
          <el-icon><User /></el-icon>
          <span>学生列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/records">
          <el-icon><Tickets /></el-icon>
          <span>识别记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/video-analysis">
          <el-icon><VideoCamera /></el-icon>
          <span>视频分析</span>
        </el-menu-item>
      </el-menu>

      <div class="side-card">
        <span>System Online</span>
        <strong>校园心理监测中枢</strong>
        <p>感知数据 · 风险研判 · 预警干预</p>
      </div>
    </el-aside>

    <el-container class="workspace">
      <el-header class="topbar">
        <div class="topbar-left">
          <span>管理员工作台</span>
          <strong>基于物联网的学生心理监测系统</strong>
        </div>
        <div class="topbar-right">
          <div class="status-pill">
            <i></i>
            <span>设备在线</span>
          </div>
          <div class="user-chip">{{ user?.real_name || user?.username || '系统管理员' }}</div>
          <el-button type="danger" size="small" :icon="SwitchButton" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main-surface">
        <div class="content-shell">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import {
  Connection,
  House,
  OfficeBuilding,
  SwitchButton,
  Tickets,
  User,
  VideoCamera,
  Warning
} from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

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
.layout-shell {
  min-height: 100vh;
  padding: 18px;
  gap: 18px;
  background: linear-gradient(135deg, #f6fbff 0%, #edf6ff 52%, #f8fcff 100%);
}

.aside-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 18px 14px;
  border: 1px solid rgba(105, 150, 215, 0.16);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 12px 28px rgba(59, 100, 164, 0.08);
}

.aside-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(140deg, rgba(47, 125, 246, 0.1), transparent 34%),
    radial-gradient(circle at 50% 98%, rgba(53, 198, 232, 0.15), transparent 34%);
}

.brand,
.side-menu,
.side-card {
  position: relative;
  z-index: 1;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 8px 18px;
}

.brand-badge {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 14px;
  color: #ffffff;
  background: linear-gradient(135deg, #2f7df6, #35c6e8);
  box-shadow: 0 8px 18px rgba(47, 125, 246, 0.18);
}

.brand-text {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.brand-text strong {
  color: #17315f;
  font-size: 15px;
  line-height: 1.35;
}

.brand-text span {
  margin-top: 3px;
  color: #8aa0c3;
  font-size: 11px;
  letter-spacing: 0.2px;
}

.side-menu {
  flex: 1;
  border-right: none;
  background: transparent;
}

:deep(.side-menu.el-menu) {
  border-right: none;
  background: transparent;
}

:deep(.side-menu .el-menu-item) {
  height: 44px;
  margin: 7px 0;
  border-radius: 13px;
  color: #5d7198;
  font-weight: 700;
  letter-spacing: 0;
}

:deep(.side-menu .el-menu-item:hover) {
  color: #1d64e8;
  background: rgba(234, 243, 255, 0.86);
}

:deep(.side-menu .el-menu-item.is-active) {
  color: #145ee8;
  background: linear-gradient(90deg, rgba(47, 125, 246, 0.16), rgba(53, 198, 232, 0.1));
  box-shadow: inset 3px 0 0 #2f7df6;
}

:deep(.side-menu .el-icon) {
  width: 20px;
  margin-right: 10px;
  font-size: 18px;
}

.side-card {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid rgba(91, 143, 220, 0.16);
  border-radius: 18px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(232, 244, 255, 0.82)),
    radial-gradient(circle at 18% 16%, rgba(53, 198, 232, 0.22), transparent 28%);
  box-shadow: 0 8px 18px rgba(71, 111, 176, 0.08);
}

.side-card span {
  display: block;
  color: #2f7df6;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.side-card strong {
  display: block;
  margin-top: 8px;
  color: #17315f;
  font-size: 14px;
}

.side-card p {
  margin: 7px 0 0;
  color: #7d8fb3;
  font-size: 12px;
  line-height: 1.7;
}

.workspace {
  min-width: 0;
}

.topbar {
  display: flex;
  height: 72px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 22px;
  border: 1px solid rgba(105, 150, 215, 0.14);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 10px 24px rgba(61, 102, 166, 0.08);
}

.topbar-left {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
}

.topbar-left span {
  color: #7d8fb3;
  font-size: 12px;
  font-weight: 700;
}

.topbar-left strong {
  overflow: hidden;
  color: #17315f;
  font-size: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-pill,
.user-chip {
  display: inline-flex;
  height: 34px;
  align-items: center;
  border: 1px solid rgba(105, 150, 215, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #5d7198;
  font-size: 13px;
  font-weight: 700;
}

.status-pill {
  gap: 8px;
  padding: 0 13px;
}

.status-pill i {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #37d5a7;
  box-shadow: 0 0 0 5px rgba(55, 213, 167, 0.14);
}

.user-chip {
  max-width: 180px;
  overflow: hidden;
  padding: 0 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main-surface {
  padding: 18px 0 0;
  overflow: auto;
}

.content-shell {
  min-height: calc(100vh - 126px);
  padding: 22px;
  border: 1px solid rgba(105, 150, 215, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.68);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.74);
}

@media (max-width: 980px) {
  .layout-shell {
    flex-direction: column;
    padding: 12px;
  }

  .aside-panel {
    width: 100% !important;
  }

  .topbar {
    height: auto;
    flex-wrap: wrap;
    padding: 14px;
  }

  .topbar-right {
    flex-wrap: wrap;
  }
}
</style>
