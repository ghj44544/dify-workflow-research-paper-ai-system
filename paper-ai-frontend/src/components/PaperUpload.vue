<template>
  <el-upload
    class="paper-upload"
    drag
    :accept="acceptTypes"
    :show-file-list="false"
    :http-request="handleUpload"
    :before-upload="beforeUpload"
    :disabled="uploading"
  >
    <div class="upload-content">
      <div class="upload-title">{{ uploading ? '正在上传并抽取论文信息...' : '拖拽论文文件到此处或点击上传' }}</div>
      <div class="upload-tip">支持 PDF、DOCX、TXT、MD 文件</div>
      <el-button type="primary" :loading="uploading">选择文件</el-button>
    </div>
  </el-upload>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadPaper } from '../api/paper'

const emit = defineEmits(['uploaded'])

const uploading = ref(false)
const acceptTypes = '.pdf,.docx,.txt,.md'
const allowedExtensions = ['pdf', 'docx', 'txt', 'md']

function beforeUpload(file) {
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (!allowedExtensions.includes(extension)) {
    ElMessage.warning('仅支持上传 PDF、DOCX、TXT、MD 文件')
    return false
  }

  if (uploading.value) {
    ElMessage.warning('文件正在上传中，请稍候')
    return false
  }

  return true
}

async function handleUpload(options) {
  uploading.value = true
  try {
    const result = await uploadPaper(options.file)
    ElMessage.success(result?.__message || '论文上传成功，信息抽取已完成')
    emit('uploaded')
  } catch (error) {
    const message = error?.response?.data?.message || error?.message
    if (message) {
      ElMessage.error(message)
    }
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.paper-upload {
  width: 100%;
}

.upload-content {
  display: flex;
  min-height: 150px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.upload-title {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.upload-tip {
  color: #909399;
  font-size: 13px;
}
</style>
