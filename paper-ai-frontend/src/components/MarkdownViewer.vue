<template>
  <div class="markdown-viewer" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  emptyText: {
    type: String,
    default: '暂无内容'
  }
})

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const renderedContent = computed(() => {
  const text = props.content?.trim()
  if (!text) {
    return `<p class="markdown-empty">${props.emptyText}</p>`
  }
  return md.render(text)
})
</script>

<style scoped>
.markdown-viewer {
  color: #263445;
  font-size: 14px;
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.markdown-viewer :deep(h1),
.markdown-viewer :deep(h2),
.markdown-viewer :deep(h3) {
  margin: 14px 0 8px;
  color: #1f2d3d;
  line-height: 1.4;
}

.markdown-viewer :deep(p) {
  margin: 8px 0;
}

.markdown-viewer :deep(ul),
.markdown-viewer :deep(ol) {
  padding-left: 22px;
  margin: 8px 0;
}

.markdown-viewer :deep(blockquote) {
  margin: 10px 0;
  padding: 8px 12px;
  border-left: 3px solid #409eff;
  background: #f5f9ff;
  color: #4b5563;
}

.markdown-viewer :deep(code) {
  padding: 2px 5px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #1f2937;
  font-family: Consolas, Monaco, monospace;
}

.markdown-viewer :deep(pre) {
  padding: 12px;
  border-radius: 6px;
  background: #f8fafc;
  overflow-x: auto;
}

.markdown-viewer :deep(.markdown-empty) {
  color: #909399;
}
</style>
