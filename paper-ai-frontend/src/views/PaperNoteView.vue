<template>
  <div class="note-page">
    <div class="page-header">
      <el-button @click="router.back()">返回</el-button>
      <div>
        <h2>阅读笔记</h2>
        <p>{{ getPaperTitle(paper) }}</p>
      </div>
    </div>

    <el-card class="section-card">
      <template #header>
        <span>生成阅读笔记</span>
      </template>
      <el-form label-position="top">
        <el-form-item label="笔记风格">
          <el-select v-model="noteStyle" filterable allow-create default-first-option class="style-select">
            <el-option v-for="option in styleOptions" :key="option" :label="option" :value="option" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="noteStyle"
            type="textarea"
            :rows="2"
            placeholder="也可以直接输入自定义阅读笔记风格"
          />
        </el-form-item>
        <el-button type="primary" :loading="generating" @click="handleGenerate">生成阅读笔记</el-button>
      </el-form>
    </el-card>

    <el-card v-if="latestNote" class="section-card">
      <template #header>
        <div class="card-header">
          <span>本次生成结果</span>
          <el-button size="small" @click="copyText(latestNote)">复制笔记内容</el-button>
        </div>
      </template>
      <MarkdownViewer :content="latestNote" />
    </el-card>

    <el-card v-loading="notesLoading" class="section-card">
      <template #header>
        <span>历史阅读笔记</span>
      </template>

      <el-empty v-if="!sortedNotes.length" description="暂无阅读笔记" />
      <div v-else class="notes-list">
        <el-card v-for="note in sortedNotes" :key="note.id || note.created_at || note.content" class="note-item">
          <template #header>
            <div class="card-header">
              <span>{{ note.note_style || note.style || '阅读笔记' }}</span>
              <div class="note-actions">
                <span>{{ formatDate(note.created_at || note.create_time) }}</span>
                <el-button size="small" @click="copyText(getNoteContent(note))">复制</el-button>
              </div>
            </div>
          </template>
          <MarkdownViewer :content="getNoteContent(note)" />
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import MarkdownViewer from '../components/MarkdownViewer.vue'
import { generateNote, getNotes, getPaperDetail } from '../api/paper'
import { formatDate, getPaperTitle, normalizeList, pickContent } from '../utils/format'

const route = useRoute()
const router = useRouter()

const defaultStyle = '适合研究生阅读笔记'
const styleOptions = ['适合研究生阅读笔记', '适合开题报告', '适合课堂汇报', '适合文献综述整理']

const paper = ref(null)
const notes = ref([])
const noteStyle = ref(defaultStyle)
const latestNote = ref('')
const generating = ref(false)
const notesLoading = ref(false)

const sortedNotes = computed(() => {
  return [...notes.value].sort((a, b) => {
    const aTime = new Date(a.created_at || a.create_time || 0).getTime()
    const bTime = new Date(b.created_at || b.create_time || 0).getTime()
    return bTime - aTime
  })
})

function getNoteContent(note) {
  return pickContent(note, ['content', 'note', 'note_content', 'result'])
}

async function loadPaper() {
  paper.value = await getPaperDetail(route.params.id)
}

async function loadNotes() {
  notesLoading.value = true
  try {
    const data = await getNotes(route.params.id)
    notes.value = normalizeList(data)
  } finally {
    notesLoading.value = false
  }
}

async function handleGenerate() {
  const style = noteStyle.value.trim() || defaultStyle
  noteStyle.value = style
  generating.value = true

  try {
    const data = await generateNote(route.params.id, style)
    latestNote.value = pickContent(data, ['content', 'note', 'note_content', 'result'])
    ElMessage.success('阅读笔记生成成功')
    await loadNotes()
  } finally {
    generating.value = false
  }
}

async function copyText(text) {
  if (!text) {
    ElMessage.warning('暂无可复制内容')
    return
  }

  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

onMounted(async () => {
  await Promise.all([loadPaper(), loadNotes()])
})
</script>

<style scoped>
.note-page {
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

.section-card,
.note-item {
  border-radius: 8px;
}

.style-select {
  width: 360px;
  max-width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.note-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}
</style>
