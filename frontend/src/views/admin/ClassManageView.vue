<template>
  <div class="page class-manage-page">
    <PageHeader title="班级管理" description="维护系统中的班级范围；删除前需确认班级内没有学生">
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
      <el-empty v-if="!loading && classes.length === 0" description="暂无班级数据" />
      <el-table v-else v-loading="loading" :data="classes" stripe size="small" max-height="520" aria-label="班级列表">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="班级名称" min-width="200" />
        <el-table-column prop="student_count" label="学生人数" width="120" align="center" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
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
    </el-card>

    <el-dialog v-model="showAdd" title="新增班级" width="420px" destroy-on-close>
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-position="top">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model.trim="addForm.name" placeholder="请输入班级名称，如：计算机技术一班" :disabled="adding" />
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
import { reactive, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { createClass, deleteClass, listAdminClasses } from '@/api/classes'

const loading = ref(false)
const loadError = ref('')
const classes = ref([])
const showAdd = ref(false)
const adding = ref(false)
const addFormRef = ref(null)
const addForm = reactive({ name: '' })
const addRules = { name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }] }

onMounted(loadClasses)

async function loadClasses() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listAdminClasses()
    classes.value = res.data || []
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
  display: grid;
  gap: 16px;
  max-width: 100%;
  overflow-x: hidden;
}

.state-alert {
  margin-bottom: 0;
}

.class-table-card {
  min-width: 0;
}
</style>
