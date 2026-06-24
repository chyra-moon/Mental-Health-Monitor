<template>
  <AuthShell
    mode="register"
    eyebrow="账号注册"
    title="创建学生账号"
    subtitle="注册后请先完善个人资料，再进入学生端功能"
    headline="把心理状态记录在校园服务流程里"
    description="平台保留学生自助检测、教师风险研判和过程追踪，注册仅创建账号，不改变后续资料完善流程。"
    :features="features"
  >
    <el-form ref="formRef" class="auth-form" :model="form" :rules="rules" label-width="0">
      <el-form-item prop="username">
        <label class="field-label">用户名</label>
        <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
      </el-form-item>
      <el-form-item prop="password">
        <label class="field-label">密码</label>
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入不少于 6 位的密码"
          autocomplete="new-password"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="submit-btn" @click="handleRegister" :loading="loading">
          注册
        </el-button>
      </el-form-item>
    </el-form>
    <p class="auth-link">
      已有账号？
      <router-link to="/login">去登录</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthShell from '@/components/layout/AuthShell.vue'
import http from '@/api/http'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const features = [
  { code: '01', title: '账号创建', text: '使用用户名和密码完成注册' },
  { code: '02', title: '资料完善', text: '首次进入学生端需填写姓名、性别和班级' },
  { code: '03', title: '状态追踪', text: '检测记录和趋势用于后续自查与管理查看' },
]

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await http.post('/auth/register', form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form {
  display: grid;
  gap: 4px;
}

.field-label {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  color: var(--mh-text);
  font-size: 14px;
  font-weight: 760;
}

.submit-btn {
  width: 100%;
  min-height: 44px;
  margin-top: 6px;
  font-size: 15px;
}

.auth-link {
  margin: 18px 0 0;
  color: var(--mh-muted);
  font-size: 14px;
  text-align: center;
}

.auth-link a {
  color: var(--mh-primary-dark);
  font-weight: 760;
  text-decoration: none;
}
</style>
