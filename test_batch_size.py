import time
import numpy as np
from neo4j import GraphDatabase
import psutil
import os

# 配置连接信息
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB

def generate_data(batch_size):
    # 生成 1024 维的随机 float 数组
    return [{"embedding": np.random.rand(1024).tolist()} for _ in range(batch_size)]

def run_test():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    batch_sizes = [50, 100, 150, 200]
    
    print(f"{'Batch Size':<12} | {'Time (ms)':<12} | {'Memory (MB)':<12}")
    print("-" * 45)
    
    for size in batch_sizes:
        data = generate_data(size)
        
        # 记录开始内存
        mem_before = get_memory_usage()
        
        start_time = time.perf_counter()
        
        with driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "UNWIND $batch AS row CREATE (:Node {embedding: row.embedding})",
                    batch=data
                )
            )
            
        end_time = time.perf_counter()
        mem_after = get_memory_usage()
        
        duration_ms = (end_time - start_time) * 1000
        print(f"{size:<12} | {duration_ms:<12.2f} | {mem_after - mem_before:<12.2f}")
        
    driver.close()

if __name__ == "__main__":
    # 注意：此脚本仅为逻辑演示，运行前请确保 Neo4j 服务已启动
    print("脚本已就绪，请在 Neo4j 启动后运行。")
