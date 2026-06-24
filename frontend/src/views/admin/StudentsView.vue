<template>
  <div class="page students-page">
    <PageHeader
      eyebrow="学生管理"
      title="学生列表"
      description="查看已注册学生账号、班级归属和基础状态。"
      tone="admin"
    >
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadStudents" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <div class="stats-grid three">
      <MetricCard label="学生总数" :value="students.length" unit="人" caption="当前列表中的学生账号" accent="sky" />
      <MetricCard label="资料已完善" :value="profileCompletedCount" unit="人" caption="已填写姓名、性别和班级" accent="green" />
      <MetricCard label="禁用账号" :value="disabledCount" unit="个" caption="状态非正常的学生账号" accent="danger" />
    </div>

    <section class="table-panel">
      <div class="panel-title-row">
        <div>
          <h2>学生数据</h2>
          <p>用于管理端查看学生基础信息</p>
        </div>
      </div>

      <el-empty v-if="!loading && students.length === 0" description="暂无学生数据" />
      <div v-else class="table-scroll">
        <el-table v-loading="loading" :data="students" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" min-width="140" />
          <el-table-column prop="real_name" label="姓名" min-width="120">
            <template #default="{ row }">{{ row.real_name || '-' }}</template>
          </el-table-column>
          <el-table-column prop="gender" label="性别" min-width="100">
            <template #default="{ row }">{{ row.gender || '-' }}</template>
          </el-table-column>
          <el-table-column prop="class_name" label="班级" min-width="140">
            <template #default="{ row }">{{ row.class_name || '-' }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="110">
            <template #default="{ row }">
              <StatusBadge :type="row.status === 1 ? 'normal' : 'disabled'" :label="row.status === 1 ? '正常' : '禁用'" />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" min-width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { formatTime } from '@/utils/presentation'
import http from '@/api/http'

const loading = ref(false)
const students = ref([])

const profileCompletedCount = computed(() => students.value.filter((item) => item.real_name && item.class_name).length)
const disabledCount = computed(() => students.value.filter((item) => item.status !== 1).length)

const loadStudents = async () => {
  loading.value = true
  try {
    const res = await http.get('/users/admin/list')
    students.value = res.data || []
  } finally {
    loading.value = false
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.students-page {
  display: grid;
  gap: var(--mh-space-4);
}
</style>
