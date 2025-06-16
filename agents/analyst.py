import re
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

class PipelineUpdate(BaseModel):
    product_name: str = Field(description="Name of drug/therapy/device or 'none'")
    indication: str = Field(description="Indication/condition/target or 'none'")
    development_stage: str = Field(description="Phase (e.g. Phase II), or 'none'")
    status: str = Field(description="Status (e.g. positive topline results, FDA approval, etc.) or 'none'")
    date: str = Field(description="Date or 'none'")
    competitors: str = Field(description="Main competitors, comma-separated, or 'none'")
    summary: str = Field(description="Short summary or 'none'")

class AnalystOutput(BaseModel):
    deals: list[Deal]
    pipeline_updates: list[PipelineUpdate]
    competitors: list[str]
    google_trends: int
    summary: str

def preprocess_llm_json(llm_response):
    """
    - Supprime les commentaires style // et /* ... */
    - Supprime les virgules superflues en fin de liste/objet
    - Corrige la structure : stringifie 'competitors' si liste
    """
    # Remove // comments
    llm_response = re.sub(r'//.*', '', llm_response)
    # Remove /* ... */ comments
    llm_response = re.sub(r'/\*.*?\*/', '', llm_response, flags=re.DOTALL)
    # Remove trailing commas before } or ]
    llm_response = re.sub(r',(\s*[}\]])', r'\1', llm_response)
    try:
        data = json.loads(llm_response)
        # Corrige competitors dans deals
        if "deals" in data and isinstance(data["deals"], list):
            for deal in data["deals"]:
                if isinstance(deal.get("competitors"), list):
                    deal["competitors"] = ", ".join(deal["competitors"])
        # Corrige competitors dans pipeline_updates
        if "pipeline_updates" in data and isinstance(data["pipeline_updates"], list):
            for pipe in data["pipeline_updates"]:
                if isinstance(pipe.get("competitors"), list):
                    pipe["competitors"] = ", ".join(pipe["competitors"])
        return json.dumps(data)
    except Exception as e:
        # Pour debug, tu peux print ici
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
Given the following news/articles about {company}, extract **up to 3 unique, real business deals** (such as acquisitions, partnerships, out-licensing, joint-ventures, investments, etc) and **up to 3 pipeline updates** (product developments, clinical trial progress, regulatory milestones, etc).

For each deal, output:
- deal_name: string (the name or title of the deal)
- date: string (or 'none')
- partners: string (or 'none')
- deal_value: string (or 'none')
- development_stage: string (or 'none')
- moa: string (mechanism of action, or 'none')
- competitors: string (main competitors as a comma-separated string, or 'none')
- opportunity_score: integer (1-5, or 0 if nothing found)
- summary: string (short summary, or 'none')

For each pipeline update, output:
- product_name: string (name of the product or candidate)
- indication: string (disease/condition/target, or 'none')
- development_stage: string (phase or status, or 'none')
- status: string (e.g. 'FDA approval', 'positive topline', 'enrollment started', or 'none')
- date: string (or 'none')
- competitors: string (main competitors as a comma-separated string, or 'none')
- summary: string (short summary, or 'none')

If you do not find a field, write 'none'.
If there are no deals or no pipeline updates, output empty lists.

Then, suggest competitors as a list (outside the deals/updates), a Google Trends score (fake, no need to specify it is fake, e.g. 60/100), and a short, realistic summary.

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
      "competitors": "...",
      "opportunity_score": 0,
      "summary": "..."
    }}
  ],
  "pipeline_updates": [
    {{
      "product_name": "...",
      "indication": "...",
      "development_stage": "...",
      "status": "...",
      "date": "...",
      "competitors": "...",
      "summary": "..."
    }}
  ],
  "competitors": ["...", "..."],
  "google_trends": 0,
  "summary": "..."
}}

Absolutely no comments or text. Output only pure, valid JSON.
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
        # Sortie vide si erreur
        data = AnalystOutput(deals=[], pipeline_updates=[], competitors=[], google_trends=50, summary="No data found.")
        return data, debug_info