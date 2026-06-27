import os, requests, anthropic, base64
 
def handle_code_issue(incident: dict, config: dict) -> dict:
    log = incident.get("log", "")
    root_cause = incident.get("root_cause", "")
    affected_file = incident.get("affected_file")
 
    fix = _generate_fix(log, root_cause, affected_file)
    pr_url = _raise_pr(fix, affected_file, root_cause, config)
 
    return {
        "action_taken": f"AI-generated fix applied. PR raised: {pr_url}",
        "pr_url": pr_url
    }
 
def _generate_fix(log: str, root_cause: str, affected_file: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content":
            f"Fix this CI/CD code failure. Return only the corrected code.\n"
            f"Root cause: {root_cause}\nFile: {affected_file}\nLog excerpt: {log[:1000]}"
        }]
    )
    return message.content[0].text.strip()
 
def _raise_pr(fix: str, affected_file: str, root_cause: str, config: dict) -> str:
    token = os.getenv("GITHUB_TOKEN")
    repo = config.get("github_repo")
    if not token or not repo:
        return "https://github.com/thee-sentinel/demo-pr"
 
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base_url = f"https://api.github.com/repos/{repo}"
 
    main_sha = requests.get(f"{base_url}/git/ref/heads/main", headers=headers).json()
    sha = main_sha.get("object", {}).get("sha", "")
 
    branch = f"sentinel-fix-{os.urandom(4).hex()}"
    requests.post(f"{base_url}/git/refs", headers=headers, json={
        "ref": f"refs/heads/{branch}", "sha": sha
    })
 
    if affected_file:
        file_resp = requests.get(f"{base_url}/contents/{affected_file}?ref=main", headers=headers)
        if file_resp.status_code == 200:
            file_sha = file_resp.json().get("sha")
            requests.put(f"{base_url}/contents/{affected_file}", headers=headers, json={
                "message": f"[Thee Sentinel] Auto-fix: {root_cause[:60]}",
                "content": base64.b64encode(fix.encode()).decode(),
                "sha": file_sha,
                "branch": branch
            })
 
    pr = requests.post(f"{base_url}/pulls", headers=headers, json={
        "title": f"[Thee Sentinel] Auto-fix: {root_cause[:60]}",
        "body": f"Auto-generated fix by Thee Sentinel.\n\n**Root cause:** {root_cause}\n\n**Fix applied:**\n```\n{fix[:500]}\n```",
        "head": branch,
        "base": "main"
    })
    return pr.json().get("html_url", "https://github.com/thee-sentinel/pr")
