<template>
  <div class="page student-home">
    <PageHeader
      eyebrow="学生端"
      title="我的心理状态概览"
      description="查看近期情绪检测、风险提醒和常用入口。"
    >
      <template #actions>
        <el-button type="primary" :icon="Camera" @click="router.push('/student/emotion')">开始检测</el-button>
      </template>
    </PageHeader>

    <div class="stats-grid three">
      <MetricCard label="累计检测" :value="records.length" unit="次" caption="来自图片识别和视频分析记录" accent="teal">
        <template #icon><Tickets /></template>
      </MetricCard>
      <MetricCard
        label="最近情绪"
        :value="latestRecord ? emotionLabel(latestRecord.dominant_emotion) : '-'"
        :caption="latestRecord ? formatTime(latestRecord.created_at) : '暂无检测记录'"
        accent="green"
      >
        <template #icon><Sunny /></template>
      </MetricCard>
      <MetricCard label="我的预警" :value="warnings.length" unit="条" caption="待关注风险提醒" accent="warm">
        <template #icon><Warning /></template>
      </MetricCard>
    </div>

    <section class="quick-entry">
      <button type="button" @click="router.push('/student/profile')">
        <User />
        <span>个人资料</span>
      </button>
      <button type="button" @click="router.push('/student/records')">
        <Tickets />
        <span>检测记录</span>
      </button>
      <button type="button" @click="router.push('/student/trend')">
        <TrendCharts />
        <span>趋势分析</span>
      </button>
    </section>

    <div class="dashboard-grid">
      <section class="business-panel">
        <div class="panel-title-row">
          <div>
            <h2>最近检测记录</h2>
            <p>按时间展示最近 5 条识别结果</p>
          </div>
        </div>
        <el-empty v-if="records.length === 0" description="暂无识别记录" />
        <div v-else class="activity-list">
          <article v-for="record in records.slice(0, 5)" :key="record.id" class="activity-item">
            <div class="activity-time">{{ formatTime(record.created_at) }}</div>
            <div class="activity-main">
              <strong>{{ emotionLabel(record.dominant_emotion) }}</strong>
              <span>置信度 {{ record.confidence == null ? '-' : `${(record.confidence * 100).toFixed(1)}%` }}</span>
            </div>
            <StatusBadge :type="record.risk_level" :label="riskLabel(record.risk_level)" />
          </article>
        </div>
      </section>

      <section class="business-panel warning-panel">
        <div class="panel-title-row">
          <div>
            <h2>风险提醒</h2>
            <p>系统检测到中高风险时会在这里提示</p>
          </div>
        </div>
        <el-empty v-if="warnings.length === 0" description="暂无风险预警" />
        <div v-else class="warning-list">
          <article v-for="warning in warnings.slice(0, 5)" :key="warning.id" class="warning-item">
            <div>
              <StatusBadge :type="warning.level" :label="riskLabel(warning.level)" />
              <p>{{ warning.reason || '系统检测到风险变化' }}</p>
            </div>
            <span>{{ formatTime(warning.created_at) }}</span>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Camera, Sunny, Tickets, TrendCharts, User, Warning } from '@element-plus/icons-vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { emotionLabel, formatTime, riskLabel } from '@/utils/presentation'
import http from '@/api/http'

const router = useRouter()
const records = ref([])
const warnings = ref([])

const latestRecord = computed(() => records.value[0] || null)

const loadData = async () => {
  const [recordsRes, warningsRes] = await Promise.all([http.get('/records/my'), http.get('/warnings/my')])
  records.value = recordsRes.data || []
  warnings.value = warningsRes.data || []
}

onMounted(loadData)
</script>

<style scoped>
.student-home {
  display: grid;
  gap: var(--mh-space-4);
}

.quick-entry {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--mh-space-3);
}

.quick-entry button {
  min-height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: var(--mh-surface);
  color: var(--mh-primary-dark);
  cursor: pointer;
  font: inherit;
  font-weight: 760;
  box-shadow: var(--mh-shadow-soft);
}

.quick-entry svg {
  width: 18px;
  height: 18px;
}

.activity-list,
.warning-list {
  display: grid;
  gap: 10px;
}

.activity-item {
  display: grid;
  grid-template-columns: 170px minmax(0, 1fr) auto;
  align-items: center;
  gap: var(--mh-space-3);
  padding: 12px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: var(--mh-surface-soft);
}

.activity-time {
  color: var(--mh-muted);
  font-size: 12px;
}

.activity-main {
  min-width: 0;
}

.activity-main strong {
  display: block;
  color: var(--mh-ink);
  font-size: 15px;
}

.activity-main span {
  color: var(--mh-muted);
  font-size: 12px;
}

.warning-panel {
  border-left: 5px solid var(--mh-warm);
}

.warning-item {
  display: grid;
  gap: 8px;
  padding: 13px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius);
  background: #fffaf2;
}

.warning-item p {
  margin: 8px 0 0;
  color: var(--mh-text);
  line-height: 1.6;
}

.warning-item > span {
  color: var(--mh-muted);
  font-size: 12px;
}

@media (max-width: 720px) {
  .quick-entry,
  .activity-item {
    grid-template-columns: 1fr;
  }
}
</style>
