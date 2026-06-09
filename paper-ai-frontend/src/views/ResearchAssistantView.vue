<template>
  <div class="assistant-page">
    <section class="assistant-hero">
      <div class="hero-icon">
        <el-icon><MagicStick /></el-icon>
      </div>
      <div>
        <h2>智能科研助手</h2>
        <p>FastAPI 联网检索 OpenAlex 近期文献，Dify 负责把检索结果整理成中文科研建议。</p>
      </div>
      <el-button :icon="Refresh" :loading="historyLoading" round @click="loadMessages">刷新历史</el-button>
    </section>

    <section class="chat-shell">
      <div ref="messagesRef" class="messages">
        <div v-if="!messages.length && !loading" class="empty-state">
          <el-icon><Search /></el-icon>
          <h3>问一个科研问题</h3>
          <p>例如：帮我找出最近的相关故障诊断文献</p>
        </div>

        <div
          v-for="message in messages"
          :key="message.localId || message.id"
          class="message-row"
          :class="message.role"
        >
          <div v-if="message.role === 'assistant'" class="avatar assistant-avatar">
            <el-icon><Cpu /></el-icon>
          </div>

          <div class="message-block">
            <div class="message-bubble">
              <div class="message-meta">
                <span>{{ message.role === 'user' ? '我' : '科研助手' }}</span>
                <span v-if="message.create_time">{{ formatDate(message.create_time) }}</span>
              </div>
              <MarkdownViewer v-if="message.role === 'assistant'" :content="message.content" />
              <div v-else class="user-text">{{ message.content }}</div>
            </div>

            <div v-if="message.papers?.length" class="paper-results">
              <div class="result-title">
                <el-icon><Document /></el-icon>
                <span>相关论文</span>
              </div>
              <el-card v-for="paper in message.papers" :key="paper.url || paper.doi || paper.title" class="paper-card">
                <div class="paper-card-header">
                  <h3>{{ paper.title || '未命名论文' }}</h3>
                  <el-tag size="small" effect="plain">{{ paper.year || '年份未知' }}</el-tag>
                </div>
                <div class="paper-meta">
                  <span><el-icon><User /></el-icon>{{ formatAuthors(paper.authors) }}</span>
                  <span><el-icon><Collection /></el-icon>{{ paper.venue || '暂无期刊/会议信息' }}</span>
                  <span><el-icon><TrendCharts /></el-icon>引用量：{{ paper.cited_by_count || 0 }}</span>
                </div>
                <p class="paper-abstract">{{ paper.abstract || '暂无摘要' }}</p>
                <div class="paper-actions">
                  <el-button size="small" type="primary" plain :disabled="isSaved(paper)" @click="handleSavePaper(paper)">
                    <el-icon><Star /></el-icon>
                    {{ isSaved(paper) ? '已收藏' : '收藏' }}
                  </el-button>
                  <el-button v-if="paper.url" size="small" :icon="Link" @click="openPaperLink(paper.url)">打开链接</el-button>
                  <el-link v-if="paper.doi" :href="paper.doi" target="_blank" type="primary">{{ paper.doi }}</el-link>
                </div>
              </el-card>
            </div>
          </div>

          <div v-if="message.role === 'user'" class="avatar user-avatar">
            <el-icon><User /></el-icon>
          </div>
        </div>

        <div v-if="loading" class="message-row assistant">
          <div class="avatar assistant-avatar">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="message-block">
            <div class="message-bubble loading-bubble">
              <el-icon class="is-loading"><Loading /></el-icon>
              正在联网检索并分析...
            </div>
          </div>
        </div>
      </div>

      <div class="composer-wrap">
        <div class="quick-settings">
          <el-tag effect="plain">检索 {{ limit }} 篇</el-tag>
          <el-tag effect="plain">最近 {{ recentYears }} 年</el-tag>
          <el-popover placement="top" width="280" trigger="click">
            <template #reference>
              <el-button text :icon="Setting">检索设置</el-button>
            </template>
            <div class="settings-panel">
              <el-form-item label="检索数量">
                <el-input-number v-model="limit" :min="1" :max="20" />
              </el-form-item>
              <el-form-item label="最近年份">
                <el-input-number v-model="recentYears" :min="1" :max="10" />
              </el-form-item>
            </div>
          </el-popover>
        </div>

        <div class="composer">
          <el-icon class="composer-plus"><Plus /></el-icon>
          <el-input
            v-model="inputMessage"
            class="composer-input"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 5 }"
            maxlength="1000"
            placeholder="有问题，尽管问"
            @keydown.enter="handleEnter"
          />
          <el-button class="send-button" type="primary" circle :loading="loading" @click="sendMessage">
            <el-icon v-if="!loading"><Position /></el-icon>
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Collection,
  Cpu,
  Document,
  Link,
  Loading,
  MagicStick,
  Plus,
  Position,
  Refresh,
  Search,
  Setting,
  Star,
  TrendCharts,
  User
} from '@element-plus/icons-vue'
import MarkdownViewer from '../components/MarkdownViewer.vue'
import {
  chatWithResearchAssistant,
  getResearchAssistantMessages,
  getSavedResearchPapers,
  saveResearchPaper
} from '../api/researchAssistant'
import { formatDate, normalizeList } from '../utils/format'

