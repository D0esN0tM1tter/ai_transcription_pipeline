from pydantic import BaseModel
from typing import List


class SummaryResponse(BaseModel):
    summary_id: str
    job_id: str
    text_content: str
    language: str


class SummariesResponse(BaseModel):
    job_id: str
    summaries: List[SummaryResponse]
