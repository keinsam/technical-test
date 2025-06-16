from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import os

def extract_deals(company, articles):
    llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    context = ""
    for art in articles:
        context += f"Title: {art['title']}\nContent: {art['snippet']}\n\n"

    prompt = f"""
You are a biotech business analyst. Given the following news snippets about {company}, extract up to 3 recent, unique business deals.
For each deal, provide:
- Deal name or title
- Date (if found)
- Partner(s)
- Deal value (if mentioned)
- Development stage (e.g. 'Phase II')
- Mechanism of Action (MOA)
- Competitors (if mentioned)
- A 1-5 'opportunity score' for {company} (with reasoning)
- Short summary

Additionally, suggest a Google Trends score (mocked if needed, e.g. 60/100) for {company} in the last 3 months.

Output as a JSON object with these fields:
deals: [ {{}}, ... ], competitors: [], google_trends: int, summary: string
Content:
{context}
    """
    msg = [HumanMessage(content=prompt)]
    response = llm.invoke(msg)
    return response.content
