<template>
  <div class="auth-page">
    <section class="auth-hero">
      <div class="brand-mark">
        <span class="brand-icon">M</span>
        <span>心理健康监测系统</span>
      </div>
      <div class="hero-copy">
        <h1>学生心理健康<br />监测与预警平台</h1>
        <p>融合物联网采集、情绪识别、趋势分析与风险预警，帮助学校持续关注学生心理状态。</p>
      </div>
      <div class="capability-row">
        <div class="capability">
          <span class="cap-icon">01</span>
          <div>
            <strong>智能感知</strong>
            <small>视频与图像情绪识别</small>
          </div>
        </div>
        <div class="capability">
          <span class="cap-icon">02</span>
          <div>
            <strong>数据研判</strong>
            <small>长期趋势辅助分析</small>
          </div>
        </div>
        <div class="capability">
          <span class="cap-icon">03</span>
          <div>
            <strong>风险预警</strong>
            <small>中高风险及时提示</small>
          </div>
        </div>
      </div>
      <div class="iot-visual" aria-hidden="true">
        <div class="core-ring">
          <div class="pulse-core">心</div>
        </div>
        <span class="node node-a"></span>
        <span class="node node-b"></span>
        <span class="node node-c"></span>
      </div>
    </section>

    <section class="auth-panel">
      <div class="panel-tabs">
        <span class="active">登录</span>
        <router-link to="/register">注册</router-link>
      </div>
      <div class="panel-title">
        <h2>欢迎回来</h2>
        <p>请使用系统账号登录平台</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <label class="field-label">用户名</label>
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item prop="password">
          <label class="field-label">密码</label>
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
      <p class="register-link">
        还没有账号？
        <router-link to="/register">去注册</router-link>
      </p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(520px, 1fr) 460px;
  align-items: center;
  gap: 54px;
  padding: 56px 9vw;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 20% 18%, rgba(94, 178, 255, 0.30), transparent 26%),
    radial-gradient(circle at 82% 80%, rgba(77, 211, 196, 0.20), transparent 24%),
    linear-gradient(135deg, #f8fbff 0%, #eef7ff 48%, #f6fbff 100%);
}

.auth-page::before {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0.42;
  background-image:
    linear-gradient(rgba(64, 126, 220, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 126, 220, 0.06) 1px, transparent 1px);
  background-size: 48px 48px;
}

.auth-hero,
.auth-panel {
  position: relative;
  z-index: 1;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #234371;
  font-weight: 750;
  padding: 10px 14px;
  border: 1px solid rgba(77, 130, 213, 0.16);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 8px 18px rgba(66, 110, 174, 0.08);
}

.brand-icon {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(135deg, #2f7df6, #38c8df);
}

.hero-copy {
  margin-top: 54px;
  max-width: 680px;
}

.hero-copy h1 {
  margin: 0;
  color: #19396c;
  font-size: clamp(42px, 5vw, 68px);
  line-height: 1.12;
  font-weight: 850;
  letter-spacing: 0;
}

.hero-copy p {
  width: min(560px, 100%);
  margin: 24px 0 0;
  color: #6880a8;
  font-size: 17px;
  line-height: 1.9;
}

.capability-row {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 38px;
}

.capability {
  min-width: 168px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(94, 140, 210, 0.13);
  box-shadow: 0 8px 18px rgba(64, 105, 164, 0.06);
}

.cap-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, #317df4, #46d0d0);
}

.capability strong {
  display: block;
  color: #274672;
  font-size: 14px;
}

.capability small {
  color: #8ba0c1;
  font-size: 12px;
}

.iot-visual {
  position: relative;
  width: 360px;
  height: 210px;
  margin-top: 46px;
}

.core-ring {
  position: absolute;
  left: 128px;
  top: 12px;
  width: 164px;
  height: 164px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,.96), rgba(197,232,255,.68));
  border: 1px solid rgba(73, 144, 226, 0.18);
  box-shadow: 0 12px 30px rgba(49, 125, 244, 0.16);
}

.core-ring::before,
.core-ring::after {
  content: "";
  position: absolute;
  inset: -24px;
  border-radius: 50%;
  border: 1px dashed rgba(55, 145, 231, 0.26);
}

.core-ring::after {
  inset: -52px;
}

.pulse-core {
  width: 86px;
  height: 86px;
  display: grid;
  place-items: center;
  border-radius: 28px;
  color: #fff;
  font-size: 34px;
  font-weight: 850;
  background: linear-gradient(145deg, #59b8ff, #2f7df6);
  box-shadow: inset 0 1px 8px rgba(255,255,255,.3), 0 10px 20px rgba(47,125,246,.18);
}

.node {
  position: absolute;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4bd4cc;
  box-shadow: 0 0 0 8px rgba(75, 212, 204, 0.16);
}

.node-a { left: 56px; top: 90px; }
.node-b { left: 300px; top: 14px; background: #5b8dff; }
.node-c { left: 238px; top: 188px; background: #38c77e; }

.auth-panel {
  padding: 36px 40px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(116, 154, 213, 0.16);
  box-shadow: 0 16px 36px rgba(56, 104, 169, 0.12);
}

.panel-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 48px;
  align-items: center;
  border-bottom: 1px solid rgba(102, 136, 188, 0.16);
  margin-bottom: 28px;
}

.panel-tabs span,
.panel-tabs a {
  text-align: center;
  color: #94a5c4;
  text-decoration: none;
  font-size: 16px;
  font-weight: 700;
}

.panel-tabs .active {
  color: #2f7df6;
  position: relative;
}

.panel-tabs .active::after {
  content: "";
  position: absolute;
  left: 22%;
  right: 22%;
  bottom: -15px;
  height: 3px;
  border-radius: 10px;
  background: linear-gradient(90deg, #2f7df6, #57c9ef);
}

.panel-title h2 {
  margin: 0;
  color: #1f3d6d;
  font-size: 28px;
  letter-spacing: 0;
}

.panel-title p {
  margin: 8px 0 26px;
  color: #8ba0c1;
}

.field-label {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  color: #405a86;
  font-size: 14px;
  font-weight: 700;
}

.login-btn {
  width: 100%;
  height: 46px;
  margin-top: 8px;
  font-size: 16px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #8ba0c1;
  margin: 22px 0 0;
}

.register-link a {
  color: #2f7df6;
  font-weight: 750;
  text-decoration: none;
}

@media (max-width: 960px) {
  .auth-page {
    grid-template-columns: 1fr;
    padding: 32px 20px;
  }

  .auth-hero {
    display: none;
  }

  .auth-panel {
    width: min(440px, 100%);
    margin: 0 auto;
  }
}
</style>
