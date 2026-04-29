<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>学生列表</h2>
        <p>查看已注册学生账号</p>
      </div>
      <el-button :icon="RefreshRight" type="primary" @click="loadStudents" :loading="loading">刷新</el-button>
    </div>

    <el-card shadow="never">
      <el-empty v-if="!loading && students.length === 0" description="暂无学生数据" />
      <el-table v-else v-loading="loading" :data="students" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column prop="gender" label="性别" min-width="100">
          <template #default="{ row }">{{ row.gender || '-' }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" min-width="140">
          <template #default="{ row }">{{ row.class_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
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
import http from '@/api/http'

const loading = ref(false)
const students = ref([])

const loadStudents = async () => {
  loading.value = true
  try {
    const res = await http.get('/users/admin/list')
    students.value = res.data || []
  } finally {
    loading.value = false
  }
}

const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')

onMounted(loadStudents)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 6px;
}

.page-header p {
  margin: 0;
  color: #909399;
}
</style>
