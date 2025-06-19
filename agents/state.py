from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.documents import Document

class PipelineState(BaseModel):
    company: str
    docs: Optional[List[Document]] = None
    events: Optional[List["Event"]] = None
    advisor_report: Optional["AdvisorOutput"] = None
    debug_logs: Dict[str, Any] = Field(default_factory=dict)

class Event(BaseModel):
    type: str
    title: str
    date: Optional[str] = None
    partners: Optional[str] = None
    deal_value: Optional[str] = None
    product_name: Optional[str] = None
    indication: Optional[str] = None
    development_stage: Optional[str] = None
    status: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    competitors: Optional[str] = None
    summary: str
    source_url: str

class AnalystOutput(BaseModel):
    events: List[Event]

class AdvisorOutput(BaseModel):
    google_trends: int
    key_insights: str
    key_takeaways: List[str]
    risks_and_opportunities: Dict[str, str]
    recommendations: List[str]
    conclusion: str

# Fix forward references for Pydantic
PipelineState.update_forward_refs()