<template>
  <CampusLayout
    variant="admin"
    role-label="教师管理台"
    title="基于物联网数据分析的心理健康监测系统"
    status-text="服务在线"
    user-fallback="系统管理员"
    note-label="Admin Desk"
    note-title="风险研判工作区"
    note-text="围绕班级、学生、预警、记录和视频分析组织日常管理。"
    :menu-items="menuItems"
  />
</template>

<script setup>
import CampusLayout from '@/components/layout/CampusLayout.vue'
import {
  House,
  OfficeBuilding,
  Tickets,
  User,
  VideoCamera,
  Warning
} from '@element-plus/icons-vue'

const menuItems = [
  { index: '/admin', label: '管理首页', icon: House },
  { index: '/admin/classes', label: '班级管理', icon: OfficeBuilding },
  { index: '/admin/warnings', label: '预警管理', icon: Warning },
  { index: '/admin/students', label: '学生管理', icon: User },
  { index: '/admin/records', label: '记录管理', icon: Tickets },
  { index: '/admin/video-analysis', label: '视频分析', icon: VideoCamera },
]
</script>