const messages = ref([])
const savedPapers = ref([])
const inputMessage = ref('')
const messagesRef = ref(null)
const limit = ref(10)
const recentYears = ref(3)
const loading = ref(false)
const historyLoading = ref(false)

function formatAuthors(authors) {
  if (!Array.isArray(authors) || !authors.length) {
    return '暂无作者信息'
  }
  return authors.join('、')
}

function getPaperKey(paper) {
  return paper.doi || paper.url || paper.title
}

function isSaved(paper) {
  const key = getPaperKey(paper)
  return savedPapers.value.some((item) => getPaperKey(item) === key)
}

function handleEnter(event) {
  if (event.shiftKey) {
    return
  }
  event.preventDefault()
  sendMessage()
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text) {
    ElMessage.warning('请输入科研问题')
    return
  }

  messages.value.push({
    localId: `user-${Date.now()}`,
    role: 'user',
    content: text
  })
  await scrollToBottom()
  inputMessage.value = ''
  loading.value = true

  try {
    const data = await chatWithResearchAssistant({
      message: text,
      limit: limit.value,
      recent_years: recentYears.value
    })

    messages.value.push({
      localId: `assistant-${Date.now()}`,
      role: 'assistant',
      content: data.answer || '',
      papers: data.papers || []
    })
    await scrollToBottom()
    ElMessage.success('检索分析完成')
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function loadMessages() {
  historyLoading.value = true
  try {
    messages.value = normalizeList(await getResearchAssistantMessages())
    await scrollToBottom()
  } finally {
    historyLoading.value = false
  }
}

async function loadSavedPapers() {
  savedPapers.value = normalizeList(await getSavedResearchPapers())
}

async function handleSavePaper(paper) {
  const data = await saveResearchPaper(paper)
  if (!isSaved(data)) {
    savedPapers.value.unshift(data)
  }
  ElMessage.success(data?.__message || '收藏成功')
}

function openPaperLink(url) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

async function scrollToBottom() {
  await nextTick()
  const element = messagesRef.value
  if (element) {
    element.scrollTop = element.scrollHeight
  }
}

onMounted(async () => {
  await Promise.all([loadMessages(), loadSavedPapers()])
  await scrollToBottom()
})
</script>

<style scoped>
.assistant-page {
  display: flex;
  height: 100%;
  min-height: 0;
  flex-direction: column;
  margin: 0;
  padding: 26px 20px 24px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at 12% 10%, rgb(64 158 255 / 10%), transparent 30%),
    radial-gradient(circle at 88% 12%, rgb(103 194 58 / 10%), transparent 28%),
    #fbfcff;
}

.assistant-hero {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  max-width: 980px;
  margin: 0 auto 18px;
  gap: 16px;
}

