
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os

import json

# MODELES Pydantic
class Deal(BaseModel):
    deal_name: str = Field(description="Deal name/title or 'none'")
    date: str = Field(description="Date or 'none'")
    partners: str = Field(description="Deal partners or 'none'")
    deal_value: str = Field(description="Deal value or 'none'")
    development_stage: str = Field(description="e.g. 'Phase II', or 'none'")
    moa: str = Field(description="Mechanism of action or 'none'")
    competitors: str = Field(description="Main competitors as a single string, comma-separated, or 'none'")
    opportunity_score: int = Field(description="Score from 1 to 5, or 0")
    summary: str = Field(description="Short summary or 'none'")

class AnalystOutput(BaseModel):
    deals: list[Deal]
    competitors: list[str]
    google_trends: int
    summary: str

# FONCTION de pré-traitement JSON : stringifie les 'competitors' des deals si liste
def preprocess_llm_json(llm_response):
    """
    Corrige la structure : pour chaque deal, si competitors est une liste, on join en string.
    """
    try:
        data = json.loads(llm_response)
        if "deals" in data and isinstance(data["deals"], list):
            for deal in data["deals"]:
                if isinstance(deal.get("competitors"), list):
                    deal["competitors"] = ", ".join(deal["competitors"])
        return json.dumps(data)
    except Exception as e:
        # Si ce n'est pas du JSON (ou erreur), renvoie la chaîne brute
        return llm_response

def extract_deals(company, articles, debug=False):
    debug_info = {}
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=2048,
        openai_api_key=os.getenv("OPENAI_API_KEY"),  # Assurez-vous que la clé API est définie
    )
    context = ""
    for art in articles:
        context += f"Title: {art['title']}\nDate: {art.get('date','')}\nContent: {art['content']}\nSource: {art['url']}\n\n"

    prompt = ChatPromptTemplate.from_template("""
You are a professional biotech business analyst.
Given the following news/articles about {company}, extract **up to 3 unique, real business deals**.  

If you do not find a field, write 'none' (not N/A).
For each deal, output:
- deal_name: string (the name or title of the deal)
- date: string (or 'none')
- partners: string (or 'none')
- deal_value: string (or 'none')
- development_stage: string (or 'none')
- moa: string (mechanism of action, or 'none')
- competitors: string (main competitors as a comma-separated string, or 'none')  // <<<<<<<<<<<<<<
- opportunity_score: integer (1-5, or 0 if nothing found)
- summary: string (short summary, or 'none')

If there are no deals, output an empty deals list.

Then, suggest competitors as a list (outside the deals), a Google Trends score (fake if not found, e.g. 60/100), and a short, realistic summary.

Articles:
{context}

Output your answer in the following JSON format:
{{
  "deals": [
    {{
      "deal_name": "...",
      "date": "...",
      "partners": "...",
      "deal_value": "...",
      "development_stage": "...",
      "moa": "...",
      "competitors": "...",    // <--- comma-separated string!
      "opportunity_score": 0,
      "summary": "..."
    }}
  ],
  "competitors": ["...", "..."],     // <--- ici une liste
  "google_trends": 0,
  "summary": "..."
}}

Absolutely no comments or text. Output only pure, valid JSON. Comments or explanations will cause errors.
    """)

    parser = PydanticOutputParser(pydantic_object=AnalystOutput)
    full_prompt = prompt.format(company=company, context=context)
    format_instructions = parser.get_format_instructions()
    full_prompt_final = full_prompt + "\n" + format_instructions

    if debug:
        debug_info["LLM Prompt"] = full_prompt_final

    # --- LLM inference ---
    llm_response = llm.invoke(full_prompt_final).content

    if debug:
        debug_info["LLM Raw Response"] = llm_response

    # --- Prétraitement JSON ---
    llm_response_fixed = preprocess_llm_json(llm_response)
    if debug and llm_response != llm_response_fixed:
        debug_info["LLM Preprocessed JSON"] = llm_response_fixed

    # --- Parsing final ---
    try:
        data = parser.parse(llm_response_fixed)
        if debug:
            debug_info["Parsed Output"] = str(data)
        return data, debug_info
    except Exception as e:
        debug_info["Parse Error"] = str(e)
        # Optionnel : retourne une sortie vide mais loggée
        data = AnalystOutput(deals=[], competitors=[], google_trends=50, summary="No deals found.")
        return data, debug_info