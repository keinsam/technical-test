from langchain_core.documents import Document
from examples import COMPANY_NEWS

def fetch_news(company, max_articles=3, debug=False, debug_logs=None):
    articles = COMPANY_NEWS.get(company, [])[:max_articles]
    docs = []
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
    if debug and debug_logs is not None:
        debug_logs["Fetched Documents"] = str(docs)
    return docs