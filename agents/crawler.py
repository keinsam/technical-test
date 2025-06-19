from typing import Optional, List
from langchain_core.documents import Document
from langchain_core.tools import tool
from examples import COMPANY_NEWS

# @tool
def fetch_news(company: str,
               max_articles: int = 3,
               debug_logs: Optional[dict] = None
               ) -> List[Document]:
    """
    Fetches news articles related to a company and returns them as Document objects.
    Args:
        company (str): The name of the company to fetch news for.
        max_articles (int): The maximum number of articles to fetch.
        debug_logs (dict): A dictionary to store debug information.
    Returns:
        List[Document]: A list of Document objects containing the articles.
    """
    articles = COMPANY_NEWS.get(company, [])[:max_articles]
    docs = []

    # For each article, create a Document object
    for art in articles:
        content = art.get("content")
        if content is None and art.get("content_file"):
            with open(art["content_file"], "r") as f:
                content = f.read()
        doc = Document(
            page_content=content or "",
            metadata={
                "title": art.get("title", ""),
                "date": art.get("date", ""),
                "url": art.get("url", "")
            }
        )
        docs.append(doc)
    
    if debug_logs is not None:
        debug_logs["Fetched Documents"] = str(docs)
    return docs