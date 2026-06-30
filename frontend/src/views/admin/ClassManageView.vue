<template>
  <div class="page class-manage-page">
    <PageHeader title="班级管理" description="维护系统中的班级范围。注意：删除班级前必须确认班级内没有任何学生。">
      <template #actions>
        <el-button type="primary" @click="showAdd = true">新增班级</el-button>
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

    <el-card class="class-table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="paginatedClasses"
        stripe
        size="small"
        max-height="450"
        class="class-table"
      >
        <el-table-column prop="id" label="ID" width="90" align="center" />
        <el-table-column prop="name" label="班级名称" min-width="220" />
        <el-table-column prop="student_count" label="学生人数" width="130" align="center" />
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确认删除该班级？"
              confirm-button-text="确认"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button type="danger" size="small" link :disabled="row.student_count > 0">
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="classes.length"
          layout="prev, pager, next, total"
          size="small"
        />
      </div>
    </el-card>

    <el-dialog v-model="showAdd" title="新增班级" width="420px" destroy-on-close>
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-position="top">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model.trim="addForm.name" placeholder="请输入班级名称，如：心理咨询一班" :disabled="adding" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :disabled="adding" @click="showAdd = false">取消</el-button>
        <el-button type="primary" :loading="adding" :disabled="adding || !addForm.name" @click="handleAdd">
          确认新增
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { createClass, deleteClass, listAdminClasses } from '@/api/classes'
import { formatTime } from '@/domain/mentalHealth'

const loading = ref(false)
const loadError = ref('')
const classes = ref([])
const showAdd = ref(false)
const adding = ref(false)
const addFormRef = ref(null)
const addForm = reactive({ name: '' })
const addRules = { name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }] }

const currentPage = ref(1)
const pageSize = ref(10)

const paginatedClasses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return classes.value.slice(start, end)
})

onMounted(loadClasses)

async function loadClasses() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listAdminClasses()
    classes.value = res.data || []
    currentPage.value = 1
  } catch (error) {
    loadError.value = error?.message || '班级数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid) return

  adding.value = true
  try {
    await createClass({ name: addForm.name })
    ElMessage.success('班级创建成功')
    showAdd.value = false
    addForm.name = ''
    await loadClasses()
  } catch {
    ElMessage.error('创建失败，班级名可能已存在')
  } finally {
    adding.value = false
  }
}

async function handleDelete(row) {
  try {
    await deleteClass(row.id)
    ElMessage.success('班级已删除')
    await loadClasses()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.class-manage-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.class-table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.class-table {
  margin-top: 4px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
