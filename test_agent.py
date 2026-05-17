import os
import sys
import io
import asyncio

# 强制设置标准输出为 UTF-8，避免 Windows GBK 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.agent import ReActAgent
from tools import arxiv_tool

# 1. 加载环境变量
load_dotenv()

# 2. 初始化 DeepSeek LLM
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_BASE = "https://api.deepseek.com/v1"

llm = OpenAILike(
    model="deepseek-v4-pro",
    api_key=API_KEY,
    api_base=API_BASE,
    is_chat_model=True,
    context_window=8192,
    max_tokens=2048
)

# 3. 初始化 ReAct Agent
# 导入我们刚才写的 arxiv_tool
agent = ReActAgent(
    tools=[arxiv_tool], 
    llm=llm, 
    verbose=True,
)

# 4. 测试运行
test_query = "请帮我查一下 ArXiv 上关于 GraphRAG 最新的 3 篇论文，并总结它们的核心贡献。"

async def main():
    print(f"🚀 开始测试智能体，输入问题: {test_query}\n")
    
    handler = agent.run(user_msg=test_query)
    response = await handler
    
    print("\n" + "="*50)
    print("🤖 智能体最终回答:")
    print(response)
    print("="*50)
    
    return response

if __name__ == "__main__":
    asyncio.run(main())
