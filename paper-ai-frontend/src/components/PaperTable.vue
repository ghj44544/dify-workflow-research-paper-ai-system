<template>
  <el-empty v-if="!papers.length" description="暂无论文，请先上传文献" />

  <el-table v-else :data="papers" border stripe class="paper-table">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column label="标题" min-width="220">
      <template #default="{ row }">
        {{ getPaperTitle(row) }}
      </template>
    </el-table-column>
    <el-table-column label="作者" min-width="160">
      <template #default="{ row }">
        {{ getAuthors(row) }}
      </template>
    </el-table-column>
    <el-table-column label="年份" width="90">
      <template #default="{ row }">
        {{ displayValue(row.year) }}
      </template>
    </el-table-column>
    <el-table-column label="文件名" min-width="180">
      <template #default="{ row }">
        {{ displayValue(row.file_name || row.filename) }}
      </template>
    </el-table-column>
    <el-table-column label="上传时间" min-width="170">
      <template #default="{ row }">
        {{ formatDate(row.created_at || row.upload_time || row.uploaded_at) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="330" fixed="right">
      <template #default="{ row }">
        <el-space wrap>
          <el-button size="small" type="primary" @click="$emit('detail', row)">查看详情</el-button>
          <el-button size="small" type="success" @click="$emit('ask', row)">论文问答</el-button>
          <el-button size="small" type="warning" @click="$emit('note', row)">生成笔记</el-button>
          <el-button size="small" type="danger" @click="$emit('delete', row)">删除</el-button>
        </el-space>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { displayValue, formatDate, getAuthors, getPaperTitle } from '../utils/format'

defineProps({
  papers: {
    type: Array,
    default: () => []
  }
})

defineEmits(['detail', 'ask', 'note', 'delete'])
</script>

<style scoped>
.paper-table {
  width: 100%;
}
</style>
