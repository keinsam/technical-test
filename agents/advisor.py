import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from agents.analyst import Event
from agents.prompts import ADVISOR_PROMPT

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")  

class AdvisorOutput(BaseModel):
    """
    Represents the output of the advisor agent, containing business insights, risks, opportunities, and recommendations.
    """
    google_trends: int = Field(..., description="Google Trends score (0-100)")
    key_insights: str = Field(..., description="Key business/market insights")
    key_takeaways: List[str] = Field(..., description="Main takeaways")
    risks_and_opportunities: Dict[str, str] = Field(..., description="Keys: 'risks', 'opportunities'")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    conclusion: str = Field(..., description="High-level conclusion or summary")

# @tool
def generate_business_report(company: str,
                             events: List[Event],
                             debug_logs: Optional[Dict] = None
                             ) -> AdvisorOutput:
    """
    Generates a business advisory report based on structured events for a company.
    Args:
        company (str): The name of the company.
        events (List[Event]): List of structured events related to the company.
        debug_logs (Optional[Dict]): Dictionary to store debug information.
    Returns:
        AdvisorOutput: A structured output containing business insights, risks, opportunities, and recommendations.
    """
    events_json = [ev.dict() for ev in events]
    prompt = ChatPromptTemplate.from_template(ADVISOR_PROMPT)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=2048
    )
    parser = PydanticOutputParser(pydantic_object=AdvisorOutput)

    # 1. input -> dictionary
    dict_step = RunnableLambda(lambda x: {"company": x["company"], "events_json": x["events_json"]})
    # 2. events_json → prompt
    prompt_step = RunnableLambda(lambda x: prompt.format(company=x["company"], events_json=x["events_json"]))
    # 3. prompt → LLM output
    llm_step = llm
    # 4. LLM output → LLM content
    content_step = RunnableLambda(lambda x: x.content if hasattr(x, "content") else x)
    # 5. LLM content → Pydantic parser
    parser_step = parser
    
    # Assemble the chain
    chain = dict_step | prompt_step | llm_step | content_step | parser_step

    try:
        result = chain.invoke({"company": company, "events_json": events_json})
        if debug_logs is not None:
            debug_logs["Advisor Chain Result"] = str(result)
        return result
    except Exception as e:
        if debug_logs is not None:
            debug_logs["Advisor Parse Error"] = str(e)
        return None
