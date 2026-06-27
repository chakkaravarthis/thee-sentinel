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
 
def handle_dependency_issue(incident: dict, config: dict) -> dict:
    log        = incident.get("log", "")
    score_data = _score_dependency(log)
    trust      = score_data.get("trust_score", 50)
    safety     = score_data.get("upgrade_safety", 50)
    threshold  = config.get("dependency_block_threshold", 40)
    ticket_url = None
    if trust < threshold or safety < threshold:
        ticket_url = _create_dep_ticket(score_data, config)
        action = f"PIPELINE BLOCKED. Trust: {trust}/100, Upgrade Safety: {safety}/100. Ticket raised."
    else:
        action = f"Dependency scored OK. Trust: {trust}/100, Upgrade Safety: {safety}/100."
    return {"action_taken": action, "ticket_url": ticket_url}
 
def _score_dependency(log: str) -> dict:
    raw = _llm(f"Score this dependency issue. Return JSON only:\n{{\"package\": \"name\", \"trust_score\": 0-100, \"upgrade_safety\": 0-100, \"reason\": \"short\"}}\nLog: {log[:1500]}")
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"package": "unknown", "trust_score": 50, "upgrade_safety": 50, "reason": log[:100]}
 
def _create_dep_ticket(score_data: dict, config: dict) -> str:
    token   = os.getenv("ADO_TOKEN")
    org     = os.getenv("ADO_ORG")
    project = os.getenv("ADO_PROJECT")
    if not all([token, org, project]):
        return "https://dev.azure.com/thee-sentinel/dep-ticket"
    url     = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Bug?api-version=7.1"
    headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {token}"}
    body    = [
        {"op": "add", "path": "/fields/System.Title", "value": f"[Thee Sentinel] Dependency Risk: {score_data.get('package')} Trust={score_data.get('trust_score')}/100"},
        {"op": "add", "path": "/fields/System.Description", "value": f"<b>Package:</b> {score_data.get('package')}<br><b>Trust:</b> {score_data.get('trust_score')}/100<br><b>Upgrade Safety:</b> {score_data.get('upgrade_safety')}/100<br><b>Reason:</b> {score_data.get('reason')}"},
        {"op": "add", "path": "/fields/System.Tags", "value": "thee-sentinel;dependency"}
    ]
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        return resp.json().get("_links", {}).get("html", {}).get("href", "https://dev.azure.com")
    except Exception:
        return "https://dev.azure.com/thee-sentinel/dep-ticket"
