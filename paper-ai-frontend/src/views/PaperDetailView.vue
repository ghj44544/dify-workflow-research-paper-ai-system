<template>
  <div class="page">
    <div class="page-header">
      <el-button @click="router.back()">返回</el-button>
      <h2>论文详情</h2>
    </div>

    <el-card v-loading="loading" class="detail-card">
      <el-empty v-if="!paper && !loading" description="未找到论文详情" />

      <template v-else>
        <h3>{{ getPaperTitle(paper) }}</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item v-for="item in detailItems" :key="item.label" :label="item.label">
            {{ item.value }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPaperDetail } from '../api/paper'
import { displayValue, formatDate, getAuthors, getPaperTitle } from '../utils/format'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const paper = ref(null)

const detailItems = computed(() => {
  const item = paper.value || {}
  return [
    { label: '标题', value: getPaperTitle(item) },
    { label: '作者', value: getAuthors(item) },
    { label: '年份', value: displayValue(item.year) },
    { label: '关键词', value: displayValue(item.keywords) },
    { label: '研究问题', value: displayValue(item.research_question || item.research_questions) },
    { label: '研究方法', value: displayValue(item.research_method || item.methodology || item.methods) },
    { label: '数据集', value: displayValue(item.dataset || item.datasets) },
    { label: '实验指标', value: displayValue(item.metrics || item.experimental_metrics) },
    { label: '创新点', value: displayValue(item.innovation || item.contributions || item.novelty) },
    { label: '研究不足', value: displayValue(item.limitations || item.shortcomings) },
    { label: '结论', value: displayValue(item.conclusion || item.conclusions) },
    { label: '文件名', value: displayValue(item.file_name || item.filename) },
    { label: '上传时间', value: formatDate(item.created_at || item.upload_time || item.uploaded_at) }
  ]
})

async function loadDetail() {
  loading.value = true
  try {
    paper.value = await getPaperDetail(route.params.id)
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
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
  gap: 14px;
}

.page-header h2 {
  margin: 0;
  color: #1f2d3d;
}

.detail-card {
  border-radius: 8px;
}

.detail-card h3 {
  margin: 0 0 18px;
  color: #303133;
  font-size: 20px;
}
</style>
