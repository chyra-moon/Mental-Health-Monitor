<template>
  <div class="page questionnaire-page">
    <PageHeader title="心理测评" />

    <div class="main-layout" v-loading="pageLoading">
      <div class="info-column">
        <el-card class="intro-card" shadow="never">
          <div class="intro-header">
            <el-icon class="intro-icon"><Document /></el-icon>
            <h3>学生心理健康自测问卷</h3>
          </div>
          <p class="intro-text">
            本测评基于量化心理评估指标开发，旨在帮助您快速掌握最近一周的整体心理状态。
          </p>
          <div class="questionnaire-meta">
            <div class="meta-item">
              <span class="meta-label">题目数量</span>
              <strong class="meta-value">8 题</strong>
            </div>
            <div class="meta-item">
              <span class="meta-label">预估时间</span>
              <strong class="meta-value">2 分钟</strong>
            </div>
            <div class="meta-item">
              <span class="meta-label">隐私保证</span>
              <strong class="meta-value">数据仅校内可用</strong>
            </div>
          </div>
          <div class="action-box">
            <el-button type="primary" size="large" class="start-btn" @click="startAssessment">
              开始心理测评
            </el-button>
          </div>
        </el-card>
      </div>

      <div class="history-column">
        <el-card class="history-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">历史测评记录</span>
            </div>
          </template>
          
          <el-table :data="historyRecords" stripe size="small" class="history-table">
            <el-table-column prop="created_at" label="测评时间" min-width="160">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="total_score" label="总得分" width="80" align="center">
              <template #default="{ row }">{{ row.total_score }} 分</template>
            </el-table-column>
            <el-table-column prop="risk_level" label="评估结果" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="riskType(row.risk_level)" size="small">
                  {{ riskLabel(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90" align="center" fixed="right">
              <template #default="{ row }">
                <el-button size="small" link type="primary" @click="viewDetail(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <el-card class="assessment-panel" shadow="never">
      <div class="panel-section score-section">
        <span class="panel-label">最近状态</span>
        <strong>{{ latestAssessmentText }}</strong>
        <p>{{ latestAssessmentNote }}</p>
      </div>
      <div class="panel-section dimension-section">
        <span class="panel-label">测评维度</span>
        <div class="dimension-list">
          <span v-for="item in assessmentDimensions" :key="item">{{ item }}</span>
        </div>
      </div>
      <div class="panel-section range-section">
        <span class="panel-label">关注区间</span>
        <div class="range-bars" aria-label="心理测评关注区间">
          <div class="range-item low"><span>低风险</span></div>
          <div class="range-item medium"><span>中风险</span></div>
          <div class="range-item high"><span>高风险</span></div>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="quizVisible"
      title="心理测评问卷"
      width="540px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-if="!showResult" class="quiz-container">
        <div class="quiz-progress">
          <div class="progress-info">
            <span>自测进度</span>
            <span>{{ currentStep + 1 }} / {{ questions.length }}</span>
          </div>
          <el-progress :percentage="Math.round(((currentStep + 1) / questions.length) * 100)" :show-text="false" />
        </div>

        <div class="question-box" v-if="questions[currentStep]">
          <h4 class="question-text">{{ questions[currentStep].text }}</h4>
          
          <el-radio-group v-model="answers[currentStep]" class="options-group" @change="handleOptionSelect">
            <el-radio 
              v-for="opt in options" 
              :key="opt.value" 
              :value="opt.value" 
              border 
              class="option-item"
            >
              {{ opt.label }}
            </el-radio>
          </el-radio-group>
        </div>

        <div class="quiz-actions">
          <el-button :disabled="currentStep === 0" @click="prevQuestion">上一题</el-button>
          <el-button 
            v-if="currentStep < questions.length - 1" 
            type="primary" 
            :disabled="answers[currentStep] === undefined" 
            @click="nextQuestion"
          >
            下一题
          </el-button>
          <el-button 
            v-else 
            type="primary" 
            :loading="submitting" 
            :disabled="answers[currentStep] === undefined" 
            @click="submitQuiz"
          >
            提交测评
          </el-button>
        </div>
      </div>

      <div v-else class="result-container">
        <div class="result-status">
          <div class="score-circle">
            <span class="score-num">{{ resultData.total_score }}</span>
            <span class="score-label">分</span>
          </div>
          <div class="result-badge">
            <el-tag :type="riskType(resultData.risk_level)" size="large" effect="dark">
              {{ riskLabel(resultData.risk_level) }}
            </el-tag>
          </div>
        </div>
        
        <div class="result-advice">
          <h5>系统指导建议：</h5>
          <p>{{ resultData.suggestion }}</p>
        </div>

        <div class="result-actions">
          <el-button type="primary" @click="finishQuiz">确认</el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      title="测评历史详情"
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedRecord" class="detail-container">
        <div class="detail-summary">
          <div class="sum-item">
            <span>测评时间</span>
            <strong>{{ formatTime(selectedRecord.created_at) }}</strong>
          </div>
          <div class="sum-item">
            <span>总得分</span>
            <strong>{{ selectedRecord.total_score }} 分</strong>
          </div>
          <div class="sum-item">
            <span>测评结果</span>
            <el-tag :type="riskType(selectedRecord.risk_level)">
              {{ riskLabel(selectedRecord.risk_level) }}
            </el-tag>
          </div>
        </div>

        <div class="detail-advice-box">
          <h5>系统调适建议：</h5>
          <p>{{ selectedRecord.suggestion || getFallbackSuggestion(selectedRecord) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getQuestions, submitAnswers } from '@/api/questionnaire'
import { formatTime, riskLabel, riskType } from '@/domain/mentalHealth'

const pageLoading = ref(false)
const quizVisible = ref(false)
const showResult = ref(false)
const submitting = ref(false)

const questions = ref([])
const options = ref([])
const answers = ref([])
const currentStep = ref(0)
const resultData = ref({})

const historyRecords = ref([])
const selectedRecord = ref(null)
const detailVisible = ref(false)

const assessmentDimensions = ['情绪波动', '睡眠质量', '压力负荷', '自我评价', '学习适应', '人际支持']
const latestAssessment = computed(() => historyRecords.value[0] || null)
const latestAssessmentText = computed(() => {
  if (!latestAssessment.value) return '暂无测评记录'
  return `${latestAssessment.value.total_score} 分 · ${riskLabel(latestAssessment.value.risk_level)}`
})
const latestAssessmentNote = computed(() => {
  if (!latestAssessment.value) return '完成一次测评后，这里会显示最近一次测评结果。'
  return `最近测评时间 ${formatTime(latestAssessment.value.created_at)}`
})

async function loadPageData() {
  pageLoading.value = true
  try {
    const res = await getQuestions()
    questions.value = res.data.questions || []
    options.value = res.data.options || []
    
    const localHistory = localStorage.getItem('questionnaire_history')
    if (localHistory) {
      historyRecords.value = JSON.parse(localHistory)
    } else {
      historyRecords.value = []
    }
  } catch (err) {
    ElMessage.error(err.message || '加载测评数据失败')
  } finally {
    pageLoading.value = false
  }
}

function startAssessment() {
  answers.value = Array(questions.value.length).fill(undefined)
  currentStep.value = 0
  showResult.value = false
  quizVisible.value = true
}

function prevQuestion() {
  if (currentStep.value > 0) currentStep.value--
}

function nextQuestion() {
  if (currentStep.value < questions.value.length - 1) currentStep.value++
}

function handleOptionSelect() {
  if (currentStep.value < questions.value.length - 1) {
    window.setTimeout(() => {
      if (!showResult.value && currentStep.value < questions.value.length - 1) {
        currentStep.value++
      }
    }, 140)
  }
}

async function submitQuiz() {
  submitting.value = true
  try {
    const rawAnswers = answers.value.map(val => Number(val))
    const res = await submitAnswers(rawAnswers)
    
    resultData.value = res.data
    showResult.value = true
    
    // 后端未提供历史查询接口，测评历史暂存浏览器本地。
    const newRecord = {
      id: `quiz-${Date.now()}`,
      created_at: new Date().toISOString(),
      total_score: res.data.total_score,
      risk_level: res.data.risk_level,
      suggestion: res.data.suggestion
    }
    historyRecords.value.unshift(newRecord)
    localStorage.setItem('questionnaire_history', JSON.stringify(historyRecords.value))
    
    ElMessage.success('测评提交成功')
  } catch (err) {
    ElMessage.error(err.message || '提交测评失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

function finishQuiz() {
  quizVisible.value = false
  showResult.value = false
}

function viewDetail(row) {
  selectedRecord.value = row
  detailVisible.value = true
}

function getFallbackSuggestion(record) {
  if (record.risk_level === 'high') {
    return '根据测评结果，目前您的压力或情绪波动较大。建议您前往校内心理中心或与辅导员联系，由专业心理老师为您提供更有针对性的线下支持。'
  }
  if (record.risk_level === 'medium') {
    return '根据测评结果，目前您存在轻度至中度的情绪波动或睡眠困扰。建议结合近期情绪识别记录观察自己的状态，适度放松、规律作息，必要时可主动预约校内辅导。'
  }
  return '根据测评结果，您的整体状态良好，暂无明显情绪波动或心理压力。建议保持健康作息与平衡的心态，规律进行状态自测与观察。'
}

onMounted(() => {
  loadPageData()
})
</script>

<style scoped>
.questionnaire-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 100%;
  height: 100%;
}

.main-layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 12px;
  align-items: stretch;
  flex: 1;
  min-height: 0;
}

.assessment-panel {
  flex: 0 0 auto;
}

.assessment-panel :deep(.el-card__body) {
  display: grid;
  grid-template-columns: 1fr 1.4fr 1.1fr;
  gap: 16px;
  align-items: stretch;
  padding: 16px 18px !important;
}

.panel-section {
  min-width: 0;
  padding: 0 16px;
  border-left: 1px solid var(--mh-line);
}

.panel-section:first-child {
  padding-left: 0;
  border-left: 0;
}

.panel-label {
  display: block;
  margin-bottom: 8px;
  color: var(--mh-muted);
  font-size: 11px;
  font-weight: 750;
}

.score-section strong {
  display: block;
  color: var(--mh-ink);
  font-size: 18px;
  font-weight: 850;
  line-height: 1.2;
}

.score-section p {
  margin: 8px 0 0;
  color: var(--mh-muted);
  font-size: 12px;
  line-height: 1.5;
}

.dimension-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dimension-list span {
  padding: 5px 8px;
  color: var(--mh-text);
  font-size: 12px;
  font-weight: 650;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: 5px;
}

.range-bars {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  height: 34px;
}

.range-item {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  border: 1px solid var(--mh-line);
}

.range-item span {
  font-size: 11.5px;
  font-weight: 750;
}

.range-item.low {
  color: var(--mh-ink);
  background: var(--mh-primary-soft);
}

.range-item.medium {
  color: var(--mh-warning);
  background: var(--mh-warning-soft);
}

.range-item.high {
  color: var(--mh-danger);
  background: var(--mh-danger-soft);
}

.intro-card {
  height: 100%;
}

.intro-card :deep(.el-card__body) {
  height: 100%;
}

.history-card :deep(.el-card__body) {
  height: calc(100% - 49px);
}

.intro-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.intro-icon {
  font-size: 24px;
  color: var(--mh-accent);
}

.intro-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--mh-ink);
}

.intro-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--mh-text);
  margin-bottom: 24px;
}

.questionnaire-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--mh-surface-muted);
  padding: 14px;
  border-radius: var(--mh-radius-md);
  margin-bottom: 24px;
  border: 1px solid var(--mh-line);
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.meta-label {
  color: var(--mh-muted);
}

