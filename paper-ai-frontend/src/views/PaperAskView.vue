<template>
  <div class="ask-page">
    <div class="page-header">
      <el-button @click="router.back()">返回</el-button>
      <div>
        <h2>论文问答</h2>
        <p>{{ getPaperTitle(paper) }}</p>
      </div>
    </div>

    <el-card v-if="latestAnswer" class="latest-card">
      <template #header>
        <span>本次回答</span>
      </template>
      <MarkdownViewer :content="latestAnswer" />
    </el-card>

    <el-card v-loading="historyLoading" class="history-card">
      <template #header>
        <span>问答历史</span>
      </template>
      <QaHistory :records="records" />
    </el-card>

    <el-card class="ask-box">
      <el-input
        v-model="question"
        type="textarea"
        :rows="4"
        maxlength="1000"
        show-word-limit
        placeholder="请输入关于这篇论文的问题，例如：这篇论文的创新点是什么？"
      />
      <div class="ask-actions">
        <el-button type="primary" :loading="asking" @click="submitQuestion">发送问题</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import MarkdownViewer from '../components/MarkdownViewer.vue'
import QaHistory from '../components/QaHistory.vue'
import { askPaper, getPaperDetail, getQaRecords } from '../api/paper'
import { getPaperTitle, normalizeList, pickContent } from '../utils/format'

const route = useRoute()
const router = useRouter()

const paper = ref(null)
const records = ref([])
const question = ref('')
const latestAnswer = ref('')
const asking = ref(false)
const historyLoading = ref(false)

async function loadPaper() {
  paper.value = await getPaperDetail(route.params.id)
}

async function loadRecords() {
  historyLoading.value = true
  try {
    const data = await getQaRecords(route.params.id)
    records.value = normalizeList(data)
  } finally {
    historyLoading.value = false
  }
}

async function submitQuestion() {
  const text = question.value.trim()
  if (!text) {
    ElMessage.warning('问题不能为空')
    return
  }

  asking.value = true
  try {
    const data = await askPaper(route.params.id, text)
    latestAnswer.value = pickContent(data, ['answer', 'content', 'response', 'result'])
    question.value = ''
    ElMessage.success('问答完成')
    await loadRecords()
  } finally {
    asking.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadPaper(), loadRecords()])
})
</script>

<style scoped>
.ask-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-header h2 {
  margin: 0 0 4px;
  color: #1f2d3d;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.latest-card,
.history-card,
.ask-box {
  border-radius: 8px;
}

.ask-box {
  position: sticky;
  bottom: 16px;
  z-index: 2;
}

.ask-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
