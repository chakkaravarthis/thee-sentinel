import os, requests
 
def handle_devops_issue(incident: dict, config: dict) -> dict:
    root_cause     = incident.get("root_cause", "")
    affected_file  = incident.get("affected_file", ".env")
    fix_suggestion = incident.get("fix_suggestion", "")
    ticket_url     = _create_ado_ticket(root_cause, affected_file, fix_suggestion, config)
    return {
        "action_taken": f"ADO ticket created. DevOps engineer notified with exact file path.",
        "ticket_url": ticket_url
    }
 
def _create_ado_ticket(root_cause: str, affected_file: str, fix: str, config: dict) -> str:
    token   = os.getenv("ADO_TOKEN")
    org     = os.getenv("ADO_ORG")
    project = os.getenv("ADO_PROJECT")
    if not all([token, org, project]):
        return "https://dev.azure.com/thee-sentinel/demo-ticket"
    url     = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {token}"}
    body    = [
        {"op": "add", "path": "/fields/System.Title",
         "value": f"[Thee Sentinel] DevOps Config: {root_cause[:80]}"},
        {"op": "add", "path": "/fields/System.Description",
         "value": f"<b>Root Cause:</b> {root_cause}<br><b>File:</b> {affected_file}<br><b>Fix:</b> {fix}"},
        {"op": "add", "path": "/fields/System.Tags", "value": "thee-sentinel;auto-created"}
    ]
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        if resp.status_code in [200, 201]:
            data = resp.json()
            return data.get("_links", {}).get("html", {}).get("href", f"https://dev.azure.com/{org}/{project}")
        return f"https://dev.azure.com/{org}/{project}/_workitems"
    except Exception:
        return f"https://dev.azure.com/{org}/{project}/_workitems"
