# 🕸️ Academic-GraphRAG: 基于算力解耦与跨语言知识图谱的智能检索系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-Framework-black)](https://www.llamaindex.ai/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_Chat-blue)](https://platform.deepseek.com/)
[![Neo4j](https://img.shields.io/badge/GraphDB-Neo4j-green)](https://neo4j.com/)

面向复杂学术文献（如 Knowledge Graph Embedding 原理、公式与网络架构解析）设计的企业级 GraphRAG 落地架构。通过算力解耦、跨语言图谱构建与双路混合检索，解决传统 RAG 系统在长文本多跳推理（Multi-hop Reasoning）中的幻觉问题。

## 💡 核心特性 (Features)

- **算力解耦架构 (Decoupled Compute)**
  - **云端高认知推理**：接入千亿参数级 `DeepSeek-Chat`，负责深度的实体识别与关系抽取。
  - **本地极速向量化**：端侧部署 `BAAI/bge-small-zh-v1.5` 开源 Embedding 模型，实现 API Token 消耗降低 90%+ 与核心语料数据隐私保护。
- **跨语言知识图谱 (Cross-lingual KG)**
  - 针对全英文学术文献（PDF格式），自动进行双语对齐与机器阅读理解，输出高纯度中文结构化三元组。
- **混合检索底座 (Hybrid Retrieval)**
  - 整合 **Neo4j 图数据库**（持久化图谱拓扑关系）与 **内存向量索引**，支持“图游走 + 向量相似度”双路召回。

## ⚙️ 系统架构 (Architecture)

1. **Document Ingestion**: 挂载 `SimpleDirectoryReader` 批量清洗学术 PDF。
2. **KG Extraction**: 重写 `OpenAILike` 接口突破框架模型校验，使用 `SimpleLLMPathExtractor` 约束提示词，进行跨语言三元组抽取。
3. **Graph Storage**: 数据流入 Neo4j 数据库，构建物理图谱。
4. **Query Engine**: 唤醒图谱索引，执行混合相似度计算，大模型结合上下文输出精准解答。

## 🚀 快速开始 (Quick Start)



### 1. 环境安装
git clone https://github.com/你的用户名/Academic-GraphRAG.git
cd Academic-GraphRAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 2. 依赖配置
系统依赖本地图数据库底座，请提前安装并启动 Neo4j Desktop，并确保已安装 APOC 插件。

### 3. 运行学术流水线
在 `data/` 目录下放入你的学术论文 PDF，并在代码中配置你的大模型 API Key。
python build_academic_kg_pipeline.py

