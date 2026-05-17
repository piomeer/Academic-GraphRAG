import os
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

print("🚀 正在启动 GraphRAG 智能问答系统...\n")

# 1. 配置 DeepSeek (大脑) 和 BAAI (眼睛)
API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 填入你的真实 Key
API_BASE = "https://api.deepseek.com/v1"

Settings.llm = OpenAILike(
    model="deepseek-v4-pro",
    api_key=API_KEY,
    api_base=API_BASE,
    is_chat_model=True,
    context_window=8192,
    max_tokens=2048
)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# 2. 连接 Neo4j 图数据库 (图谱记忆库)
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD"),
    url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
)

# 3. 一体化核心：阅读文件 -> 提取图谱 -> 保留在内存中供立即查询
print("📖 正在阅读 data 文件夹中的文档，并构建/更新知识图谱...")
documents = SimpleDirectoryReader("./data").load_data()

index = PropertyGraphIndex.from_documents(
    documents,
    property_graph_store=graph_store,
    show_progress=True,
)

# 4. 创建混合查询引擎
query_engine = index.as_query_engine(
    include_text=True,
    similarity_top_k=2
)

# 5. 终极提问！
question = "RotatE 算法是谁提出的？它和 TransE 相比，能处理哪些特殊的关系？"
print(f"\n🙋‍♂️ 用户提问: {question}")
print("🧠 正在结合知识图谱进行推理，请稍候...")
print("-" * 50)

response = query_engine.query(question)

print(f"🤖 GraphRAG 回答:\n{response.response}")
print("\n🎉 全链路跑通！恭喜你！")
