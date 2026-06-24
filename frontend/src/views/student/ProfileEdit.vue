<template>
  <div class="page profile-page">
    <PageHeader
      eyebrow="学生资料"
      title="完善个人信息"
      :description="locked ? '信息已完善，如需修改请联系管理员。' : '请填写真实姓名、性别和班级，保存后不可自行修改。'"
    />

    <section class="profile-shell">
      <aside class="profile-aside">
        <span>Profile Setup</span>
        <h2>{{ locked ? '资料已确认' : '首次使用前需完成资料确认' }}</h2>
        <p>班级信息会用于管理端查看、预警归属和后续记录筛选，保存后沿用原有账号资料流程。</p>
        <StatusBadge :type="locked ? 'handled' : 'pending'" :label="locked ? '已完善' : '待完善'" />
      </aside>

      <section class="business-panel form-panel">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="82px" :disabled="locked">
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
            <el-button type="primary" @click="handleSubmit" :loading="loading">保存资料</el-button>
          </el-form-item>
          <el-form-item v-else>
            <StatusBadge type="handled" label="信息已完善" />
          </el-form-item>
        </el-form>
      </section>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
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
.profile-shell {
  display: grid;
  grid-template-columns: minmax(240px, 0.42fr) minmax(360px, 0.58fr);
  gap: var(--mh-space-4);
  align-items: start;
}

.profile-aside {
  padding: var(--mh-space-6);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background:
    linear-gradient(180deg, var(--mh-primary-soft), #ffffff);
  box-shadow: var(--mh-shadow-soft);
}

.profile-aside span {
  color: var(--mh-warm);
  font-size: 12px;
  font-weight: 820;
}

.profile-aside h2 {
  margin: 10px 0 0;
  color: var(--mh-ink);
  font-size: 20px;
}

.profile-aside p {
  margin: 12px 0 18px;
  color: var(--mh-text);
  line-height: 1.8;
}

.form-panel {
  max-width: 640px;
}

@media (max-width: 860px) {
  .profile-shell {
    grid-template-columns: 1fr;
  }

  .form-panel {
    max-width: none;
  }
}
</style>
