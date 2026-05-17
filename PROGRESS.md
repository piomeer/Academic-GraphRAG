# Academic-GraphRAG — 项目进度与开荒日志

> 自动生成于 2026-05-17 · 三层记忆系统开荒初始化
> 首席架构师: Cline (ACL 2025 算力解耦与跨语言知识图谱架构)

---

## 一、项目概述 (Project Overview)

**Academic-GraphRAG** 是一个面向复杂学术文献（如 Knowledge Graph Embedding 原理、公式与网络架构解析）的企业级 GraphRAG 落地架构。通过**算力解耦**（云端 DeepSeek-v4-pro 高认知推理 + 本地 BAAI/bge-small-zh-v1.5 极速向量化）、**跨语言图谱构建**（英文学术 PDF → 中文结构化三元组）与**双路混合检索**（Neo4j 图游走 + 向量相似度），解决传统 RAG 系统在长文本多跳推理中的幻觉问题。

### 技术栈

| 层级 | 技术选型 | 版本限制 |
|------|---------|---------|
| 语言 | Python | >= 3.11 |
| 框架 | LlamaIndex | PropertyGraphIndex, ReActAgent, FunctionTool |
| LLM | DeepSeek-v4-pro | 通过 OpenAILike 接口接入，API Base: `https://api.deepseek.com/v1` |
| Embedding | BAAI/bge-small-zh-v1.5 | 本地 HuggingFace 模型，镜像源: `hf-mirror.com` |
| 图数据库 | Neo4j | 需本地安装 Desktop + APOC 插件，URI: `bolt://127.0.0.1:7687` |
| 外部工具 | ArXiv API | 通过 `arxiv` Python 包接入 |
| 记忆系统 | MCP Memory Server | JSON 文件: `academic-memory.json` (L2 图谱层) |

### 项目结构

```
e:/data/GraphRAG/
├── .gitignore
├── .env                          # API Key 与数据库凭证
├── academic-memory.json          # L2 知识图谱记忆 (MCP Server)
├── PROGRESS.md                   # L3 项目进度文件 (本文件)
├── .clinerules                   # L1 宪法文件
├── SPEC.md                       # 规格文档 (待完善)
├── README.md                     # 项目自述文件
│
├── build_graph.py                # 基础版：读取 PDF → 构建 KG → 存入 Neo4j
├── build_academic_kg_pipeline.py # 进阶版：含实体消歧、跨语言抽取、双模式(raw/clean)
├── demo.py                       # 简化版：全链路演示
├── query_graph.py                # 从已有 Neo4j 加载图谱并查询
├── test_agent.py                 # ReActAgent 测试 (集成 arxiv 外部工具)
├── test_batch_size.py            # 批量大小测试
│
├── tools/
│   ├── __init__.py
│   └── arxiv_fetcher.py          # ArXiv 论文检索工具 (FunctionTool)
│
├── utils/
│   └── memory_safe_disambiguator.py  # 异步实体消歧器 (分批 + GC 安全)
│
├── scripts/
│   └── clean_neo4j.py            # Neo4j 数据清理脚本
│
├── data/
│   └── eval_dataset.json         # 评估数据集
└── eval_pipeline.py              # 评估流水线
```

---

## 二、当前进度 (Current Status)

### ✅ 已完成功能
- [x] **核心 KG 构建流水线**: `build_graph.py` 可读取 PDF → LLM 抽取三元组 → Neo4j 持久化
- [x] **跨语言抽取**: `build_academic_kg_pipeline.py` 实现英文 PDF → 中文三元组，支持 `raw` / `clean` 双模式
- [x] **实体消歧**: `AsyncEntityDisambiguator` 实现异步分批处理 + 显示内存回收
- [x] **Neo4j 拦截器**: `DisambiguatorWrapper` 代理 upsert 操作，自动打标签
- [x] **混合查询引擎**: 图游走 + 向量相似度，支持 `include_text=True`
- [x] **ReAct Agent**: 集成 arxiv 外部工具，可检索最新学术论文
- [x] **评估流水线**: `eval_pipeline.py` + `eval_dataset.json`
- [x] **L2 记忆层初始化**: MCP Memory Server 已连接，知识图谱文件 `academic-memory.json` 已存在

### ⚠️ 已知问题 / 待完善
- [ ] `requirements.txt` / `pyproject.toml` 缺失（依赖管理不完整）
- [ ] `.gitignore` 内容待确认（至少需忽略 `.env`, `.venv/`, `__pycache__/`）
- [ ] 未配置 CI/CD
- [ ] 缺少单元测试目录 `tests/`
- [ ] SPEC.md 内容为空，需补充架构规格文档
- [ ] 记忆系统 L2 图谱需要基于当前代码架构植入初始知识点

---

## 三、Active Task（当前活跃任务）

### 🔴 最高优先级: 三层记忆系统开荒初始化

**任务描述**:
作为项目首席架构师，运用本地文件读取权限，为 Academic-GraphRAG 自动构建三层记忆系统：

1. **L1 宪法层** (`/.clinerules`) ✅ **已完成**
   - 写入核心技术栈限制与版本约束
   - 写入 TKG 图谱演化与真值维护协议（Append-Only 机制）

2. **L2 图谱层** (`academic-memory.json` via MCP Server) **⬅️ 下一步任务**
   - 将当前项目架构、模块职责、技术决策注入 L2 知识图谱
   - 建立实体关系：项目 → 模块 → 功能 → 技术依赖

3. **L3 感知层** (`PROGRESS.md`) ✅ **已完成**
   - 本项目进度文件（当前文件）
   - 记录项目概述、结构、进度、活跃任务

**后续 Active Task 候选**:
- [ ] **L2 种子种植**: 使用 MCP `create_entities` 将项目核心架构写入记忆图谱
- [ ] **依赖清单生成**: 创建 `requirements.txt` 锁定所有依赖版本
- [ ] **SPEC 补全**: 将架构规格补全到 SPEC.md
- [ ] **单元测试框架**: 搭建 `tests/` 目录，写入 pytest 基础配置

---

> ⚡ **开荒指令**: 后续迭代请自动从 MCP Memory Server 加载 L2 记忆上下文，同步更新 L3 `PROGRESS.md`，并在 `.clinerules` 中严格执行 L1 宪法约束。
