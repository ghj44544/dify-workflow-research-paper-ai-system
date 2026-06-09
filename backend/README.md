# 基于 Dify Workflow 的科研文献智能分析系统 - 后端

这是一个 FastAPI 后端项目，用于对接已经在 Dify 中配置好的 3 个 Workflow：

- 科研文献问答助手
- 文献信息抽取助手
- 论文阅读笔记生成助手

后端负责论文文件上传、本地保存、调用 Dify Workflow、MySQL 数据持久化、问答历史和阅读笔记管理。

## 目录结构

```text
backend/
  app/
    main.py
    core/
      config.py
      database.py
    models/
      paper.py
      qa_record.py
      paper_note.py
      workflow_log.py
    schemas/
      paper.py
      qa_record.py
      paper_note.py
      common.py
    services/
      dify_service.py
      paper_service.py
    api/
      routes/
        paper_routes.py
        qa_routes.py
        note_routes.py
        health_routes.py
    utils/
      file_utils.py
  requirements.txt
  .env.example
  README.md
```

## 环境准备

- Python 3.10+
- MySQL 5.7+ 或 8.x
- 已可用的 Dify Workflow API Key

## 安装依赖

```bash
cd "E:\个人项目\基于 Dify Workflow 的科研文献智能分析系统\backend"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## .env 配置说明

复制 `.env.example` 为 `.env`，然后修改其中配置：

```bash
copy .env.example .env
```

需要配置的关键项：

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

API Key 不要写入代码，统一放在 `.env` 中。

## MySQL 建库 SQL

```sql
CREATE DATABASE IF NOT EXISTS paper_ai_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

应用启动时会自动创建 `paper`、`qa_record`、`paper_note`、`workflow_log` 表。

## 启动命令

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- 健康检查：http://localhost:8000/api/health
- Swagger 文档：http://localhost:8000/docs

## API 接口说明

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| POST | `/api/papers/upload` | 上传论文并自动抽取结构化信息 |
| GET | `/api/papers` | 获取论文列表 |
| GET | `/api/papers/{paper_id}` | 获取论文详情 |
| DELETE | `/api/papers/{paper_id}` | 删除论文及关联问答、笔记 |
| POST | `/api/papers/{paper_id}/ask` | 向论文提问 |
| GET | `/api/papers/{paper_id}/qa-records` | 获取问答历史 |
| POST | `/api/papers/{paper_id}/note` | 生成论文阅读笔记 |
| GET | `/api/papers/{paper_id}/notes` | 获取阅读笔记列表 |

问答请求示例：

```json
{
  "question": "这篇论文的创新点是什么？"
}
```

阅读笔记请求示例：

```json
{
  "note_style": "适合研究生阅读笔记"
}
```

## Dify Workflow 变量名要求

请确保 Dify Start 节点变量名与后端保持一致：

- 文献问答：`paper_file`、`question`
- 信息抽取：`paper_file`
- 阅读笔记：`paper_file`、`note_style`

后端会先调用 `/files/upload` 上传文件，再调用 `/workflows/run`，文件输入格式为：

```json
{
  "paper_file": {
    "type": "document",
    "transfer_method": "local_file",
    "upload_file_id": "Dify文件ID"
  }
}
```

## 常见问题排查

- `Dify API Key 未配置`：检查 `.env` 中 3 个 `DIFY_*_API_KEY` 是否已填写。
- `Dify 文件上传失败`：检查 `DIFY_BASE_URL`、Dify 服务地址、Workflow Key 权限和文件大小限制。
- `paper_id 不存在`：确认先调用上传接口，或通过 `/api/papers` 查看已有论文 ID。
- `本地文件不存在`：数据库中有记录，但 `uploads` 下文件被移动或删除了。
- 数据库连接失败：确认 MySQL 已启动、库已创建、`DATABASE_URL` 用户名密码正确。
- Dify 抽取结果未写入字段：检查 Workflow 输出是否为 JSON；如果无法解析，后端会保存基础论文信息并在 `workflow_log.error_message` 中记录原因。

## 文件作用说明

- `app/main.py`：FastAPI 应用入口、CORS、异常处理、路由注册、启动建表。
- `app/core/config.py`：统一读取 `.env` 配置。
- `app/core/database.py`：SQLAlchemy 引擎、Session 和建表逻辑。
- `app/models/`：数据库 ORM 模型。
- `app/schemas/`：Pydantic 请求和响应结构。
- `app/services/dify_service.py`：Dify 文件上传和 Workflow 调用封装。
- `app/services/paper_service.py`：论文、问答、笔记和 workflow 日志业务逻辑。
- `app/api/routes/`：HTTP API 路由。
- `app/utils/file_utils.py`：上传文件校验、保存和删除。

## 推荐运行顺序

1. 创建 MySQL 数据库。
2. 安装 Python 依赖。
3. 复制 `.env.example` 为 `.env`。
4. 在 `.env` 中配置数据库连接和 3 个 Dify Workflow API Key。
5. 执行 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`。
6. 打开 `http://localhost:8000/docs` 测试接口。
