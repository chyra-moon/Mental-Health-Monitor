<template>
  <div class="page profile-page">
    <PageHeader
      title="个人档案"
      :description="locked ? '档案已完成入档，如需调整请联系管理员。' : '请补全真实姓名、性别和班级，保存后用于校内关注和必要支持。'"
    />

    <el-alert
      v-if="loadError"
      class="profile-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <el-card v-if="locked" class="profile-card" shadow="never">
      <template #header>已入档信息</template>
      <el-alert
        class="profile-alert"
        title="学生本人不能直接修改已入档资料，确需变更时请联系辅导员或系统管理员。"
        type="success"
        show-icon
        :closable="false"
      />
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ user.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ user.real_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ user.gender || '-' }}</el-descriptions-item>
        <el-descriptions-item label="班级">{{ user.class_name || className || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-else class="profile-card" shadow="never">
      <template #header>学生入档信息</template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="profile-form">
        <el-form-item label="用户名">
          <el-input :model-value="user.username" disabled />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model.trim="form.real_name" autocomplete="name" placeholder="请输入真实姓名" :disabled="loading" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender" :disabled="loading">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" class="class-select" :disabled="loading">
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-alert
          class="profile-alert"
          title="保存后系统会将测评、识别记录和风险提醒关联到该学生档案。"
          type="info"
          show-icon
          :closable="false"
        />
        <div class="form-actions">
          <el-button type="primary" :loading="loading" :disabled="loading" @click="handleSubmit">
            保存档案
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { updateStudentProfile } from '@/api/auth'
import { listClasses } from '@/api/classes'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const loadError = ref('')
const classes = ref([])

const user = computed(() => userStore.user || {})
const locked = computed(() => !!user.value.real_name)
const className = computed(() => classes.value.find((item) => item.id === user.value.class_id)?.name || '')

const form = reactive({
  real_name: user.value.real_name || '',
  gender: user.value.gender || '男',
  class_id: user.value.class_id || null,
})

const rules = {
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
}

onMounted(async () => {
  try {
    const res = await listClasses()
    classes.value = res.data || []
  } catch (error) {
    loadError.value = error?.message || '班级数据加载失败，请稍后重试。'
  }
})

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await updateStudentProfile({
      real_name: form.real_name,
      gender: form.gender,
      class_id: form.class_id,
    })
    userStore.updateUser(res.data)
    ElMessage.success('个人档案已保存')
    router.push('/student')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 760px;
}

.profile-card {
  max-width: 680px;
}

.profile-form {
  max-width: 520px;
}

.class-select {
  width: 100%;
}

.profile-alert {
  margin: 8px 0 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .form-actions {
    justify-content: stretch;
  }

  .form-actions .el-button {
    width: 100%;
  }
}
</style>
