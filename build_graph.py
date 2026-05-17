import os
from dotenv import load_dotenv

load_dotenv()

# 🌟 核心破局点：设置 Hugging Face 国内镜像源！这行代码必须放在最前面！
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. 配置 DeepSeek API
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_BASE = "https://api.deepseek.com"

llm = OpenAI(
    model="deepseek-v4-pro",
    api_key=API_KEY,
    api_base=API_BASE,
    max_tokens=2048
)

# 2. 配置本地 Embedding 模型 (通过国内镜像极速下载)
print("正在通过国内镜像下载并加载本地向量模型...")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
Settings.llm = llm  # 将 DeepSeek 设置为全局默认 LLM

# 3. 连接本地的 Neo4j 图数据库
print("正在连接 Neo4j 数据库...")
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD"),
    url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
)

# 4. 加载刚才准备的测试文档
print("正在读取 data 文件夹下的文档...")
documents = SimpleDirectoryReader("./data").load_data()

# 5. 核心步骤：让大模型抽取三元组并构建图谱
print("🧠 大模型开始工作，正在提取实体和关系，请耐心等待...")
index = PropertyGraphIndex.from_documents(
    documents,
    property_graph_store=graph_store,
    show_progress=True,
)

print("🎉 知识图谱构建完成！数据已成功存入 Neo4j！")
