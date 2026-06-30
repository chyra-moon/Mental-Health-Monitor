<template>
  <CampusAuthFrame
    mode="login"
    title="心理健康监测系统"
    description="识别、测评、预警与档案集中管理。"
    form-title="账号登录"
    form-description="输入账号和密码进入系统。"
    form-title-id="login-form-title"
    :context-items="contextItems"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="handleLogin">
      <el-form-item label="用户名" prop="username">
        <el-input v-model.trim="form.username" autocomplete="username" placeholder="请输入账号" :disabled="loading" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          autocomplete="current-password"
          placeholder="请输入密码"
          show-password
          :disabled="loading"
        />
      </el-form-item>
      <el-button type="primary" class="submit-button" :loading="loading" :disabled="loading" @click="handleLogin">
        登录
      </el-button>
    </el-form>
    <p class="auth-switch">
      学生还没有账号？
      <router-link to="/register">创建学生账号</router-link>
    </p>
  </CampusAuthFrame>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CampusAuthFrame from '@/components/CampusAuthFrame.vue'
import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const contextItems = [
  { label: '账号范围', text: '学生可注册，管理员账号由学校维护。' },
  { label: '数据用途', text: '数据仅用于校内支持。' },
]

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
    const res = await login(form)
    const { token, user } = res.data
    userStore.login(token, user)
    ElMessage.success('登录成功')
    router.push(user.role === 'admin' ? '/admin' : '/student')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.submit-button {
  width: 100%;
  min-height: 44px;
  margin-top: 4px;
  font-size: 16px;
}

.auth-switch {
  margin: 18px 0 0;
  color: var(--mh-muted);
  font-size: 14px;
  text-align: center;
}

.auth-switch a {
  color: var(--mh-primary-strong);
  font-weight: 750;
  text-decoration: none;
}
</style>
