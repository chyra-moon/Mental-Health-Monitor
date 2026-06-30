<template>
  <AppShell :nav-items="studentNavItems" />
</template>

<script setup>
import AppShell from '@/components/AppShell.vue'
import { Camera, DocumentChecked, House, Tickets, TrendCharts, User } from '@element-plus/icons-vue'

const studentNavItems = [
  { index: '/student', label: '心理工作台', icon: House },
  { index: '/student/emotion', label: '情绪识别', icon: Camera },
  { index: '/student/questionnaire', label: '心理测评', icon: DocumentChecked },
  { index: '/student/records', label: '识别记录', icon: Tickets },
  { index: '/student/trend', label: '趋势观察', icon: TrendCharts },
  { index: '/student/profile', label: '个人档案', icon: User },
]
</script>
