<template>
  <AppShell
    :nav-items="studentNavItems"
    section-label="学生自助工作台"
    headline="记录个人状态，完成测评并查看关注建议"
    status-text="资料同步"
    user-fallback="学生"
    side-label="自助关注"
    side-title="识别和测评结合查看"
    side-description="结果用于校内支持参考，不替代专业评估。"
  />
</template>

<script setup>
import AppShell from '@/components/AppShell.vue'
import { Camera, DocumentChecked, House, Tickets, TrendCharts, User } from '@element-plus/icons-vue'

const studentNavItems = [
  { index: '/student', label: '心理工作台', icon: House },
  { index: '/student/emotion', label: '情绪识别', icon: Camera },
  { index: '/student/questionnaire', label: '心理测评', icon: DocumentChecked },
  { index: '/student/trend', label: '趋势观察', icon: TrendCharts },
  { index: '/student/records', label: '识别记录', icon: Tickets },
  { index: '/student/profile', label: '个人档案', icon: User },
]
</script>
