from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.schemas import WebhookPayload
from backend.agents.analyzer import analyze_log
from backend.agents.action_code import handle_code_issue
from backend.agents.action_devops import handle_devops_issue
from backend.agents.action_infra import handle_infra_issue
from backend.agents.action_abap import handle_abap_issue
from backend.agents.action_dependency import handle_dependency_issue
from backend.db.database import init_db, save_incident, resolve_incident, get_all_incidents, get_stats
from backend.notifier import notify_all
from backend.config_loader import load_config
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
 
app = FastAPI(title="Thee Sentinel", version="1.0.0", lifespan=lifespan)
 
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])
 
ACTION_MAP = {
    "code_issue": handle_code_issue,
    "devops_config": handle_devops_issue,
    "infrastructure": handle_infra_issue,
    "abap_sap": handle_abap_issue,
    "dependency_risk": handle_dependency_issue,
}
 
@app.get("/health")
def health():
    return {"status": "ok", "service": "Thee Sentinel"}
 
@app.post("/webhook/failure")
async def receive_failure(payload: WebhookPayload):
    config = load_config(payload.project)
 
    analysis = analyze_log(payload.log)
    issue_type = analysis.get("type", "code_issue")
 
    incident_data = {
        "project": payload.project,
        "pipeline": payload.pipeline,
        "issue_type": issue_type,
        "root_cause": analysis.get("root_cause", ""),
        "fix_suggestion": analysis.get("fix_suggestion", ""),
        "affected_file": analysis.get("affected_file"),
        "confidence": analysis.get("confidence", 50),
        "status": "open",
        "log": payload.log,
    }
 
    incident_id = save_incident(incident_data)
 
    handler = ACTION_MAP.get(issue_type, handle_code_issue)
    result = handler({**incident_data, "id": incident_id}, config)
 
    resolve_incident(
        incident_id,
        result.get("action_taken", ""),
        result.get("pr_url"),
        result.get("ticket_url")
    )
 
    notify_all(incident_data, result)
 
    return {
        "incident_id": incident_id,
        "issue_type": issue_type,
        "root_cause": incident_data["root_cause"],
        "action_taken": result.get("action_taken"),
        "pr_url": result.get("pr_url"),
        "ticket_url": result.get("ticket_url"),
        "confidence": incident_data["confidence"]
    }
 
@app.get("/api/incidents")
def list_incidents(limit: int = 50):
    return get_all_incidents(limit)
 
@app.get("/api/stats")
def stats():
    return get_stats()
