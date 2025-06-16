import re
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import json
from agents.prompts import ANALYST_PROMPT

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

class RisksAndOpportunities(BaseModel):
    risks: str
    opportunities: str

class AnalystOutput(BaseModel):
    events: List[Event]
    google_trends: int
    key_insights: str
    key_takeaways: List[str]
    risks_and_opportunities: RisksAndOpportunities
    recommendations: List[str]
    conclusion: str



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

    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)

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
        data = AnalystOutput(
            events=[],
            google_trends=50,
            key_insights="No data found.",
            key_takeaways=[],
            risks_and_opportunities=RisksAndOpportunities(risks="No data", opportunities="No data"),
            recommendations=[],
            conclusion="No data found."
        )
        return data, debug_info