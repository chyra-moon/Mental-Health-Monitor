<template>
  <el-container class="layout">
    <el-aside width="220px">
      <div class="logo">管理后台</div>
      <el-menu :default-active="route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff">
        <el-menu-item index="/admin">
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/admin/warnings">
          <span>风险预警</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>{{ user?.real_name || user?.username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

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
.layout { height: 100vh; }
.el-aside { background-color: #304156; overflow: hidden; }
.logo { height: 60px; line-height: 60px; text-align: center; color: #fff; font-size: 16px; font-weight: bold; }
.el-header { background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: flex-end; gap: 12px; }
.el-main { background: #f0f2f5; }
</style>
