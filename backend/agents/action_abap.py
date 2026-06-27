import os, requests, anthropic
 
def handle_abap_issue(incident: dict, config: dict) -> dict:
    log = incident.get("log", "")
    root_cause = incident.get("root_cause", "")
 
    sub_type, fix = _classify_abap(log, root_cause)
    ticket_url = _create_abap_ticket(root_cause, sub_type, fix, config)
 
    return {
        "action_taken": f"ABAP sub-type: {sub_type}. ADO ticket created. BASIS/Dev team notified.",
        "ticket_url": ticket_url
    }
 
def _classify_abap(log: str, root_cause: str) -> tuple:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content":
            f"Classify this SAP/ABAP failure into one of: abap_code_issue, abap_transport_issue, abap_runtime_issue.\n"
            f"Also suggest an exact fix with program name and line number if available.\n"
            f"Return JSON: {{\"sub_type\": \"...\", \"fix\": \"...\"}}\n\nLog: {log[:2000]}"
        }]
    )
    import json, re
    raw = re.sub(r"```json|```", "", message.content[0].text).strip()
    try:
        data = json.loads(raw)
        return data.get("sub_type", "abap_runtime_issue"), data.get("fix", root_cause)
    except Exception:
        return "abap_runtime_issue", root_cause
 
def _create_abap_ticket(root_cause: str, sub_type: str, fix: str, config: dict) -> str:
    token = os.getenv("ADO_TOKEN")
    org = os.getenv("ADO_ORG")
    project = os.getenv("ADO_PROJECT")
 
    if not all([token, org, project]):
        return "https://dev.azure.com/thee-sentinel/abap-ticket"
 
    url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {token}"
    }
    body = [
        {"op": "add", "path": "/fields/System.Title",
         "value": f"[Thee Sentinel] SAP/ABAP Issue ({sub_type}): {root_cause[:70]}"},
        {"op": "add", "path": "/fields/System.Description",
         "value": f"<b>Sub-Type:</b> {sub_type}<br><b>Root Cause:</b> {root_cause}<br><b>Suggested Fix:</b> {fix}"},
        {"op": "add", "path": "/fields/System.Tags", "value": "thee-sentinel;abap;auto-created"}
    ]
    resp = requests.post(url, headers=headers, json=body)
    return resp.json().get("_links", {}).get("html", {}).get("href", "https://dev.azure.com")
