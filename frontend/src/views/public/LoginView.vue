<template>
  <AuthShell
    mode="login"
    eyebrow="账号登录"
    title="进入平台"
    subtitle="请使用学生或管理员账号继续访问"
    headline="基于物联网数据分析的心理健康监测系统"
    description="面向校园日常心理服务场景，整合情绪检测、趋势观察、风险预警和管理留痕。"
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
          placeholder="请输入密码"
          autocomplete="current-password"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="submit-btn" @click="handleLogin" :loading="loading">
          登录
        </el-button>
      </el-form-item>
    </el-form>
    <p class="auth-link">
      还没有账号？
      <router-link to="/register">去注册</router-link>
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

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await http.post('/auth/login', form)
    const { token, user } = res.data
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    ElMessage.success('登录成功')
    router.push(user.role === 'admin' ? '/admin' : '/student')
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
