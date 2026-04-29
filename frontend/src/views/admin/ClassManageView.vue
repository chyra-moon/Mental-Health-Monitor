<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>班级列表</h2>
        <p>管理系统中的班级，删除班级前需确保班级内无学生</p>
      </div>
      <el-button type="primary" @click="showAdd = true">新增班级</el-button>
    </div>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="classes" stripe>
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="班级名称" min-width="200" />
        <el-table-column prop="student_count" label="学生人数" width="120" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="200" />
        <el-table-column label="操作" width="100" align="center" fixed="right">
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

    <!-- 新增班级弹窗 -->
    <el-dialog v-model="showAdd" title="新增班级" width="400px">
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="0">
        <el-form-item prop="name">
          <el-input v-model="addForm.name" placeholder="请输入班级名称，如：一班" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAdd">确认新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/api/http'

const loading = ref(false)
const classes = ref([])
const showAdd = ref(false)
const adding = ref(false)
const addFormRef = ref(null)
const addForm = reactive({ name: '' })
const addRules = { name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }] }

onMounted(loadClasses)

async function loadClasses() {
  loading.value = true
  try {
    const res = await http.get('/admin/classes')
    classes.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid) return

  adding.value = true
  try {
    await http.post('/admin/classes', { name: addForm.name })
    ElMessage.success('班级创建成功')
    showAdd.value = false
    addForm.name = ''
    loadClasses()
  } catch {
    ElMessage.error('创建失败，班级名可能已存在')
  } finally {
    adding.value = false
  }
}

async function handleDelete(row) {
  try {
    await http.delete(`/admin/classes/${row.id}`)
    ElMessage.success('班级已删除')
    loadClasses()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 20px; color: #303133; }
.page-header p { margin: 0; font-size: 13px; color: #909399; }
</style>
