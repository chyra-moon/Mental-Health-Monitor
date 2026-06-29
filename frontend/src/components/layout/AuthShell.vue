<template>
  <main class="auth-shell">
    <section class="auth-campus">
      <div class="brand-row">
        <AppLogo />
      </div>
      <div class="campus-copy">
        <span class="copy-kicker">基于物联网数据分析的心理健康监测系统</span>
        <h1>{{ headline }}</h1>
        <p>{{ description }}</p>
      </div>

      <div class="campus-board" aria-hidden="true">
        <div class="board-roof"></div>
        <div class="board-body">
          <div class="board-line wide"></div>
          <div class="board-line"></div>
          <div class="board-tags">
            <span>情绪识别</span>
            <span>趋势分析</span>
            <span>风险预警</span>
          </div>
        </div>
      </div>

      <div class="feature-ledger">
        <div v-for="item in features" :key="item.title" class="feature-item">
          <span>{{ item.code }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.text }}</p>
        </div>
      </div>
    </section>

    <section class="auth-card">
      <div class="auth-tabs">
        <router-link to="/login" :class="{ active: mode === 'login' }">登录</router-link>
        <router-link to="/register" :class="{ active: mode === 'register' }">注册</router-link>
      </div>
      <div class="auth-title">
        <span>{{ eyebrow }}</span>
        <h2>{{ title }}</h2>
        <p>{{ subtitle }}</p>
      </div>
      <slot />
    </section>
  </main>
</template>

<script setup>
import AppLogo from '@/components/AppLogo.vue'

defineProps({
  mode: { type: String, required: true },
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  headline: { type: String, default: '基于物联网数据分析的心理健康监测系统' },
  description: { type: String, default: '将学生日常情绪识别、历史记录、趋势分析和风险预警放在同一个清晰工作流中，方便学生自查，也方便教师持续关注。' },
  features: {
    type: Array,
    default: () => [
      { code: '01', title: '学生自助', text: '完成资料后即可进行情绪识别和记录查看' },
      { code: '02', title: '教师研判', text: '聚合班级、学生、预警和历史数据' },
      { code: '03', title: '过程留痕', text: '识别记录与视频分析会形成可追溯结果' },
    ],
  },
})
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 430px);
  align-items: center;
  gap: clamp(28px, 5vw, 70px);
  padding: clamp(28px, 5vw, 64px) clamp(18px, 7vw, 92px);
  background:
    linear-gradient(90deg, rgba(20, 118, 109, 0.06) 1px, transparent 1px),
    linear-gradient(0deg, rgba(20, 118, 109, 0.05) 1px, transparent 1px),
    linear-gradient(135deg, #fbfcf8 0%, #f0f7f3 52%, #f8faf4 100%);
  background-size: 44px 44px, 44px 44px, auto;
}

.auth-campus {
  min-width: 0;
}

.brand-row {
  margin-bottom: clamp(28px, 5vh, 54px);
}

.campus-copy {
  max-width: 720px;
}

.copy-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid var(--mh-line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--mh-primary-dark);
  font-size: 13px;
  font-weight: 760;
}

h1 {
  margin: 18px 0 0;
  color: var(--mh-ink);
  font-size: clamp(36px, 5vw, 58px);
  line-height: 1.14;
  letter-spacing: 0;
}

.campus-copy p {
  max-width: 600px;
  margin: 18px 0 0;
  color: var(--mh-text);
  font-size: 16px;
  line-height: 1.9;
}

.campus-board {
  width: min(520px, 100%);
  margin: 34px 0;
  border: 1px solid var(--mh-line-strong);
  border-radius: var(--mh-radius);
  background: var(--mh-surface);
  box-shadow: var(--mh-shadow);
  overflow: hidden;
}

.board-roof {
  height: 18px;
  background:
    repeating-linear-gradient(90deg, #dfece5 0 22px, #f7f3e9 22px 44px);
  border-bottom: 1px solid var(--mh-line);
}

.board-body {
  padding: 22px;
}

.board-line {
  height: 10px;
  width: 58%;
  margin-bottom: 12px;
  border-radius: 999px;
  background: #d8e8e2;
}

.board-line.wide {
  width: 78%;
  background: #c7ded6;
}

.board-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.board-tags span {
  padding: 6px 10px;
  border: 1px solid var(--mh-line);
  border-radius: 999px;
  color: var(--mh-primary-dark);
  background: var(--mh-primary-soft);
  font-size: 12px;
  font-weight: 720;
}

.feature-ledger {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  max-width: 720px;
}

.feature-item {
  min-width: 0;
  padding: 16px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: rgba(255, 255, 255, 0.8);
}

.feature-item span {
  color: var(--mh-warm);
  font-size: 12px;
  font-weight: 820;
}

.feature-item strong {
  display: block;
  margin-top: 8px;
  color: var(--mh-ink);
  font-size: 15px;
}

.feature-item p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.7;
}

.auth-card {
  width: 100%;
  padding: 30px;
  border: 1px solid var(--mh-line-strong);
  border-radius: var(--mh-radius-lg);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--mh-shadow);
}

.auth-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 4px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: var(--mh-surface-soft);
}

.auth-tabs a {
  min-height: 38px;
  display: grid;
  place-items: center;
  border-radius: 6px;
  color: var(--mh-muted);
  font-weight: 760;
  text-decoration: none;
}

.auth-tabs a.active {
  background: var(--mh-surface);
  color: var(--mh-primary-dark);
  box-shadow: 0 4px 12px rgba(47, 76, 68, 0.08);
}

.auth-title {
  margin: 24px 0;
}

.auth-title span {
  color: var(--mh-muted);
  font-size: 12px;
  font-weight: 760;
}

.auth-title h2 {
  margin: 8px 0 0;
  color: var(--mh-ink);
  font-size: 26px;
  letter-spacing: 0;
}

.auth-title p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 14px;
}

@media (max-width: 980px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-campus {
    display: none;
  }

  .auth-card {
    max-width: 460px;
    margin: 0 auto;
  }
}

@media (max-width: 520px) {
  .auth-shell {
    padding: 18px;
  }

  .auth-card {
    padding: 22px 18px;
  }
}
</style>
