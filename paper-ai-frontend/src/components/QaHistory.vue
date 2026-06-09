<template>
  <div class="qa-history">
    <el-empty v-if="!sortedRecords.length" description="暂无问答历史" />

    <el-card v-for="record in sortedRecords" :key="record.id || record.created_at || record.question" class="qa-card">
      <template #header>
        <div class="qa-header">
          <span class="qa-label">用户问题</span>
          <span class="qa-time">{{ formatDate(record.created_at || record.create_time) }}</span>
        </div>
      </template>

      <div class="question">{{ record.question || record.user_question || '未提及' }}</div>
      <el-divider />
      <div class="answer-title">AI 回答</div>
      <MarkdownViewer :content="record.answer || record.ai_answer || record.response || ''" />
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownViewer from './MarkdownViewer.vue'
import { formatDate } from '../utils/format'

const props = defineProps({
  records: {
    type: Array,
    default: () => []
  }
})

const sortedRecords = computed(() => {
  return [...props.records].sort((a, b) => {
    const aTime = new Date(a.created_at || a.create_time || 0).getTime()
    const bTime = new Date(b.created_at || b.create_time || 0).getTime()
    return bTime - aTime
  })
})
</script>

<style scoped>
.qa-history {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-card {
  border-radius: 8px;
}

.qa-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.qa-label {
  color: #303133;
  font-weight: 600;
}

.qa-time {
  color: #909399;
  font-size: 13px;
}

.question {
  color: #303133;
  font-weight: 500;
  line-height: 1.7;
}

.answer-title {
  margin-bottom: 8px;
  color: #606266;
  font-weight: 600;
}
</style>
