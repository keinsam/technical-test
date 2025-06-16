import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from typing import Optional, List
from pydantic import BaseModel, Field
from agents.prompts import ANALYST_PROMPT

# MODELS
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

def docs_to_context(docs: List[Document]) -> str:
    context = ""
    for doc in docs:
        meta = doc.metadata
        context += f"Title: {meta.get('title')}\nDate: {meta.get('date','')}\nContent: {doc.page_content}\nSource: {meta.get('url')}\n\n"
    return context

# Full chain
def extract_events(company, docs, debug=False):
    debug_info = {}

    # Compose chain: docs → context → prompt → LLM → parse
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2048
    )
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)
    parser = PydanticOutputParser(pydantic_object=AnalystOutput)

    # 1. docs → context string
    docs_to_context_step = RunnableLambda(lambda x: docs_to_context(x["docs"]))

    # 2. context → prompt string
    prompt_step = RunnableLambda(lambda x: prompt.format(company=x["company"], context=x["context"]))

    # 3. prompt → LLM output
    # 4. LLM output → Pydantic parsing

    chain = (
        RunnableLambda(lambda x: {"company": x["company"], "docs": x["docs"]})
        | RunnableLambda(lambda x: {"company": x["company"], "context": docs_to_context(x["docs"])})
        | RunnableLambda(lambda x: prompt.format(company=x["company"], context=x["context"]))
        | llm
        | RunnableLambda(lambda x: x.content if hasattr(x, "content") else x)
        | parser
    )

    # Execution
    result = None
    try:
        result = chain.invoke({"company": company, "docs": docs})
        if debug:
            debug_info["Analyst Chain Result"] = str(result)
        return result, debug_info
    except Exception as e:
        debug_info["Analyst Parse Error"] = str(e)
        return AnalystOutput(events=[]), debug_info