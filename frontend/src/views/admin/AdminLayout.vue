<template>
  <AppShell :nav-items="adminNavItems" />
</template>

<script setup>
import AppShell from '@/components/AppShell.vue'
import { House, OfficeBuilding, Tickets, User, VideoCamera, Warning } from '@element-plus/icons-vue'

const adminNavItems = [
  { index: '/admin', label: '工作台', icon: House },
  { index: '/admin/video-analysis', label: '视频分析', icon: VideoCamera },
  { index: '/admin/warnings', label: '预警处置', icon: Warning },
  { index: '/admin/students', label: '学生档案', icon: User },
  { index: '/admin/classes', label: '班级管理', icon: OfficeBuilding },
  { index: '/admin/records', label: '识别记录', icon: Tickets },
]
</script>
