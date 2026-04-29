<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">管理后台</div>
      <el-menu
        class="menu"
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#c0c8d2"
        active-text-color="#409eff"
      >
        <el-menu-item index="/admin">
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/admin/classes">
          <span>班级列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/warnings">
          <span>风险预警</span>
        </el-menu-item>
        <el-menu-item index="/admin/students">
          <span>学生列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/records">
          <span>识别记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/video-analysis">
          <span>视频分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">管理员端</div>
        <div class="header-right">
          <span class="user-name">{{ user?.real_name || user?.username || '系统管理员' }}</span>
          <el-button type="danger" size="small" :icon="SwitchButton" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { SwitchButton } from '@element-plus/icons-vue'
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
.layout {
  height: 100vh;
}

.aside {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0;
}

.menu {
  border-right: none;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-title {
  font-size: 14px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: #303133;
}

.main {
  background: #f5f7fa;
}
</style>
