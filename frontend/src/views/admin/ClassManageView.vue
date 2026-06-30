<template>
  <div class="page class-manage-page">
    <PageHeader title="班级管理">
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

    <section class="class-summary" aria-label="班级管理摘要">
      <MetricCard label="班级总数" :value="classes.length" unit="个" note="系统当前维护的班级" tone="info" icon="collection" compact />
      <MetricCard label="学生总数" :value="totalStudentCount" unit="人" note="已分配到班级的学生" tone="neutral" icon="user" compact />
      <MetricCard label="空班级" :value="emptyClassCount" unit="个" note="暂无学生归属的班级" :tone="emptyClassCount ? 'warning' : 'stable'" icon="folder" compact />
    </section>

    <el-card class="class-table-card" shadow="never">
      <template #header>
        <div class="table-toolbar">
          <div class="toolbar-left">
            <span class="card-title">班级列表</span>
            <small class="card-desc">共 {{ classes.length }} 个班级</small>
          </div>
          <el-button type="primary" @click="showAdd = true">新增班级</el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="paginatedClasses"
        stripe
        size="small"
        max-height="360"
        class="class-table"
      >
        <el-table-column prop="id" label="ID" width="90" align="center" sortable />
        <el-table-column prop="name" label="班级名称" min-width="220" sortable />
        <el-table-column prop="student_count" label="学生人数" width="130" align="center" sortable />
        <el-table-column prop="created_at" label="创建时间" min-width="180" sortable>
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
import MetricCard from '@/components/MetricCard.vue'
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

const totalStudentCount = computed(() => classes.value.reduce((sum, item) => sum + Number(item.student_count || 0), 0))
const emptyClassCount = computed(() => classes.value.filter((item) => Number(item.student_count || 0) === 0).length)

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
  gap: 12px;
  height: 100%;
}

.state-alert {
  margin-bottom: 0;
}

.class-table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.class-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.class-table-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.card-desc {
  color: var(--mh-muted);
  font-size: 11px;
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
