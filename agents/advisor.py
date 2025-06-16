from langchain.prompts import ChatPromptTemplate
from agents.prompts import ADVISOR_PROMPT
import json
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

class RisksAndOpportunities:
    risks: str
    opportunities: str

class AdvisorOutput:
    google_trends: int
    key_insights: str
    key_takeaways: list
    risks_and_opportunities: dict
    recommendations: list
    conclusion: str

def preprocess_llm_json(llm_response):
    import re
    llm_response = re.sub(r'//.*', '', llm_response)
    llm_response = re.sub(r'/\*.*?\*/', '', llm_response, flags=re.DOTALL)
    llm_response = re.sub(r',(\s*[}\]])', r'\1', llm_response)
    return llm_response

def get_advisor_output(company, events, debug=False):
    debug_info = {}
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2048
    )

    events_json = json.dumps([ev.dict() for ev in events], ensure_ascii=False, indent=2)
    prompt = ChatPromptTemplate.from_template(ADVISOR_PROMPT)
    full_prompt = prompt.format(company=company, events_json=events_json)

    if debug:
        debug_info["Advisor LLM Prompt"] = full_prompt

    llm_response = llm.invoke(full_prompt)
    if hasattr(llm_response, "content"):
        llm_response = llm_response.content
    llm_response_fixed = preprocess_llm_json(llm_response)


    if debug:
        debug_info["Advisor LLM Raw"] = llm_response
        debug_info["Advisor LLM Preprocessed"] = llm_response_fixed

    try:
        data = json.loads(llm_response_fixed)
        if debug:
            debug_info["Advisor Parsed"] = data
        return data, debug_info
    except Exception as e:
        debug_info["Advisor Parse Error"] = str(e)
        return None, debug_info
