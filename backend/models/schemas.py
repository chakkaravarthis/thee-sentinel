from pydantic import BaseModel
from typing import Optional
 
class WebhookPayload(BaseModel):
    project: str
    pipeline: str
    log: str
    source: Optional[str] = "jenkins"
 
class IncidentCreate(BaseModel):
    project: str
    pipeline: str
    issue_type: str
    root_cause: str
    fix_suggestion: str
    affected_file: Optional[str] = None
    confidence: int
    status: str = "open"
    action_taken: Optional[str] = None
    pr_url: Optional[str] = None
    ticket_url: Optional[str] = None
