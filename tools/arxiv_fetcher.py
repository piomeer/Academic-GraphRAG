import arxiv
from llama_index.core.tools import FunctionTool

def search_latest_arxiv(query: str, max_results: int = 3) -> str:
    """
    这个工具用于在本地知识图谱缺乏最新信息时，从外部 ArXiv 获取最新的学术文献摘要。
    
    Args:
        query (str): 学术关键词或查询语句。
        max_results (int): 返回的最大结果数量，默认为 3。
        
    Returns:
        str: 包含 Top N 论文标题、作者、发布日期和摘要的格式化纯文本字符串。
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for result in client.results(search):
        authors = ", ".join([author.name for author in result.authors])
        formatted_result = (
            f"标题: {result.title}\n"
            f"作者: {authors}\n"
            f"发布日期: {result.published.strftime('%Y-%m-%d')}\n"
            f"摘要: {result.summary}\n"
            f"{'-' * 40}"
        )
        results.append(formatted_result)
    
    if not results:
        return "未找到相关文献。"
        
    return "\n\n".join(results)

# 将函数暴露为 LlamaIndex 的 FunctionTool
arxiv_tool = FunctionTool.from_defaults(
    fn=search_latest_arxiv,
    name="arxiv_fetcher",
    description="从 ArXiv 检索最新的学术文献。当本地知识库无法回答前沿学术问题时，应优先调用此工具。"
)
