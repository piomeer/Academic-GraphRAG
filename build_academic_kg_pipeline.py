import os
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor

print("🚀 正在启动跨语言 GraphRAG 学术处理引擎...\n")

# 1. 唤醒 DeepSeek 大脑
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_BASE = "https://api.deepseek.com/v1"

Settings.llm = OpenAILike(
    model="deepseek-chat",
    api_key=API_KEY,
    api_base=API_BASE,
    is_chat_model=True,
    context_window=8192,
    max_tokens=2048,
    timeout=120.0 # 处理几万字文献需要更多思考时间，调大超时限制
)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# 2. 连接 Neo4j
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD"),
    url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
)

# 3. 核心黑科技：跨语言实体抽取器
kg_extractor = SimpleLLMPathExtractor(
    llm=Settings.llm,
    max_paths_per_chunk=10,
    num_workers=4,
    # 🌟 就是这里！把 prompt_template 改成 extract_prompt
    extract_prompt=(
        "你是一个极其专业的知识图谱构建专家。\n"
        "请阅读以下英文文本，并提取出核心的知识图谱三元组 (实体1, 关系, 实体2)。\n"
        "【严格警告】你必须将所有的实体和关系翻译成准确的中文学术术语！不要输出任何英文！\n"
        "文本内容:\n{text}\n"
    )
)

print("📖 正在解析 PDF 文献，大模型开始进行跨语言图谱构建（可能需要几分钟，请静候）...")
documents = SimpleDirectoryReader("./data").load_data()

index = PropertyGraphIndex.from_documents(
    documents,
    property_graph_store=graph_store,
    kg_extractors=[kg_extractor], # 挂载跨语言抽取器
    show_progress=True,
)

# 4. 创建问答引擎
query_engine = index.as_query_engine(
    include_text=True,
    similarity_top_k=3
)

# 5. 用中文向你的英文文献提问！
# 你可以根据你放进去的论文，修改下面这个问题
question = "这篇文献提出了什么核心算法？它的主要创新点和解决的痛点是什么？"
print(f"\n🙋‍♂️ 你的问题: {question}")
print("🧠 正在穿透中英语言壁垒进行图谱推理...\n")
print("-" * 50)

response = query_engine.query(question)

print(f"🤖 学术引擎回答:\n{response.response}")
