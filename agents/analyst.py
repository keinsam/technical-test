import re
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
import os

import json

# MODELES Pydantic
class Event(BaseModel):
    type: str = Field(description="Type of event: 'deal', 'pipeline', or 'other'")
    title: str = Field(description="Title or name of the event")
    date: Optional[str] = Field(default=None, description="Date if any")
    partners: Optional[str] = Field(default=None, description="Partners involved (for deals), if any")
    deal_value: Optional[str] = Field(default=None, description="Deal value (for deals), if any")
    product_name: Optional[str] = Field(default=None, description="Product/Drug name (for pipeline), if any")
    indication: Optional[str] = Field(default=None, description="Indication/target (for pipeline), if any")
    development_stage: Optional[str] = Field(default=None, description="Development stage, if any")
    status: Optional[str] = Field(default=None, description="Status update (for pipeline), if any")
    mechanism_of_action: Optional[str] = Field(default=None, description="Mechanism Of Action, if any")
    competitors: Optional[str] = Field(default=None, description="Main competitors, comma-separated, if any")
    opportunity_score: Optional[int] = Field(default=None, description="Score from 1 to 5 or 0")
    summary: str = Field(description="Short summary or description")

class AnalystOutput(BaseModel):
    events: List[Event]
    competitors: List[str]
    google_trends: int
    summary: str


# FONCTION de pré-traitement JSON : stringifie les 'competitors' des deals si liste
def preprocess_llm_json(llm_response):
    # Remove // comments
    llm_response = re.sub(r'//.*', '', llm_response)
    # Remove /* ... */ comments
    llm_response = re.sub(r'/\*.*?\*/', '', llm_response, flags=re.DOTALL)
    # Remove trailing commas before } or ]
    llm_response = re.sub(r',(\s*[}\]])', r'\1', llm_response)
    try:
        data = json.loads(llm_response)
        # Corrige competitors si jamais c'est une liste
        if "events" in data and isinstance(data["events"], list):
            for ev in data["events"]:
                if isinstance(ev.get("competitors"), list):
                    ev["competitors"] = ", ".join(ev["competitors"])
        return json.dumps(data)
    except Exception as e:
        return llm_response

def extract_events(company, articles, debug=False):
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
Given the following news/articles about {company}, extract up to 6 significant, unique events, each of type "deal", "pipeline", or "other".
For each event, classify it as:
- type: "deal" (business deals: acquisition, partnership, out-licensing, joint-venture, investment, etc)
- type: "pipeline" (product developments, clinical trial progress, regulatory milestones, etc)
- type: "other" (other significant news not fitting the above)

For each event, output:
- type: "deal", "pipeline", or "other"
- title: string (title or name of the event)
- date: string (or 'none')
- partners: string (if any, or 'none')
- deal_value: string (if any, or 'none')
- product_name: string (if any, or 'none')
- indication: string (if any, or 'none')
- development_stage: string (if any, or 'none')
- status: string (if any, or 'none')
- mechanism_of_action: string (if any, or 'none')
- competitors: string (main competitors as a comma-separated string, or 'none')
- opportunity_score: integer (1-5, or 0 if nothing found)
- summary: string (short summary, or 'none')

If you do not find a field, write 'none'.
If there are no relevant events, output an empty list.

Then, suggest main competitors as a list (outside events), a Google Trends score (fake if needed, e.g. 60/100), and a short, realistic summary.

Articles:
{context}

Output your answer in the following JSON format:
{{
  "events": [
    {{
      "type": "...",
      "title": "...",
      "date": "...",
      "partners": "...",
      "deal_value": "...",
      "product_name": "...",
      "indication": "...",
      "development_stage": "...",
      "status": "...",
      "mechanism_of_action": "...",
      "competitors": "...",
      "opportunity_score": 0,
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
        data = AnalystOutput(events=[], competitors=[], google_trends=50, summary="No data found.")
        return data, debug_info