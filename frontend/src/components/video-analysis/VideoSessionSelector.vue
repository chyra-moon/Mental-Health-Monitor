<template>
  <el-card class="selector-card" shadow="never">
    <template #header>
      <div class="card-title">分析控制面板</div>
    </template>
    
    <el-form class="selector-form" label-position="top">
      <el-form-item label="选择班级">
        <el-select
          :model-value="selectedClassId"
          @update:model-value="$emit('update:selectedClassId', $event); $emit('class-change')"
          placeholder="请选择班级"
        >
          <el-option
            v-for="item in classes"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="选择学生">
        <el-select
          :model-value="selectedStudentId"
          @update:model-value="$emit('update:selectedStudentId', $event); $emit('student-change', $event)"
          placeholder="请选择学生"
          :disabled="!selectedClassId"
        >
          <el-option
            v-for="item in filteredStudents"
            :key="item.id"
            :label="item.real_name || item.username"
            :value="item.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="分析抽帧数量">
        <el-slider
          :model-value="frameCount"
          @update:model-value="$emit('update:frameCount', $event)"
          :min="5"
          :max="40"
          :step="5"
          show-stops
        />
        <div class="slider-tip">推荐抽帧 20 帧，可在 5-40 帧间调节</div>
      </el-form-item>

      <div v-if="selectedStudentId" class="check-result-box">
        <div class="status-strip" :class="statusClass">
          <span class="status-dot"></span>
          <strong>{{ statusText }}</strong>
        </div>
      </div>

      <div class="action-box">
        <el-button
          :type="primaryButtonType === 'info' ? 'primary' : primaryButtonType"
          class="start-btn"
          :loading="primaryButtonLoading"
          :disabled="primaryButtonDisabled"
          @click="$emit('primary-action')"
        >
          {{ primaryButtonLabel }}
        </el-button>
      </div>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  selectedClassId: [Number, String],
  selectedStudentId: [Number, String],
  frameCount: {
    type: Number,
    default: 20
  },
  classes: {
    type: Array,
    default: () => []
  },
  students: {
    type: Array,
    default: () => []
  },
  checkResult: Object,
  videoDuration: Number,
  captureIntervalMs: Number,
  primaryButtonLabel: String,
  primaryButtonType: String,
  primaryButtonLoading: Boolean,
  primaryButtonDisabled: Boolean
})

defineEmits([
  'update:selectedClassId',
  'update:selectedStudentId',
  'update:frameCount',
  'class-change',
  'student-change',
  'primary-action'
])

const filteredStudents = computed(() => {
  if (!props.selectedClassId) return []
  return props.students.filter(student => student.class_id === props.selectedClassId)
})

const statusText = computed(() => {
  if (props.checkResult === undefined) return '正在准备'
  if (props.checkResult && props.checkResult.available) return '分析准备就绪'
  return '暂无可分析内容'
})

const statusClass = computed(() => {
  if (props.checkResult === undefined) return 'is-pending'
  if (props.checkResult && props.checkResult.available) return 'is-ready'
  return 'is-empty'
})
</script>

<style scoped>
.selector-card {
  height: 100%;
  overflow: hidden;
}

.selector-card :deep(.el-card__body) {
  height: calc(100% - 49px);
  overflow: hidden;
  padding: 12px 16px;
}

.selector-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.selector-card :deep(.el-form-item) {
  margin-bottom: 9px;
}
.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.slider-tip {
  font-size: 11px;
  color: var(--mh-muted);
  margin-top: 2px;
}
.check-result-box {
  margin: 2px 0 8px;
}

.status-strip {
  height: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border: 1px solid var(--mh-line);
  border-radius: var(--mh-radius-sm);
  background: #fbfbfc;
  color: var(--mh-text);
}

.status-strip strong {
  font-size: 12px;
  font-weight: 750;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--mh-muted);
}

.status-strip.is-ready {
  border-color: var(--mh-line-strong);
}

.status-strip.is-ready .status-dot {
  background: var(--mh-primary);
}

.status-strip.is-empty .status-dot {
  background: #b45309;
}
.action-box {
  margin-top: auto;
}
.start-btn {
  width: 100%;
  height: 40px;
}
</style>
