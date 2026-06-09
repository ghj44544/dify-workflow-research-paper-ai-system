# paper-ai-frontend

## 1. 项目介绍

`paper-ai-frontend` 是“基于 Dify Workflow 的科研文献智能分析系统”的 Vue 3 前端项目。前端只调用 FastAPI 后端接口，不直接访问 Dify，也不保存任何 Dify API Key。

系统支持论文上传、论文结构化信息展示、单篇论文智能问答、问答历史查看、阅读笔记生成与历史笔记管理。

## 2. 技术栈

- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios
- Pinia
- markdown-it

## 3. 目录结构

```text
src/
  main.js
  App.vue
  router/
    index.js
  api/
    request.js
    paper.js
  views/
    HomeView.vue
    PaperListView.vue
    PaperDetailView.vue
    PaperAskView.vue
    PaperNoteView.vue
  components/
    PaperUpload.vue
    PaperTable.vue
    MarkdownViewer.vue
    QaHistory.vue
  stores/
    paperStore.js
  utils/
    format.js
```

## 4. 安装依赖

```bash
npm install
```

## 5. 启动命令

```bash
npm run dev
```

启动后浏览器访问 Vite 输出的本地地址，通常是：

```text
http://localhost:5173
```

## 6. 后端地址配置

默认后端基础地址为：

```text
http://localhost:8000
```

配置位置：

```text
src/api/request.js
```

如果需要切换后端地址，可以在项目根目录创建 `.env`：

```text
VITE_API_BASE_URL=http://localhost:8000
```

## 7. 页面说明

- 首页 `/`：展示系统介绍、核心功能卡片和“开始使用”入口。
- 文献管理 `/papers`：上传 PDF、DOCX、TXT、MD 文件，查看论文列表，支持详情、问答、笔记和删除操作。
- 论文详情 `/papers/:id`：展示标题、作者、年份、关键词、研究问题、研究方法、数据集、实验指标、创新点、研究不足、结论、文件名、上传时间。
- 论文问答 `/papers/:id/ask`：输入问题并向后端发起问答请求，AI 回答和历史记录均支持 Markdown 渲染。
- 阅读笔记 `/papers/:id/notes`：选择或输入笔记风格，生成阅读笔记，支持复制内容和查看历史笔记。

## 8. 常见问题

### 后端未启动

如果后端服务没有运行，请求会提示：

```text
网络请求失败，请检查后端服务是否启动
```

请先启动 FastAPI 后端，并确认地址为 `http://localhost:8000`。

### 上传失败

请确认文件格式为 `.pdf`、`.docx`、`.txt` 或 `.md`，并确认后端 `/api/papers/upload` 接口可用。

### 页面为空

文献列表、问答历史、阅读笔记为空时会展示 Empty 组件。请先上传论文，或确认后端返回的数据在 `data` 字段中。

### 跨域问题

如果浏览器控制台出现 CORS 错误，请在 FastAPI 后端开启前端地址的跨域访问，例如允许 `http://localhost:5173`。
