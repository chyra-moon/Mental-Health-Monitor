<template>
  <div class="page students-page">
    <PageHeader title="学生档案" description="查看学生入档状态、班级归属和账号启用情况">
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadStudents" :loading="loading">刷新</el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="loadError"
      class="state-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <el-card class="students-table-card" shadow="never">
      <el-empty v-if="!loading && students.length === 0" description="暂无学生数据" />
      <el-table v-else v-loading="loading" :data="students" stripe size="small" max-height="520" aria-label="学生档案列表">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="real_name" label="姓名" min-width="120">
          <template #default="{ row }">{{ row.real_name || '未入档' }}</template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" min-width="100">
          <template #default="{ row }">{{ row.gender || '-' }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" min-width="140">
          <template #default="{ row }">{{ row.class_name || '未分班' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="账号状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { listStudents } from '@/api/users'
import { formatTime } from '@/domain/mentalHealth'

const loading = ref(false)
const loadError = ref('')
const students = ref([])

const loadStudents = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listStudents()
    students.value = res.data || []
  } catch (error) {
    loadError.value = error?.message || '学生列表加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.students-page {
  display: grid;
  gap: 16px;
  max-width: 100%;
  overflow-x: hidden;
}

.state-alert {
  margin-bottom: 0;
}

.students-table-card {
  min-width: 0;
}
</style>
