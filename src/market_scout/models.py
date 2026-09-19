from pydantic import BaseModel
from typing import List


class Source(BaseModel):
    title: str
    url: str


class CompanyResearch(BaseModel):
    ticker: str
    company_name: str

    period_return: float
    volatility: float
    sharpe_ratio: float

    research_summary: str
    recent_developments: list[str]
    catalysts: list[str]
    risks: list[str]

    sources: list[Source]
    
class ResearchReport(BaseModel):
    companies: List[CompanyResearch]