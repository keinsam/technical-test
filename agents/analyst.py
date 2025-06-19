import os
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from agents.prompts import ANALYST_PROMPT

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

class Event(BaseModel):
    """
    Represents an event extracted by the analyst agent.
    """
    type: str = Field(default=..., description="Type of event: 'deal', 'pipeline', or 'other'")
    title: str = Field(default=..., description="Title or name of the event")
    date: Optional[str] = Field(default=None, description="Date of the event in YYYY-MM-DD format")
    partners: Optional[str] = Field(default=None, description="Partners involved in the event")
    deal_value: Optional[str] = Field(default=None, description="Monetary value of the deal, if applicable")
    product_name: Optional[str] = Field(default=None, description="Name of the product involved in the event")
    indication: Optional[str] = Field(default=None, description="Medical indication or condition related to the event")
    development_stage: Optional[str] = Field(default=None, description="Development stage of the product or event")
    status: Optional[str] = Field(default=None, description="Current status of the event (e.g., 'ongoing', 'completed')")
    mechanism_of_action: Optional[str] = Field(default=None, description="Mechanism of action of the product or treatment involved in the event")
    competitors: Optional[str] = Field(default=None, description="Competitors related to the event or product")
    summary: str = Field(default=..., description="Long summary of the event")
    source_url: str = Field(default=..., description="URL of the article where the event was found")

class AnalystOutput(BaseModel):
    """
    Represents the output of the analyst agent, containing a list of events.
    """
    events: List[Event]

def docs_to_context(docs: List[Document]) -> str:
    """
    Converts a list of Document objects into a formatted context string.
    Each document's metadata and content are included in the context.
    """
    context = ""
    for doc in docs:
        meta = doc.metadata
        context += f"Title: {meta.get('title')}\nDate: {meta.get('date','')}\nContent: {doc.page_content}\nSource: {meta.get('url')}\n\n"
    return context

# @tool
def extract_events(
    company: str,
    docs: List[Document],
    debug_logs: Optional[dict] = None
    ) -> AnalystOutput:
    """
    Extracts events related to a company from a list of documents using an LLM.
    Args:
        company (str): The name of the company to analyze.
        docs (List[Document]): A list of Document objects containing the articles.
        debug_logs (dict): A dictionary to store debug information.
    Returns:
        AnalystOutput: A Pydantic model containing the extracted events.
    """
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=2048
    )
    parser = PydanticOutputParser(pydantic_object=AnalystOutput)

    # 1. input -> dictionary
    dict_step = RunnableLambda(lambda x: {"company": x["company"], "docs": x["docs"]})
    # 2. disctionary → context string
    context_step = RunnableLambda(lambda x: {"company": x["company"], "context": docs_to_context(x["docs"])})
    # 3. context string → prompt
    prompt_step = RunnableLambda(lambda x: prompt.format(company=x["company"], context=x["context"]))
    # 4. prompt → LLM output
    llm_step = llm
    # 5. LLM output → LLM content
    content_step = RunnableLambda(lambda x: x.content if hasattr(x, "content") else x)
    # 6. LLM content → Pydantic parser
    parser_step = parser

    # Assemble the chain
    chain = dict_step | context_step | prompt_step | llm_step | content_step | parser_step

    try:
        result = chain.invoke({"company": company, "docs": docs})
        if debug_logs is not None:
            debug_logs["Analyst Chain Result"] = str(result)
        return result
    except Exception as e:
        if debug_logs is not None:
            debug_logs["Analyst Parse Error"] = str(e)
        return None