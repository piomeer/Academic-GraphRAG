import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class KGEvaluator:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def custom_retrieve(self, query_str: str, target_label: str, k: int = 5):
        """
        根据标签隔离进行自定义检索，防止数据越界
        """
        cypher = f"""
        MATCH (e:{target_label})-[:MENTIONS|HAS_CHUNK]->(c:Chunk)
        WHERE e.id CONTAINS $query
        RETURN c.text AS text
        LIMIT $k
        """
        with self.driver.session() as session:
            result = session.run(cypher, query=query_str, k=k)
            return [record["text"] for record in result]

    def close(self):
        self.driver.close()

import json

def evaluate_top_k_recall(eval_dataset: list, k: int = 5) -> dict:
    evaluator = KGEvaluator()
    results = {"RawEntity": 0, "CleanEntity": 0}
    
    for item in eval_dataset:
        query = item["query"]
        expected = item["expected_entities"]
        
        for label in ["RawEntity", "CleanEntity"]:
            retrieved_texts = evaluator.custom_retrieve(query, label, k)
            combined_text = " ".join(retrieved_texts).lower()
            
            # 命中判定：忽略大小写的子串包含
            hit = any(entity.lower() in combined_text for entity in expected)
            if hit:
                results[label] += 1
                
    evaluator.close()
    
    total = len(eval_dataset)
    return {label: f"{(count / total) * 100:.2f}%" for label, count in results.items()}

if __name__ == "__main__":
    with open("data/eval_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    print("开始执行 Top-k 评测...")
    recall_results = evaluate_top_k_recall(dataset, k=5)
    print(f"评测结果: {recall_results}")
