from examples import COMPANY_NEWS

def fetch_news(company, max_articles=3, debug=False, debug_logs=None):
    articles = COMPANY_NEWS.get(company, [])[:max_articles]
    for art in articles:
        if art.get("content") is None and art.get("content_file"):
            with open(art["content_file"], "r") as f:
                art["content"] = f.read()
    return articles