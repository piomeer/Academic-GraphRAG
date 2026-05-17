import os
from dotenv import load_dotenv

load_dotenv()

# 设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from llama_index.core import PropertyGraphIndex, Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 请替换为你的真实 Key

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

# 连接 Neo4j 记忆库
print("正在连接 Neo4j 记忆库...")
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD"),
    url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
)

# 加载图谱索引
print("正在加载图谱索引...")
index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
)

# 创建查询引擎
query_engine = index.as_query_engine(
    include_text=True,
    similarity_top_k=2
)

# 提问！
question = "RotatE 算法是谁提出的？它和 TransE 相比，有什么区别？"
print(f"\n🙋‍♂️ 你的问题: {question}")
print("🧠 大模型正在图谱中检索并思考，请稍候...\n")

response = query_engine.query(question)

# 🌟 修复 2：高阶工程技巧！打印出底层检索到的参考资料，看看系统是不是真的“没找到”
print("-" * 50)
print("🔍 [底层透视] 大模型从 Neo4j 检索到的参考资料：")
if len(response.source_nodes) == 0:
    print("【警告】检索系统什么都没找到！")
else:
    for i, node in enumerate(response.source_nodes):
        print(f"资料 {i+1}: {node.text}")
print("-" * 50)

print(f"\n🤖 大模型的回答:\n{response.response}")
