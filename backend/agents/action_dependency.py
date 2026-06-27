import os, requests, anthropic, json, re
 
def handle_dependency_issue(incident: dict, config: dict) -> dict:
    log = incident.get("log", "")
    score_data = _score_dependency(log)
    trust = score_data.get("trust_score", 50)
    safety = score_data.get("upgrade_safety", 50)
    threshold = config.get("dependency_block_threshold", 40)
 
    action = "Dependency risk assessed."
    ticket_url = None
 
    if trust < threshold or safety < threshold:
        ticket_url = _create_dep_ticket(score_data, config)
        action = f"PIPELINE BLOCKED. Trust: {trust}/100, Upgrade Safety: {safety}/100. ADO ticket raised."
 
    return {"action_taken": action, "ticket_url": ticket_url}
 
def _score_dependency(log: str) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content":
            f"Score this dependency issue from a pipeline log.\n"
            f"Return JSON only: {{\"package\": \"name\", \"trust_score\": 0-100, \"upgrade_safety\": 0-100, \"reason\": \"short explanation\"}}\n\nLog: {log[:1500]}"
        }]
    )
    raw = re.sub(r"```json|```", "", message.content[0].text).strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"package": "unknown", "trust_score": 50, "upgrade_safety": 50, "reason": log[:100]}
 
def _create_dep_ticket(score_data: dict, config: dict) -> str:
    token = os.getenv("ADO_TOKEN")
    org = os.getenv("ADO_ORG")
    project_name = os.getenv("ADO_PROJECT")
 
    if not all([token, org, project_name]):
        return "https://dev.azure.com/thee-sentinel/dep-ticket"
 
    url = f"https://dev.azure.com/{org}/{project_name}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {token}"}
    body = [
        {"op": "add", "path": "/fields/System.Title",
         "value": f"[Thee Sentinel] Dependency Risk: {score_data.get('package')} Trust={score_data.get('trust_score')}/100"},
        {"op": "add", "path": "/fields/System.Description",
         "value": f"<b>Package:</b> {score_data.get('package')}<br><b>Trust Score:</b> {score_data.get('trust_score')}/100<br><b>Upgrade Safety:</b> {score_data.get('upgrade_safety')}/100<br><b>Reason:</b> {score_data.get('reason')}"},
        {"op": "add", "path": "/fields/System.Tags", "value": "thee-sentinel;dependency;auto-created"}
    ]
    resp = requests.post(url, headers=headers, json=body)
    return resp.json().get("_links", {}).get("html", {}).get("href", "https://dev.azure.com")
