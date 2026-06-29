<template>
  <CampusAuthFrame
    mode="register"
    title="创建学生自助账号"
    description="学生账号用于完成个人档案、情绪识别记录和心理测评；管理员和心理中心账号请由学校统一开通。"
    form-title="学生注册"
    form-description="注册后请立即完善真实姓名、性别和班级，资料保存后需联系管理员才能修改。"
    form-title-id="register-form-title"
    :context-items="contextItems"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="handleRegister">
      <el-form-item label="用户名" prop="username">
        <el-input v-model.trim="form.username" autocomplete="username" placeholder="设置登录用户名" :disabled="loading" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          autocomplete="new-password"
          placeholder="至少 6 位"
          show-password
          :disabled="loading"
        />
      </el-form-item>
      <el-button type="primary" class="submit-button" :loading="loading" :disabled="loading" @click="handleRegister">
        创建学生账号
      </el-button>
    </el-form>
    <p class="auth-switch">
      已有学校账号？
      <router-link to="/login">返回登录</router-link>
    </p>
  </CampusAuthFrame>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CampusAuthFrame from '@/components/CampusAuthFrame.vue'
import { registerStudent } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const contextItems = [
  { label: '账号身份', text: '当前注册入口只创建学生账号，用于本人记录和测评。' },
  { label: '资料入档', text: '首次登录后需完善真实姓名、性别和班级，便于学校在需要时提供支持。' },
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
    await registerStudent(form)
    ElMessage.success('注册成功，请登录后完善个人档案')
    router.push('/login')
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
