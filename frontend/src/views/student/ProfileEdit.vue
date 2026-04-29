<template>
  <div class="page">
    <div class="page-header">
      <h2>个人信息</h2>
      <p v-if="!locked">请填写以下信息以完成账号设置，保存后不可自行修改，如需更改请联系管理员</p>
      <p v-else>信息已完善，如需修改请联系管理员</p>
    </div>

    <el-card class="profile-card" shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" style="max-width:480px" :disabled="locked">
        <el-form-item label="用户名">
          <el-input :model-value="user?.username" disabled />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" :disabled="locked" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender" :disabled="locked">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" style="width:100%" :disabled="locked">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!locked">
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
        </el-form-item>
        <el-form-item v-else>
          <el-tag type="success">信息已完善</el-tag>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '@/api/http'

const router = useRouter()
const user = JSON.parse(localStorage.getItem('user') || '{}')
const formRef = ref(null)
const loading = ref(false)
const classes = ref([])
const locked = ref(!!user.real_name)

const form = reactive({
  real_name: user.real_name || '',
  gender: user.gender || '男',
  class_id: user.class_id || null,
})

const rules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
}

onMounted(async () => {
  try {
    const res = await http.get('/classes')
    classes.value = res.data || []
  } catch {}
})

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await http.put('/auth/profile', {
      real_name: form.real_name,
      gender: form.gender,
      class_id: form.class_id,
    })
    const newUser = res.data
    localStorage.setItem('user', JSON.stringify(newUser))
    locked.value = true
    ElMessage.success('个人信息已保存')
    router.push('/student')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 20px; color: #303133; }
.page-header p { margin: 0; font-size: 13px; color: #909399; }
.profile-card { max-width: 600px; }
</style>
