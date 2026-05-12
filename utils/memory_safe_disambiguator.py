import asyncio
import gc
import logging
import httpx
from typing import List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Disambiguator")

class AsyncEntityDisambiguator:
    def __init__(self, batch_size: int = 50):
        self.semaphore = asyncio.Semaphore(10)
        self.batch_size = batch_size

    async def _process_single_node(self, node: Any):
        async with self.semaphore:
            # 防御设计：带超时的模拟调用
            try:
                # 实际业务中这里会调用 embedding 和 neo4j 检索
                # 使用 asyncio.to_thread 包装同步操作
                return await asyncio.wait_for(asyncio.to_thread(lambda: node), timeout=5.0)
            except (asyncio.TimeoutError, Exception) as e:
                logger.error(f"Node processing failed: {e}")
                return node

    async def process_nodes_in_batches(self, nodes: List[Any]):
        """显式内存分块处理"""
        processed_nodes = []
        for i in range(0, len(nodes), self.batch_size):
            batch = nodes[i:i + self.batch_size]
            tasks = [self._process_single_node(node) for node in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_nodes.extend([r for r in results if not isinstance(r, Exception)])
            
            # 强制内存清理
            del batch
            del tasks
            del results
            gc.collect()
            logger.info(f"Processed batch {i // self.batch_size + 1}, GC collected.")
            
        return processed_nodes
