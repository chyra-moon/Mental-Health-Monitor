<template>
  <div class="page students-page">
    <PageHeader title="学生档案">
      <template #actions>
        <el-button :icon="RefreshRight" type="primary" @click="loadData" :loading="loading">刷新</el-button>
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
      <el-table
        v-loading="loading"
        :data="paginatedStudents"
        stripe
        size="small"
        max-height="390"
        @sort-change="handleSortChange"
        class="students-table"
      >
        <el-table-column prop="id" label="ID" width="90" sortable="custom" align="center" />
        <el-table-column prop="username" label="用户名" min-width="140" sortable="custom" />
        <el-table-column prop="real_name" label="姓名" min-width="120" sortable="custom">
          <template #default="{ row }">{{ row.real_name || '未入档' }}</template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" min-width="90" sortable="custom" align="center">
          <template #default="{ row }">{{ row.gender || '-' }}</template>
        </el-table-column>
        
        <!-- Interactive header class selection filter -->
        <el-table-column prop="class_name" label="班级" min-width="170" sortable="custom">
          <template #header>
            <el-select
              v-model="selectedClassFilter"
              size="small"
              placeholder="全校班级筛选"
              clearable
              class="header-filter-select"
            >
              <el-option
                v-for="item in classes"
                :key="item.id"
                :label="item.name"
                :value="item.name"
              />
            </el-select>
          </template>
          <template #default="{ row }">{{ row.class_name || '未分班' }}</template>
        </el-table-column>

        <el-table-column prop="status" label="账号状态" min-width="110" sortable="custom" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '正常启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="注册时间" min-width="170" sortable="custom">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredStudents.length"
          layout="prev, pager, next, total"
          size="small"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { listStudents } from '@/api/users'
import { listAdminClasses } from '@/api/classes'
import { formatTime } from '@/domain/mentalHealth'

const loading = ref(false)
const loadError = ref('')
const students = ref([])
const classes = ref([])
const selectedClassFilter = ref('')

const currentPage = ref(1)
const pageSize = ref(10)
const sortProp = ref('')
const sortOrder = ref('')

const filteredStudents = computed(() => {
  let list = [...students.value]
  
  // Apply class filter
  if (selectedClassFilter.value) {
    list = list.filter(student => student.class_name === selectedClassFilter.value)
  }

  // Apply sorting
  if (sortProp.value && sortOrder.value) {
    const prop = sortProp.value
    const order = sortOrder.value === 'ascending' ? 1 : -1
    
    list.sort((a, b) => {
      let valA = a[prop]
      let valB = b[prop]
      
      // Fallback for nulls
      if (valA === null || valA === undefined) valA = ''
      if (valB === null || valB === undefined) valB = ''
      
      if (typeof valA === 'string') {
        return valA.localeCompare(valB) * order
      }
      return (valA - valB) * order
    })
  }

  return list
})

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStudents.value.slice(start, end)
})

watch(selectedClassFilter, () => {
  currentPage.value = 1
})

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [studentsRes, classesRes] = await Promise.all([
      listStudents(),
      listAdminClasses()
    ])
    students.value = studentsRes.data || []
    classes.value = classesRes.data || []
    currentPage.value = 1
  } catch (error) {
    loadError.value = error?.message || '加载学生档案数据失败，请重试。'
  } finally {
    loading.value = false
  }
}

function handleSortChange({ prop, order }) {
  sortProp.value = prop
  sortOrder.value = order
  currentPage.value = 1
}

onMounted(loadData)
</script>

<style scoped>
.students-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.students-table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  min-height: 0;
}

.students-table-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.students-table {
  margin-top: 4px;
}

.header-filter-select {
  width: 100%;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