.meta-value {
  color: var(--mh-ink);
  font-weight: 700;
}

.start-btn {
  width: 100%;
  height: 44px;
  font-weight: 700;
}

.history-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}

.history-table {
  margin-top: 4px;
}

.quiz-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quiz-progress {
  margin-bottom: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--mh-muted);
  margin-bottom: 6px;
  font-weight: 600;
}

.question-box {
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-lg);
  padding: 24px;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.question-text {
  margin: 0 0 20px;
  font-size: 15px;
  font-weight: 800;
  color: var(--mh-ink);
  line-height: 1.6;
  text-align: center;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  margin: 0 !important;
  width: 100%;
  height: auto;
  padding: 12px 16px !important;
  border-radius: var(--mh-radius-md);
  border-color: var(--mh-line) !important;
  display: flex;
  align-items: center;
}

.option-item.is-checked {
  border-color: var(--mh-primary) !important;
  background-color: var(--mh-primary-soft) !important;
}

.quiz-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.quiz-actions .el-button {
  min-width: 100px;
  height: 38px;
}

.result-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 20px 0;
}

.result-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--mh-primary-soft);
  border: 2px solid var(--mh-line-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--mh-ink);
}

.score-num {
  font-size: 32px;
  font-weight: 850;
}

.score-label {
  font-size: 12px;
  font-weight: 600;
  margin-left: 2px;
  margin-top: 10px;
}

.result-badge {
  transform: translateY(-4px);
}

.result-advice {
  width: 100%;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 16px;
}

.result-advice h5 {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}

.result-advice p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--mh-text);
}

.result-actions {
  width: 100%;
}

.result-actions .el-button {
  width: 100%;
  height: 40px;
  font-weight: 700;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  padding: 14px;
  border-radius: var(--mh-radius-md);
}

.sum-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;
}

.sum-item span {
  font-size: 11px;
  color: var(--mh-muted);
  font-weight: 600;
}

.sum-item strong {
  font-size: 13px;
  color: var(--mh-ink);
}

.detail-advice-box {
  background: var(--mh-surface-muted);
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-md);
  padding: 14px;
}

.detail-advice-box h5 {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 800;
  color: var(--mh-ink);
}

.detail-advice-box p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--mh-text);
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  .assessment-panel :deep(.el-card__body) {
    grid-template-columns: 1fr;
  }
  .panel-section {
    padding: 12px 0 0;
    border-top: 1px solid var(--mh-line);
    border-left: 0;
  }
  .panel-section:first-child {
    padding-top: 0;
    border-top: 0;
  }
}
</style>
