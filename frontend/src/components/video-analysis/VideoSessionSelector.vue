<template>
  <el-card class="selector-card" shadow="never">
    <template #header>
      <div class="card-title">分析控制面板</div>
    </template>
    
    <el-form label-position="top">
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

      <!-- 视频检测提示 -->
      <div v-if="selectedStudentId" class="check-result-box">
        <el-alert
          v-if="checkResult === undefined"
          title="检测中..."
          type="info"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else-if="checkResult && checkResult.available"
          :title="`检测到视频文件：${checkResult.filename}`"
          type="success"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else
          :title="checkResult?.hint || '该学生暂无可分析的会话视频'"
          type="warning"
          :closable="false"
          show-icon
        />
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
</script>

<style scoped>
.selector-card {
  height: 100%;
}
.card-title {
  font-weight: 700;
  color: var(--mh-ink);
}
.slider-tip {
  font-size: 11px;
  color: var(--mh-muted);
  margin-top: 4px;
}
.check-result-box {
  margin: 16px 0;
}
.action-box {
  margin-top: 24px;
}
.start-btn {
  width: 100%;
  height: 40px;
}
</style>
