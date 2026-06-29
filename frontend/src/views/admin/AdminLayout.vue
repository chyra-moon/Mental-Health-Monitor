<template>
  <AppShell
    :nav-items="adminNavItems"
    section-label="心理中心工作台"
    headline="风险信号、学生档案和干预跟进"
    status-text="数据接入"
    user-fallback="系统管理员"
    side-label="今日关注"
    side-title="预警处置和跟进"
    side-description="优先查看高风险、超时未处理和近期波动学生。"
  />
</template>

<script setup>
import AppShell from '@/components/AppShell.vue'
import { House, OfficeBuilding, Tickets, User, VideoCamera, Warning } from '@element-plus/icons-vue'

const adminNavItems = [
  { index: '/admin', label: '风险工作台', icon: House },
  { index: '/admin/classes', label: '班级管理', icon: OfficeBuilding },
  { index: '/admin/warnings', label: '预警处置', icon: Warning },
  { index: '/admin/students', label: '学生档案', icon: User },
  { index: '/admin/records', label: '识别记录', icon: Tickets },
  { index: '/admin/video-analysis', label: '视频会话', icon: VideoCamera },
]
</script>
