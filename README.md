# 基于 Dify Workflow 的科研文献智能分析系统

这是一个前后端分离的科研文献智能分析系统。系统使用 Vue 3 构建前端页面，FastAPI 提供后端接口，后端统一对接 Dify Workflow 完成论文信息抽取、论文问答和阅读笔记生成。

前端不会直接调用 Dify，也不会保存任何 Dify API Key。所有 Dify 调用都由后端完成。

## 项目结构

```text
dify-workflow-research-paper-ai-system/
  backend/              FastAPI 后端服务
  paper-ai-frontend/    Vue 3 + Vite 前端项目
```

## 技术栈

前端：

- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios
- Pinia
- markdown-it

后端：

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- httpx
- aiofiles
- PyMySQL
- MySQL

智能工作流：

- Dify Workflow
- 文件上传接口 `/files/upload`
- Workflow 运行接口 `/workflows/run`

## 技术方案

系统采用前后端分离架构：

```text
Vue 3 前端
   |
   | HTTP / Axios
   v
FastAPI 后端
   |
   | 保存上传文件、记录数据库、调用 Dify API
   v
Dify Workflow
   |
   | 返回 Markdown 或结构化结果
   v
FastAPI 清洗结果并入库
   |
   v
Vue 前端渲染 Markdown、表格和详情页
```

三个 Dify Workflow 分工：

- 文献信息抽取 Workflow：接收 `paper_file`，返回论文标题、作者、年份、关键词、研究问题、研究方法、数据集、指标、创新点、不足和结论。
- 论文问答 Workflow：接收 `paper_file` 和 `question`，返回基于论文内容的回答。
- 阅读笔记 Workflow：接收 `paper_file` 和 `note_style`，返回 Markdown 格式阅读笔记。

后端会先将本地论文上传到 Dify，得到 `upload_file_id`，再以单文件对象格式传给 Workflow：

```json
{
  "paper_file": {
    "type": "document",
    "transfer_method": "local_file",
    "upload_file_id": "Dify文件ID"
  }
}
```

## 功能说明

- 论文上传：支持 PDF、DOCX、TXT、MD。
- 信息抽取：上传后自动调用 Dify Workflow 抽取论文结构化信息。
- 文献管理：展示论文列表、详情、删除操作。
- 论文问答：围绕单篇论文提问，保存问答历史。
- 阅读笔记：按研究生阅读笔记、开题报告、课堂汇报、文献综述等风格生成 Markdown 笔记。
- Markdown 渲染：AI 回答和阅读笔记均使用 markdown-it 渲染。
- 输出清洗：后端会清理模型输出中的 `<think>...</think>`，避免推理过程展示给用户。

## 后端启动

进入后端目录：

```bash
cd backend
```

创建虚拟环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

复制环境变量模板：

```bash
copy .env.example .env
```

修改 `.env`：

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/paper_ai_system?charset=utf8mb4
DIFY_BASE_URL=http://localhost/v1
DIFY_QA_API_KEY=你的论文问答WorkflowKey
DIFY_EXTRACT_API_KEY=你的文献信息抽取WorkflowKey
DIFY_NOTE_API_KEY=你的阅读笔记WorkflowKey
UPLOAD_DIR=uploads
APP_NAME=科研文献智能分析系统
DEBUG=true
```

创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS paper_ai_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

启动后端：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

- 健康检查：http://localhost:8000/api/health
- Swagger 文档：http://localhost:8000/docs

## 前端启动

进入前端目录：

```bash
cd paper-ai-frontend
```

安装依赖：

```bash
npm install
```

启动开发服务：

```bash
npm run dev
```

默认前端地址：

```text
http://localhost:5173
```

默认后端地址：

```text
http://localhost:8000
```

如需修改后端地址，可在 `paper-ai-frontend/.env` 中配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| POST | `/api/papers/upload` | 上传论文并自动抽取信息 |
| GET | `/api/papers` | 获取论文列表 |
| GET | `/api/papers/{paper_id}` | 获取论文详情 |
| DELETE | `/api/papers/{paper_id}` | 删除论文 |
| POST | `/api/papers/{paper_id}/ask` | 向论文提问 |
| GET | `/api/papers/{paper_id}/qa-records` | 获取问答历史 |
| POST | `/api/papers/{paper_id}/note` | 生成阅读笔记 |
| GET | `/api/papers/{paper_id}/notes` | 获取阅读笔记列表 |

## 常见问题

### 上传后提示 Dify 调用失败

请检查：

- Dify 服务是否启动。
- `DIFY_BASE_URL` 是否正确，例如 `http://localhost/v1`。
- 三个 Workflow API Key 是否填写正确。
- Dify Start 节点变量名是否为 `paper_file`、`question`、`note_style`。
- `paper_file` 是否是单文件类型，而不是文件列表。

### 问答中出现 `{{question}}`

说明 Dify Workflow 的 LLM 节点 Prompt 中变量没有正确引用。后端已经传入 `question`，需要在 Dify 节点中使用正确的变量选择器，而不是把 `{{question}}` 当普通文本写死。

### 为什么不提交 `.env`、`node_modules`、`uploads`

`.env` 包含数据库和 Dify API Key，不能上传到公开仓库。`node_modules` 和 `uploads` 是本地运行产物，应通过安装依赖和上传文件动态生成。
