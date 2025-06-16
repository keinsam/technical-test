import requests
from bs4 import BeautifulSoup
from examples import COMPANY_NEWS

def fetch_news(company, max_articles=3, debug=False, debug_logs=None):
    """
    Mock/simple crawler: récupère pour chaque URL le titre et le premier <p>.
    Si pas de <p>, prend la meta description. Si pas, content = ''.
    La date est toujours 'unknown' (ou peut être récupérée via balise meta).
    Debug: stocke toutes les étapes et résultats dans debug_logs (dict).
    """
    articles = []
    urls = COMPANY_NEWS.get(company, [])[:max_articles]
    if debug and debug_logs is not None:
        debug_logs["Fetched URLs"] = urls

    for idx, url in enumerate(urls):
        step_logs = {}
        try:
            step_logs["URL"] = url
            resp = requests.get(url, timeout=5)
            step_logs["HTTP status"] = resp.status_code
            soup = BeautifulSoup(resp.text, "html.parser")
            # Titre
            title = soup.title.string.strip() if soup.title else url
            step_logs["title"] = title

            # Premier vrai paragraphe
            para = soup.find('p')
            content = para.get_text(strip=True) if para else ""
            step_logs["first_paragraph"] = content

            # Si pas de <p>, on tente la meta description
            if not content:
                meta = soup.find("meta", attrs={"name": "description"})
                content = meta["content"] if meta and "content" in meta.attrs else ""
                step_logs["meta_description"] = content

            # Récupération de la date (si présente)
            date = ""
            meta_date = soup.find("meta", attrs={"property": "article:published_time"})
            if meta_date and meta_date.get("content"):
                date = meta_date["content"]
                step_logs["date_source"] = "property:article:published_time"
            else:
                meta_date = soup.find("meta", attrs={"name": "pubdate"})
                date = meta_date["content"] if meta_date and "content" in meta_date.attrs else "unknown"
                step_logs["date_source"] = "name:pubdate" if date != "unknown" else "unknown"
            step_logs["date"] = date

            article_dict = {
                "url": url,
                "title": title,
                "content": content,
                "date": date
            }
            articles.append(article_dict)
            step_logs["final_article"] = article_dict

        except Exception as e:
            step_logs["error"] = str(e)
            article_dict = {
                "url": url,
                "title": "Fetch error",
                "content": str(e),
                "date": "unknown"
            }
            articles.append(article_dict)
            step_logs["final_article"] = article_dict

        # Log chaque étape
        if debug and debug_logs is not None:
            debug_logs[f"Article_{idx}"] = step_logs

    if debug and debug_logs is not None:
        debug_logs["Fetched Articles (List)"] = articles

    return articles