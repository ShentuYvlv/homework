# Lang RAG Knowledge Base (方案A)

这是一个本地知识库问答项目：把 `data/` 里的 Markdown 文档切分、向量化后写入本地 ChromaDB；用户提问时先向量检索 Top-k 片段，再把检索到的内容作为“背景资料”交给 Gemini 生成答案（RAG）。

本项目按 `流程计划.md` 的**方案 A：标准 RAG**落地，重点是“可复现、可落地、可排错”，适合给上级汇报与后续扩展为 API 服务。

---

## 架构概览（RAG 两条链路）

### Indexing / 入库（离线）
1. Loader：遍历 `data/` 读取 `.md`
2. Splitter：按 Markdown 标题 + 长度二次切分为 chunk
3. Embedding：使用 HuggingFace 本地模型（默认 `bge-m3`）生成向量
4. Store：写入本地 ChromaDB（持久化目录 `./chromadb`）

### Retrieval / 问答（在线）
1. Question：用户输入问题
2. Retrieve：Chroma 相似度检索 Top-k chunk
3. Prompt：把 chunk 拼成【背景资料】+【问题】
4. Generate：调用 Gemini 生成答案，并打印来源文件

---

## 用到的技术（给上司汇报版）

### LangChain（本项目核心）
- **Embeddings**：`langchain_huggingface.HuggingFaceEmbeddings`（HuggingFace 本地向量模型）
- **VectorStore**：Chroma 的 LangChain 封装（用于 `similarity_search`）
- **Text Splitters**：`MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter`
- **LLM**：`langchain_openai.ChatOpenAI`（走 Gemini 的 OpenAI 兼容接口）

### ChromaDB（本地向量数据库）
- 持久化到 `./chromadb/`，用于存储向量与元数据（如 `source`）

### HuggingFace / Sentence-Transformers
- 本地 embedding 模型（默认路径 `./models/Xorbits/bge-m3`）

### Gemini（LLM）
- 通过 **OpenAI 兼容协议**调用：
  - `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
  - `GEMINI_API_KEY=...`

### LangGraph
- **本项目方案A未使用 LangGraph**（那是方案B/Agent 才会引入）。

---

## 目录结构与文件说明

### 入口脚本
- `ingest.py`：入库脚本（读文件 -> 切分 -> embedding -> 写入 Chroma）
- `chat.py`：问答脚本（检索 Top-k -> 拼 prompt -> 调 Gemini -> 输出答案与来源）

### 配置与环境
- `config.py`：集中读取配置（数据目录、chroma 目录、embedding 模型、chunk 参数、top_k 等）
- `.env`：你的本地运行配置（**本项目优先读取并覆盖系统环境变量**）
- `.env.example`：环境变量模板
- `requirements.txt`：依赖清单

### 核心模块（`src/`）
- `src/loader.py`：扫描并加载 `data/**/*.md` 为 `Document`，写入 `metadata['source']`
- `src/splitter.py`：Markdown 标题切分 + 长度切分
- `src/embeddings.py`：构建 HuggingFace embedding
- `src/vector_store.py`：
  - `get_vector_store()`：连接 Chroma
  - `resolve_collection_name()`：当 `.env` 写错 collection 导致为空时，自动回退到“有数据”的 collection
- `src/rag.py`：把检索到的 `Document` 格式化为“背景资料”（含来源与标题层级）
- `src/llm.py`：构建 LLM（Gemini OpenAI 兼容接口 `ChatOpenAI`）

### 数据与存储
- `data/`：知识库 Markdown 文件
- `chromadb/`：Chroma 持久化目录（`chroma.sqlite3` + 分片目录）
- `models/`：本地 embedding 模型缓存（示例：`models/Xorbits/bge-m3`）
- `downModel.py`：使用 ModelScope 下载模型（可选）

### 参考/学习目录（可忽略）
- `lc和lc学习/`：你此前测试 LangChain/Gemini 调用方式的示例，不影响本项目主流程

---

## 快速开始

### 1) 配置 `.env`
复制模板并填入 Gemini key：

```bash
cp .env.example .env
```

关键变量：
- `GEMINI_API_KEY`：Gemini API Key
- `LLM_BASE_URL`：默认已是 `https://generativelanguage.googleapis.com/v1beta/openai/`
- `DATA_DIR`：默认 `./data`
- `CHROMA_DIR`：默认 `./chromadb`
- `CHROMA_COLLECTION`：默认建议 `kbase`（避免写错导致“查不到”）
- `EMBEDDING_MODEL`：默认 `./models/Xorbits/bge-m3`

### 2) 入库（一次/增量）
```bash
python ingest.py
```

你会看到 `Progress x/y` 输出；这一步会花时间（全量 chunk 多时更久）。

### 3) 问答
```bash
python chat.py
```

输入问题后会输出：
- 回答
- 检索命中的来源文件列表（用于溯源）

---

## 常见问题（排错）

### 1) “知识库中未找到相关信息”，但我确定文档里有
优先排查 **collection 配置是否写错/为空**：
- `.env` 的 `CHROMA_COLLECTION` 必须与入库一致
- `chat.py` 已做自动回退：如果配置的 collection 为空，会提示并改用同目录下有数据的 collection

### 2) `huggingface/tokenizers ... forked ...` 警告
这是 tokenizers 的并行提示，不影响功能；`chat.py` 已默认设置 `TOKENIZERS_PARALLELISM=false` 来降低噪音。

### 3) `LangChainDeprecationWarning: Chroma was deprecated`
这是 LangChain 的弃用提示，不影响功能。
如果你想消掉 warning，可安装 `langchain-chroma` 并让 `src/vector_store.py` 优先使用它。

---

## 下一步（可选）
- 增量入库：基于文件 hash/mtime 做更新与删除
- 更强检索：MMR、rerank（例如 bge-reranker）
- API 服务：FastAPI 封装为 HTTP 接口

