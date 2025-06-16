from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import re
from agents.prompts import ANALYST_PROMPT
from langchain_openai import ChatOpenAI
import os

class Event(BaseModel):
    type: str = Field(description="Type of event: 'deal', 'pipeline', or 'other'")
    title: str = Field(description="Title or name of the event")
    date: Optional[str] = Field(default=None)
    partners: Optional[str] = Field(default=None)
    deal_value: Optional[str] = Field(default=None)
    product_name: Optional[str] = Field(default=None)
    indication: Optional[str] = Field(default=None)
    development_stage: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    mechanism_of_action: Optional[str] = Field(default=None)
    competitors: Optional[str] = Field(default=None)
    summary: str = Field(description="Long summary of the event")

class AnalystOutput(BaseModel):
    events: List[Event]

def preprocess_llm_json(llm_response):
    llm_response = re.sub(r'//.*', '', llm_response)
    llm_response = re.sub(r'/\*.*?\*/', '', llm_response, flags=re.DOTALL)
    llm_response = re.sub(r',(\s*[}\]])', r'\1', llm_response)
    try:
        data = json.loads(llm_response)
        if "events" in data and isinstance(data["events"], list):
            for ev in data["events"]:
                if isinstance(ev.get("competitors"), list):
                    ev["competitors"] = ", ".join(ev["competitors"])
        return json.dumps(data)
    except Exception:
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
    # format_instructions = parser.get_format_instructions()
    # full_prompt_final = full_prompt + "\n" + format_instructions
    full_prompt_final = prompt.format(company=company, context=context)

    if debug:
        debug_info["LLM Prompt"] = full_prompt_final

    llm_response = llm.invoke(full_prompt_final)
    if hasattr(llm_response, "content"):
        llm_response = llm_response.content

    if debug:
        debug_info["LLM Raw Response"] = llm_response

    llm_response_fixed = preprocess_llm_json(llm_response)
    if debug and llm_response != llm_response_fixed:
        debug_info["LLM Preprocessed JSON"] = llm_response_fixed

    try:
        data = parser.parse(llm_response_fixed)
        if debug:
            debug_info["Parsed Output"] = str(data)
        return data, debug_info
    except Exception as e:
        debug_info["Parse Error"] = str(e)
        data = AnalystOutput(events=[])
        return data, debug_info
