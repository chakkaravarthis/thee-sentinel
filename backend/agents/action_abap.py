import os, requests, json, re
 
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "http://10.10.19.109:4000")
API_KEY  = os.getenv("ANTHROPIC_API_KEY")
MODEL    = "gpt-4.1"
 
def _llm(prompt: str) -> str:
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 256},
            timeout=30
        )
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "{}"
 
def handle_abap_issue(incident: dict, config: dict) -> dict:
    log        = incident.get("log", "")
    root_cause = incident.get("root_cause", "")
    sub_type, fix = _classify_abap(log, root_cause)
    ticket_url    = _create_abap_ticket(root_cause, sub_type, fix, config)
    return {"action_taken": f"ABAP sub-type: {sub_type}. Ticket created. BASIS/Dev notified.", "ticket_url": ticket_url}
 
def _classify_abap(log: str, root_cause: str) -> tuple:
    raw = _llm(f"Classify this SAP/ABAP failure. One of: abap_code_issue, abap_transport_issue, abap_runtime_issue.\nReturn JSON only: {{\"sub_type\": \"...\", \"fix\": \"...\"}}\nLog: {log[:1500]}")
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        data = json.loads(raw)
        return data.get("sub_type", "abap_runtime_issue"), data.get("fix", root_cause)
    except Exception:
        return "abap_runtime_issue", root_cause
 
def _create_abap_ticket(root_cause: str, sub_type: str, fix: str, config: dict) -> str:
    token   = os.getenv("ADO_TOKEN")
    org     = os.getenv("ADO_ORG")
    project = os.getenv("ADO_PROJECT")
    if not all([token, org, project]):
        return "https://dev.azure.com/thee-sentinel/abap-ticket"
    url     = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {token}"}
    body    = [
        {"op": "add", "path": "/fields/System.Title", "value": f"[Thee Sentinel] SAP/ABAP ({sub_type}): {root_cause[:70]}"},
        {"op": "add", "path": "/fields/System.Description", "value": f"<b>Sub-Type:</b> {sub_type}<br><b>Root Cause:</b> {root_cause}<br><b>Fix:</b> {fix}"},
        {"op": "add", "path": "/fields/System.Tags", "value": "thee-sentinel;abap"}
    ]
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        return resp.json().get("_links", {}).get("html", {}).get("href", "https://dev.azure.com")
    except Exception:
        return "https://dev.azure.com/thee-sentinel/abap-ticket"
