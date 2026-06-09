<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>文献管理</h2>
        <p>上传论文并查看自动抽取后的文献信息。</p>
      </div>
      <el-button :loading="paperStore.loading" @click="loadPapers">刷新列表</el-button>
    </div>

    <el-card class="section-card">
      <template #header>
        <span>上传论文</span>
      </template>
      <PaperUpload @uploaded="loadPapers" />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <span>论文列表</span>
      </template>
      <div v-loading="paperStore.loading">
        <PaperTable
          :papers="paperStore.papers"
          @detail="goDetail"
          @ask="goAsk"
          @note="goNote"
          @delete="handleDelete"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaperUpload from '../components/PaperUpload.vue'
import PaperTable from '../components/PaperTable.vue'
import { deletePaper } from '../api/paper'
import { usePaperStore } from '../stores/paperStore'

const router = useRouter()
const paperStore = usePaperStore()

function getId(row) {
  return row.id || row.paper_id
}

async function loadPapers() {
  await paperStore.fetchPapers()
}

function goDetail(row) {
  router.push(`/papers/${getId(row)}`)
}

function goAsk(row) {
  router.push(`/papers/${getId(row)}/ask`)
}

function goNote(row) {
  router.push(`/papers/${getId(row)}/notes`)
}

async function handleDelete(row) {
  const id = getId(row)
  try {
    await ElMessageBox.confirm('删除后该论文及相关记录将不可恢复，确认删除吗？', '删除确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deletePaper(id)
    ElMessage.success('论文已删除')
    await loadPapers()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      throw error
    }
  }
}

onMounted(loadPapers)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 6px;
  color: #1f2d3d;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.section-card {
  border-radius: 8px;
}
</style>
