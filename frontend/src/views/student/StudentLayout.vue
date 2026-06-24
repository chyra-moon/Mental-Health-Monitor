<template>
  <CampusLayout
    variant="student"
    role-label="学生服务台"
    title="基于物联网数据分析的心理健康监测系统"
    status-text="个人数据同步"
    user-fallback="学生"
    note-label="Student Care"
    note-title="我的心理状态追踪"
    note-text="从情绪识别到记录和趋势，帮助你看见近期状态变化。"
    :menu-items="menuItems"
  />
</template>

<script setup>
import CampusLayout from '@/components/layout/CampusLayout.vue'
import { Camera, House, Tickets, TrendCharts, User } from '@element-plus/icons-vue'

const menuItems = [
  { index: '/student', label: '学生首页', icon: House },
  { index: '/student/profile', label: '个人资料', icon: User },
  { index: '/student/emotion', label: '情绪检测', icon: Camera },
  { index: '/student/records', label: '检测记录', icon: Tickets },
  { index: '/student/trend', label: '趋势分析', icon: TrendCharts },
]
</script>