.hero-icon {
  display: grid;
  width: 48px;
  height: 48px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 16px;
  background: #111827;
  color: #ffffff;
  font-size: 24px;
  box-shadow: 0 14px 34px rgb(17 24 39 / 18%);
}

.assistant-hero h2 {
  margin: 0 0 6px;
  color: #111827;
  font-size: 24px;
}

.assistant-hero p {
  margin: 0;
  color: #6b7280;
  line-height: 1.7;
}

.assistant-hero .el-button {
  margin-left: auto;
}

.chat-shell {
  display: flex;
  flex: 1;
  max-width: 980px;
  min-height: 0;
  width: 100%;
  margin: 0 auto;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 26px;
  background: rgb(255 255 255 / 86%);
  box-shadow: 0 24px 70px rgb(15 23 42 / 10%);
  backdrop-filter: blur(16px);
  overflow: hidden;
}

.messages {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  padding: 30px 28px 18px;
}

.empty-state {
  display: grid;
  min-height: 340px;
  place-items: center;
  align-content: center;
  color: #9ca3af;
  text-align: center;
}

.empty-state .el-icon {
  margin-bottom: 12px;
  color: #111827;
  font-size: 36px;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: #111827;
}

.empty-state p {
  margin: 0;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.avatar {
  display: grid;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
}

.assistant-avatar {
  background: #111827;
  color: #ffffff;
}

.user-avatar {
  background: #eff6ff;
  color: #2563eb;
}

.message-block {
  max-width: min(780px, 86%);
}

.message-bubble {
  padding: 16px 18px;
  border-radius: 20px;
  background: #ffffff;
  color: #111827;
  box-shadow: 0 8px 24px rgb(15 23 42 / 8%);
}

.message-row.user .message-bubble {
  border-top-right-radius: 8px;
  background: #f3f4f6;
  box-shadow: none;
}

.message-row.assistant .message-bubble {
  border-top-left-radius: 8px;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 8px;
  color: #9ca3af;
  font-size: 13px;
}

.user-text {
  white-space: pre-wrap;
  line-height: 1.75;
}

.loading-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
}

.paper-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #111827;
  font-weight: 700;
}

.paper-card {
  border-radius: 14px;
  border-color: #eef2f7;
}

.paper-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.paper-card h3 {
  margin: 0;
  color: #111827;
  font-size: 16px;
  line-height: 1.5;
}

.paper-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 10px 0;
  color: #6b7280;
  font-size: 13px;
}

.paper-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.paper-abstract {
  display: -webkit-box;
  margin: 0;
  color: #4b5563;
  line-height: 1.75;
  overflow: hidden;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

.paper-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}

.paper-actions .el-button .el-icon {
  margin-right: 4px;
}

.composer-wrap {
  flex: 0 0 auto;
  padding: 12px 18px 18px;
  border-top: 1px solid rgb(229 231 235 / 80%);
  background: linear-gradient(180deg, rgb(255 255 255 / 72%), #ffffff 42%);
}

.quick-settings {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 8px;
}

.settings-panel :deep(.el-form-item) {
  margin-bottom: 12px;
}

.composer {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  min-height: 58px;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 28px;
  background: #ffffff;
  box-shadow: 0 8px 30px rgb(15 23 42 / 10%);
}

.composer-plus {
  margin-bottom: 9px;
  color: #111827;
  font-size: 22px;
}

.composer-input {
  flex: 1;
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 36px !important;
  padding: 8px 0;
  border: none;
  box-shadow: none;
  resize: none;
  font-size: 15px;
}

.send-button {
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  margin-bottom: 0;
  background: #111827;
  border-color: #111827;
}

@media (max-width: 760px) {
  .assistant-page {
    height: 100%;
    min-height: 0;
    margin: 0;
    padding: 18px 12px 18px;
  }

  .assistant-hero {
    align-items: flex-start;
  }

  .assistant-hero .el-button {
    display: none;
  }

  .chat-shell {
    border-radius: 18px;
  }

  .messages {
    padding: 18px 14px;
  }

  .message-block {
    max-width: calc(100% - 44px);
  }

  .quick-settings {
    justify-content: flex-start;
  }
}
</style>
