<template>
  <div v-if="sessionSummary" class="report-container">
    <div class="report-header">
      <div class="title-group">
        <h3 class="report-title">会话情绪分析报告</h3>
        <p class="report-subtitle">评估 ID: #VS-{{ sessionSummary.id }} · 文件: {{ sessionSummary.video_filename }}</p>
      </div>
      <div class="risk-badge-box">
        <el-tag :type="riskType(sessionSummary.risk_level)" size="large" effect="dark" class="risk-tag">
          {{ riskLabel(sessionSummary.risk_level) }}
        </el-tag>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card">
        <span class="metric-label">主导情绪</span>
        <strong class="metric-value">{{ emotionLabel(sessionSummary.dominant_emotion) }}</strong>
        <p class="metric-desc">置信度 {{ formatPercent(sessionSummary.dominant_confidence || sessionSummary.confidence) }}</p>
      </div>

      <div class="metric-card">
        <span class="metric-label">负向情绪频次占比</span>
        <strong class="metric-value" :class="{ 'is-negative': sessionSummary.negative_ratio >= 0.3 }">
          {{ formatPercent(sessionSummary.negative_ratio) }}
        </strong>
        <p class="metric-desc">超出 30% 触发风险关注</p>
      </div>

      <div class="metric-card">
        <span class="metric-label">分析样本帧</span>
        <strong class="metric-value">{{ sessionSummary.analyzed_frames }} 帧</strong>
        <p class="metric-desc">总设计帧数 {{ sessionSummary.total_frames }} 帧</p>
      </div>
    </div>

    <el-card class="result-details" shadow="never">
      <div class="details-section">
        <h4 class="section-title">风险评估原因</h4>
        <p class="section-text">{{ sessionSummary.reason || '无明显异常负向情绪集中或高频波动。' }}</p>
      </div>

      <el-divider />

      <div class="details-section">
        <h4 class="section-title">系统干预建议</h4>
        <p class="section-text suggestion-text">{{ sessionSummary.suggestion || '建议保持日常关注，定期查看学生测评表现。' }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { emotionLabel, riskLabel, riskType } from '@/domain/mentalHealth'

defineProps({
  sessionSummary: {
    type: Object,
    required: true
  }
})

const formatPercent = (val) => {
  if (val === undefined || val === null) return '-'
  return `${(Number(val) * 100).toFixed(1)}%`
}
</script>

<style scoped>
.report-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--mh-line);
}

.report-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--mh-ink);
}

.report-subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--mh-muted);
}

.risk-tag {
  font-size: 14px;
  font-weight: 700;
  padding: 6px 16px;
  border-radius: var(--mh-radius-sm);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 12px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
}

.metric-label {
  display: block;
  font-size: 12px;
  color: var(--mh-muted);
  font-weight: 600;
}

.metric-value {
  display: block;
  font-size: 20px;
  font-weight: 850;
  color: var(--mh-ink);
  margin-top: 6px;
}

.metric-value.is-negative {
  color: var(--mh-danger);
}

.metric-desc {
  margin: 4px 0 0;
  font-size: 11px;
  color: var(--mh-muted);
}

.result-details {
  background: var(--mh-surface) !important;
}

.details-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}

.section-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--mh-text);
}

.suggestion-text {
  font-weight: 600;
  color: var(--mh-primary-strong);
}

.el-divider {
  margin: 12px 0;
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
