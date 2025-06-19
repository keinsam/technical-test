from typing import List
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.documents import Document

from .state import PipelineState, AnalystOutput, AdvisorOutput, Event
from .prompts import ANALYST_PROMPT, ADVISOR_PROMPT
from .configuration import get_llm

# --- NODES / STEPS ---

def fetch_news_node(state: PipelineState) -> PipelineState:
    # Demo: mock fetch, replace with real scraping
    from examples import COMPANY_NEWS  # use your examples.py
    articles = COMPANY_NEWS.get(state.company, [])[:3]
    docs = []
    for art in articles:
        content = art.get("content")
        if content is None and art.get("content_file"):
            with open(art["content_file"], "r") as f:
                content = f.read()
        doc = Document(
            page_content=content or "",
            metadata={
                "title": art.get("title", ""),
                "date": art.get("date", ""),
                "url": art.get("url", "")
            }
        )
        docs.append(doc)
    state.docs = docs
    state.debug_logs["Fetched Documents"] = str(docs)
    return state

def docs_to_context(docs: List[Document]) -> str:
    context = ""
    for doc in docs:
        meta = doc.metadata
        context += f"Title: {meta.get('title')}\nDate: {meta.get('date','')}\nContent: {doc.page_content}\nSource: {meta.get('url')}\n\n"
    return context

def analyst_node(state: PipelineState) -> PipelineState:
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)
    llm = get_llm(model="gpt-4o-mini", temperature=0.1)
    parser = PydanticOutputParser(pydantic_object=AnalystOutput)
    context = docs_to_context(state.docs or [])
    formatted_prompt = prompt.format(company=state.company, context=context)
    # LLM call
    output = llm.invoke(formatted_prompt)
    content = output.content if hasattr(output, "content") else output
    result = parser.parse(content)
    state.events = result.events
    state.debug_logs["Analyst Output"] = str(result)
    return state

def advisor_node(state: PipelineState) -> PipelineState:
    prompt = ChatPromptTemplate.from_template(ADVISOR_PROMPT)
    llm = get_llm(model="gpt-4o-mini", temperature=0.3)
    parser = PydanticOutputParser(pydantic_object=AdvisorOutput)
    events_json = [ev.dict() for ev in (state.events or [])]
    formatted_prompt = prompt.format(company=state.company, events_json=events_json)
    # LLM call
    output = llm.invoke(formatted_prompt)
    content = output.content if hasattr(output, "content") else output
    result = parser.parse(content)
    state.advisor_report = result
    state.debug_logs["Advisor Output"] = str(result)
    return state

# --- LANGGRAPH DEFINITION ---

def build_graph():
    builder = StateGraph(PipelineState)

    builder.add_node("fetch_news", fetch_news_node)
    builder.add_node("analyze", analyst_node)
    builder.add_node("advise", advisor_node)

    # Transitions
    builder.set_entry_point("fetch_news")
    builder.add_edge("fetch_news", "analyze")
    builder.add_edge("analyze", "advise")
    builder.add_edge("advise", END)

    return builder.compile()