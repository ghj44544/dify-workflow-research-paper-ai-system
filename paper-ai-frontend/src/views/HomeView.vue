<template>
  <div class="home-view">
    <section class="hero">
      <div>
        <h1>科研文献智能分析系统</h1>
        <p>
          面向研究生与科研项目的文献分析前端，连接 FastAPI 后端，支持论文上传、信息抽取、
          智能问答、阅读笔记生成与历史记录管理。
        </p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/papers')">开始使用</el-button>
    </section>

    <section class="feature-grid">
      <el-card v-for="feature in features" :key="feature.title" class="feature-card">
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
      </el-card>
    </section>

    <section class="info-grid">
      <el-card class="info-card">
        <template #header>
          <span>技术栈</span>
        </template>
        <div class="tag-group">
          <el-tag v-for="item in techStack" :key="item" effect="plain">{{ item }}</el-tag>
        </div>
      </el-card>

      <el-card class="info-card">
        <template #header>
          <span>技术方案</span>
        </template>
        <el-steps direction="vertical" :active="4" finish-status="success">
          <el-step
            v-for="step in architectureSteps"
            :key="step.title"
            :title="step.title"
            :description="step.description"
          />
        </el-steps>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    title: '论文上传与信息抽取',
    description: '上传 PDF、DOCX、TXT 或 MD 文件，自动抽取标题、作者、年份、方法、结论等结构化信息。'
  },
  {
    title: '论文智能问答',
    description: '围绕单篇论文提出研究问题，获取基于论文内容的 Markdown 格式回答。'
  },
  {
    title: '阅读笔记生成',
    description: '按研究生阅读、开题报告、课堂汇报、文献综述等风格生成可复制的阅读笔记。'
  },
  {
    title: '问答历史管理',
    description: '自动保存每篇论文的问答记录，便于复盘关键问题与后续研究线索。'
  }
]

const techStack = [
  'Vue 3',
  'Vite',
  'Element Plus',
  'Vue Router',
  'Axios',
  'Pinia',
  'markdown-it',
  'FastAPI',
  'SQLAlchemy',
  'MySQL',
  'Dify Workflow'
]

const architectureSteps = [
  {
    title: '前端交互层',
    description: 'Vue 3 负责论文上传、列表管理、详情查看、问答输入和 Markdown 内容展示。'
  },
  {
    title: '后端服务层',
    description: 'FastAPI 统一提供 REST API，处理文件保存、数据库记录、异常提示和结果清洗。'
  },
  {
    title: '智能工作流层',
    description: '后端调用 Dify 的三个 Workflow，分别完成信息抽取、论文问答和阅读笔记生成。'
  },
  {
    title: '数据持久化层',
    description: 'MySQL 保存论文基础信息、问答历史、阅读笔记和 Workflow 调用日志。'
  }
]
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 36px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgb(31 45 61 / 6%);
}

.hero h1 {
  margin: 0 0 12px;
  color: #1f2d3d;
  font-size: 30px;
}

.hero p {
  max-width: 760px;
  margin: 0;
  color: #606266;
  font-size: 16px;
  line-height: 1.8;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.feature-card {
  border-radius: 8px;
}

.feature-card h3 {
  margin: 0 0 10px;
  color: #303133;
  font-size: 17px;
}

.feature-card p {
  margin: 0;
  color: #606266;
  line-height: 1.7;
}

.info-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.8fr) minmax(360px, 1.2fr);
  gap: 16px;
}

.info-card {
  border-radius: 8px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

@media (max-width: 1100px) {
  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
