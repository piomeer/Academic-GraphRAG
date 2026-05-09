import os
from dotenv import load_dotenv

load_dotenv()

import json
import asyncio
from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, Settings
from llama_index.core.evaluation import generate_question_context_pairs
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

# 配置
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

Settings.llm = OpenAILike(
    model="deepseek-chat",
    api_key=API_KEY,
    api_base=API_BASE,
    is_chat_model=True,
    context_window=8192,
    max_tokens=2048
)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

async def generate_dataset():
    print("正在加载文档...")
    documents = SimpleDirectoryReader("./data").load_data()
    
    # 生成数据集
    print("正在生成 Ground Truth 数据集...")
    eval_dataset = await generate_question_context_pairs(
        documents[:10],  # 取前10篇
        llm=Settings.llm,
        num_questions_per_chunk=2
    )
    
    with open("eval_dataset.json", "w", encoding="utf-8") as f:
        json.dump(eval_dataset.dict(), f, ensure_ascii=False, indent=4)
    print("数据集已保存至 eval_dataset.json")
    return eval_dataset

def calculate_metrics(eval_dataset, retriever):
    print("开始评估检索器...")
    hit_rates = []
    mrrs = []
    
    queries = eval_dataset.queries
    relevant_docs = eval_dataset.relevant_docs
    
    for query_id, query_text in queries.items():
        # 检索 Top-5
        nodes = retriever.retrieve(query_text)
        retrieved_ids = [node.node.node_id for node in nodes[:5]]
        
        # 计算 Hit Rate
        ground_truth_ids = relevant_docs[query_id]
        hit = any(gt_id in retrieved_ids for gt_id in ground_truth_ids)
        hit_rates.append(1 if hit else 0)
        
        # 计算 MRR
        rank = next((i + 1 for i, nid in enumerate(retrieved_ids) if nid in ground_truth_ids), 0)
        mrrs.append(1 / rank if rank > 0 else 0)
        
    return sum(hit_rates) / len(hit_rates), sum(mrrs) / len(mrrs)

async def main():
    # 1. 生成数据
    if not os.path.exists("eval_dataset.json"):
        eval_dataset = await generate_dataset()
    else:
        with open("eval_dataset.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            from llama_index.core.evaluation import EmbeddingQAFinetuneDataset
            eval_dataset = EmbeddingQAFinetuneDataset.from_dict(data)

    # 2. 初始化检索器
    graph_store = Neo4jPropertyGraphStore(
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD"),
        url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
    )
    index = PropertyGraphIndex.from_existing(property_graph_store=graph_store)
    retriever = index.as_retriever(similarity_top_k=5)

    # 3. 计算指标
    hr, mrr = calculate_metrics(eval_dataset, retriever)
    print(f"\n评估结果:")
    print(f"Hit Rate@5: {hr:.4f}")
    print(f"MRR: {mrr:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
