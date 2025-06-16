import requests
from bs4 import BeautifulSoup
from eval.examples import COMPANY_NEWS

def fetch_news(company):
    articles = []
    urls = COMPANY_NEWS.get(company, [])
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            # For MVP: get title and first paragraph
            title = soup.title.string if soup.title else url
            para = soup.find('p')
            snippet = para.text if para else ""
            articles.append({"url": url, "title": title, "snippet": snippet})
        except Exception as e:
            articles.append({"url": url, "title": "Fetch error", "snippet": str(e)})
    return articles
