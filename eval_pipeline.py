import os
import json
import re
from dotenv import load_dotenv
from neo4j import GraphDatabase, Query

load_dotenv()


class KGEvaluator:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def custom_retrieve(self, query_str: str, target_label: str, k: int = 5):
        """
        根据标签隔离进行自定义检索，返回按相关性得分降序排列的 Top-k 文本块。

        实现说明：
        - 将查询文本拆分为有意义的 token（按标点/空格切分，过滤长度 <= 1 的噪音）
        - 使用 Cypher 的 reduce 对每个 Chunk 累积 token 匹配得分，实现 ORDER BY 排序
        - 确保返回结果按照相关性从高到低排序，为 MRR 提供正确的 Rank 依据
        """
        # 将查询拆分为有意义的 token 用于相关性评分
        tokens = [
            t for t in re.split(
                r'[\s,，。；;：:()（）""''""\?？!！、/\\\\\[\]{}]+', query_str
            ) if len(t) > 1
        ]

        cypher = f"""
        MATCH (e:{target_label})-[:MENTIONS|HAS_CHUNK]->(c:Chunk)
        WHERE e.id CONTAINS $query_str
        WITH c,
             reduce(score = 0.0, token IN $tokens |
                 score + CASE WHEN c.text CONTAINS token THEN 1.0 ELSE 0.0 END
             ) AS relevance_score
        RETURN c.text AS text
        ORDER BY relevance_score DESC
        LIMIT $k
        """
        with self.driver.session() as session:
            result = session.run(Query(cypher), query_str=query_str, tokens=tokens, k=k)  # type: ignore[arg-type]
            return [record["text"] for record in result]

    def close(self):
        self.driver.close()


def evaluate_retrieval_metrics(eval_dataset: list, k: int = 5) -> dict:
    """
    评测管线核心函数：同时计算 Top-k Recall (%) 和 MRR (Mean Reciprocal Rank)。

    MRR 算法：
    - 对每条 query，遍历 Top-k 文本块（Rank 1 → k）
    - 检查每个文本块是否包含预期实体（忽略大小写的子串匹配，宽容策略：命中任一实体即停止）
    - 若在第 r 个文本块首次命中，该 query 的 MRR 贡献 = 1/r
    - 若 Top-k 均未命中，贡献 = 0
    - 最终 MRR = sum(贡献) / N（N 为数据集大小）

    返回字典：
      RawEntity Top-k Recall
      CleanEntity Top-k Recall
      RawEntity MRR
      CleanEntity MRR
    """
    evaluator = KGEvaluator()
    total = len(eval_dataset)

    raw_recall_hits = 0
    clean_recall_hits = 0
    raw_mrr_reciprocals = []
    clean_mrr_reciprocals = []

    for idx, item in enumerate(eval_dataset, start=1):
        query = item["query"]
        expected = item["expected_entities"]
        expected_lower = [e.lower() for e in expected]

        # ── RawEntity 评测 ─────────────────────────────────────
        raw_texts = evaluator.custom_retrieve(query, "RawEntity", k)

        # Top-k Recall (任意命中即认为该 query 被召回)
        raw_combined = " ".join(raw_texts).lower()
        raw_hit = any(entity in raw_combined for entity in expected_lower)
        if raw_hit:
            raw_recall_hits += 1

        # MRR
        raw_found = False
        for rank, text in enumerate(raw_texts, start=1):
            if any(entity in text.lower() for entity in expected_lower):
                raw_mrr_reciprocals.append(1.0 / rank)
                raw_found = True
                break
        if not raw_found:
            raw_mrr_reciprocals.append(0.0)

        # ── CleanEntity 评测 ────────────────────────────────────
        clean_texts = evaluator.custom_retrieve(query, "CleanEntity", k)

        clean_combined = " ".join(clean_texts).lower()
        clean_hit = any(entity in clean_combined for entity in expected_lower)
        if clean_hit:
            clean_recall_hits += 1

        clean_found = False
        for rank, text in enumerate(clean_texts, start=1):
            if any(entity in text.lower() for entity in expected_lower):
                clean_mrr_reciprocals.append(1.0 / rank)
                clean_found = True
                break
        if not clean_found:
            clean_mrr_reciprocals.append(0.0)

        # 实时进度打印
        if idx % 5 == 0 or idx == total:
            print(f"  ▸ 已评测 {idx}/{total} 条...")

    evaluator.close()

    # 聚合统计
    raw_recall = (raw_recall_hits / total) * 100
    clean_recall = (clean_recall_hits / total) * 100
    raw_mrr = sum(raw_mrr_reciprocals) / total
    clean_mrr = sum(clean_mrr_reciprocals) / total

    return {
        "RawEntity Top-k Recall": f"{raw_recall:.2f}%",
        "CleanEntity Top-k Recall": f"{clean_recall:.2f}%",
        "RawEntity MRR": round(raw_mrr, 4),
        "CleanEntity MRR": round(clean_mrr, 4),
    }


if __name__ == "__main__":
    with open("data/eval_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    TOTAL = len(dataset)
    K = 5

    print("=" * 62)
    print("  学术知识图谱检索评测管线  v2.0  (Recall + MRR)")
    print("=" * 62)
    print(f"  评测数据集: data/eval_dataset.json")
    print(f"  黄金 QA 对数: {TOTAL}")
    print(f"  Top-k 参数: k={K}")
    print(f"  MRR Alpha: 1/rank (宽容策略，命中任一实体)")
    print("-" * 62)

    results = evaluate_retrieval_metrics(dataset, k=K)

    print("\n  📊 评测报告")
    print(f"  ┌─────────────────────────────┬────────────────┐")
    print(f"  │ 指标                        │ 数值           │")
    print(f"  ├─────────────────────────────┼────────────────┤")
    rec_raw = results["RawEntity Top-k Recall"]
    rec_clean = results["CleanEntity Top-k Recall"]
    mrr_raw = results["RawEntity MRR"]
    mrr_clean = results["CleanEntity MRR"]
    print(f"  │ RawEntity Top-k Recall      │ {rec_raw:>14} │")
    print(f"  │ CleanEntity Top-k Recall    │ {rec_clean:>14} │")
    print(f"  │ RawEntity MRR              │ {mrr_raw:>14.4f} │")
    print(f"  │ CleanEntity MRR            │ {mrr_clean:>14.4f} │")
    print(f"  └─────────────────────────────┴────────────────┘")
    print("=" * 62)
    print("  评测完成 ✅")
