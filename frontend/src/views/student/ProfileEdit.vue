<template>
  <div class="page profile-page">
    <PageHeader title="个人档案" />

    <el-alert
      v-if="loadError"
      class="profile-alert"
      :title="loadError"
      type="error"
      show-icon
      :closable="false"
    />

    <div class="profile-grid">
      <div class="main-column">
        <el-card v-if="locked" class="info-card" shadow="never">
          <template #header>
            <div class="card-header-title">已入档档案信息</div>
          </template>
          
          <el-alert
            class="profile-alert"
            title="信息锁定提示"
            type="info"
            description="学生本人不能直接修改已入档的资料。若信息有误，请联系辅导员或管理员进行修正。"
            show-icon
            :closable="false"
          />
          
          <el-descriptions :column="2" border class="descriptions-box">
            <el-descriptions-item label="登录账号">{{ user.username || '-' }}</el-descriptions-item>
            <el-descriptions-item label="真实姓名">{{ user.real_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学生性别">{{ user.gender || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属班级">{{ user.class_name || className || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card v-else class="info-card" shadow="never">
          <template #header>
            <div class="card-header-title">补充入档资料</div>
          </template>
          
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="profile-form">
            <div class="form-row">
              <el-form-item label="登录账号" class="form-item-half">
                <el-input :model-value="user.username" disabled />
              </el-form-item>
              
              <el-form-item label="真实姓名" prop="real_name" class="form-item-half">
                <el-input v-model.trim="form.real_name" placeholder="请输入真实姓名" :disabled="loading" />
              </el-form-item>
            </div>

            <div class="form-row">
              <el-form-item label="性别" prop="gender" class="form-item-half">
                <el-radio-group v-model="form.gender" :disabled="loading" class="gender-radio">
                  <el-radio-button value="男">男生</el-radio-button>
                  <el-radio-button value="女">女生</el-radio-button>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="选择班级" prop="class_id" class="form-item-half">
                <el-select v-model="form.class_id" placeholder="请选择您的班级" class="class-select" :disabled="loading">
                  <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-form-item>
            </div>

            <el-alert
              class="profile-alert"
              title="填写须知"
              type="warning"
              description="真实姓名与班级是匹配后续心理测评、预警跟进的唯一凭证，请务必如实填写。保存后不可自行修改。"
              :closable="false"
              show-icon
            />

            <div class="form-actions">
              <el-button type="primary" :loading="loading" :disabled="loading" class="save-btn" @click="handleSubmit">
                提交并保存档案
              </el-button>
            </div>
          </el-form>
        </el-card>
      </div>

      <div class="side-column">
        <el-card class="guide-card" shadow="never">
          <template #header>
            <div class="card-header-title">系统使用须知与帮助</div>
          </template>
          
          <div class="guide-content">
            <div class="guide-item">
              <h5>如何记录个人情绪？</h5>
              <p>进入“情绪识别”页面，允许调用摄像头进行面部捕捉，或手动上传您的生活照片，系统会自动分析您的主导情绪并记录在“识别记录”中。</p>
            </div>

            <div class="guide-item">
              <h5>关于风险评估</h5>
              <p>系统仅根据情绪识别频度及自测问卷给出日常心理波动的参考建议，并不代表专业临床心理评估结果。</p>
            </div>

            <div class="guide-item">
              <h5>隐私与数据安全</h5>
              <p>您的全部测评记录、图像识别记录受严格权限控制，仅限学校心理中心授权教师及本人查阅，不作任何外部透露。</p>
            </div>
          </div>
        </el-card>
      </div>
    </div>
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
    ElMessage.success('个人档案已成功保存')
    router.push('/student')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 100%;
  height: 100%;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.8fr);
  gap: 12px;
  align-items: stretch;
  flex: 1;
  min-height: 0;
}

.main-column,
.side-column {
  min-height: 0;
}

.card-header-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.descriptions-box {
  margin-top: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-item-half {
  flex: 1;
}

.gender-radio {
  width: 100%;
  display: flex;
}

.gender-radio :deep(.el-radio-button) {
  flex: 1;
}

.gender-radio :deep(.el-radio-button__inner) {
  width: 100%;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.class-select {
  width: 100%;
}

.profile-alert {
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.save-btn {
  height: 40px;
  padding: 0 24px;
  font-weight: 700;
}

.guide-card {
  height: 100%;
}

.info-card,
.guide-card {
  height: 100%;
}

.info-card :deep(.el-card__body),
.guide-card :deep(.el-card__body) {
  max-height: calc(100dvh - 190px);
  overflow: auto;
}

.guide-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.guide-item h5 {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}

.guide-item p {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--mh-muted);
}

@media (max-width: 800px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
