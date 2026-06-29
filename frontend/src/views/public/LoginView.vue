<template>
  <CampusAuthFrame
    mode="login"
    title="校园心理健康支持系统"
    description="学生可查看个人记录和测评建议，心理中心人员可跟进风险预警、学生档案和视频会话。"
    form-title="账号登录"
    form-description="请使用学校分配的账号登录。学生首次登录后需要先完善个人档案。"
    form-title-id="login-form-title"
    :context-items="contextItems"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="handleLogin">
      <el-form-item label="用户名" prop="username">
        <el-input v-model.trim="form.username" autocomplete="username" placeholder="请输入学校账号" :disabled="loading" />
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
  { label: '账号范围', text: '管理员账号由学校维护；学生可使用注册入口创建本人账号。' },
  { label: '隐私用途', text: '识别、测评和预警数据仅用于校内心理健康支持和必要跟进。' },
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
