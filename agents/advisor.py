import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from typing import List, Dict
from pydantic import BaseModel, Field
from agents.prompts import ADVISOR_PROMPT

class AdvisorOutput(BaseModel):
    google_trends: int = Field(..., description="Google Trends score (0-100)")
    key_insights: str = Field(..., description="Key business/market insights")
    key_takeaways: List[str] = Field(..., description="Main takeaways")
    risks_and_opportunities: Dict[str, str] = Field(..., description="Keys: 'risks', 'opportunities'")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    conclusion: str = Field(..., description="High-level conclusion or summary")

def get_advisor_output(company, events, debug=False):
    debug_info = {}

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2048
    )
    events_json = [ev.dict() for ev in events]  # Pydantic Event objects -> dict
    prompt = ChatPromptTemplate.from_template(ADVISOR_PROMPT)
    parser = PydanticOutputParser(pydantic_object=AdvisorOutput)

    # Compose la chaîne advisor
    chain = (
        RunnableLambda(lambda x: prompt.format(company=x["company"], events_json=x["events_json"]))
        | llm
        | RunnableLambda(lambda x: x.content if hasattr(x, "content") else x)
        | parser
    )

    try:
        result = chain.invoke({"company": company, "events_json": events_json})
        if debug:
            debug_info["Advisor Chain Result"] = str(result)
        return result, debug_info
    except Exception as e:
        debug_info["Advisor Parse Error"] = str(e)
        return None, debug_info
