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
      <MetricCard
        label="主导情绪"
        :value="emotionLabel(sessionSummary.dominant_emotion)"
        :note="`置信度 ${formatPercent(sessionSummary.dominant_confidence || sessionSummary.confidence)}`"
        :tone="sessionSummary.risk_level || 'neutral'"
        icon="monitor"
        compact
      />
      <MetricCard
        label="负向情绪频次占比"
        :value="formatPercent(sessionSummary.negative_ratio)"
        note="超出 30% 触发风险关注"
        :tone="sessionSummary.negative_ratio >= 0.3 ? 'danger' : 'info'"
        icon="pie"
        compact
      />
      <MetricCard
        label="分析样本帧"
        :value="sessionSummary.analyzed_frames"
        unit="帧"
        :note="`总设计帧数 ${sessionSummary.total_frames} 帧`"
        tone="info"
        icon="video"
        compact
      />
    </div>

    <div class="review-grid">
      <div class="review-item">
        <span>情绪稳定性</span>
        <strong>{{ stabilityLabel(sessionSummary) }}</strong>
        <p>{{ stabilityText(sessionSummary) }}</p>
      </div>
      <div class="review-item">
        <span>复核优先级</span>
        <strong>{{ priorityLabel(sessionSummary) }}</strong>
        <p>{{ priorityText(sessionSummary) }}</p>
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
import MetricCard from '@/components/MetricCard.vue'
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

function stabilityLabel(summary) {
  if (summary.negative_ratio >= 0.45) return '波动明显'
  if (summary.negative_ratio >= 0.25) return '轻度波动'
  return '相对平稳'
}

function stabilityText(summary) {
  if (summary.negative_ratio >= 0.45) return '负向情绪占比偏高，建议结合会谈记录复核。'
  if (summary.negative_ratio >= 0.25) return '存在阶段性波动，可纳入近期观察。'
  return '未见明显连续负向信号。'
}

function priorityLabel(summary) {
  if (summary.risk_level === 'high') return '优先处理'
  if (summary.risk_level === 'medium') return '建议跟进'
  return '常规归档'
}

function priorityText(summary) {
  if (summary.risk_level === 'high') return '建议尽快完成线下沟通并记录处置结果。'
  if (summary.risk_level === 'medium') return '建议结合班级、测评和历史记录持续观察。'
  return '保持常规记录即可。'
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

.review-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.review-item {
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  background: var(--mh-surface);
}

.review-item span {
  display: block;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 650;
}

.review-item strong {
  display: block;
  margin-top: 6px;
  color: var(--mh-ink);
  font-size: 16px;
}

.review-item p {
  margin: 6px 0 0;
  color: var(--mh-text);
  font-size: 12px;
  line-height: 1.6;
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
  color: var(--mh-ink);
}

.el-divider {
  margin: 12px 0;
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .review-grid {
    grid-template-columns: 1fr;
  }
}
</style>
