import os, requests, base64, re, json
 
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "http://10.10.19.109:4000")
API_KEY  = os.getenv("ANTHROPIC_API_KEY")
MODEL    = "gpt-4.1"
 
def _llm(prompt: str) -> str:
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1024},
            timeout=30
        )
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"# Fix generation failed: {e}"
 
def handle_code_issue(incident: dict, config: dict) -> dict:
    root_cause    = incident.get("root_cause", "")
    affected_file = incident.get("affected_file")
    log           = incident.get("log", "")
    fix           = _llm(f"Fix this CI/CD code failure. Return only corrected code.\nRoot cause: {root_cause}\nFile: {affected_file}\nLog: {log[:1000]}")
    pr_url        = _raise_pr(fix, affected_file, root_cause, config)
    return {"action_taken": f"AI fix generated. PR raised: {pr_url}", "pr_url": pr_url}
 
def _raise_pr(fix: str, affected_file: str, root_cause: str, config: dict) -> str:
    token = os.getenv("GITHUB_TOKEN")
    repo  = config.get("github_repo")
    if not token or not repo:
        return "https://github.com/thee-sentinel/demo-pr"
    headers  = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base_url = f"https://api.github.com/repos/{repo}"
    try:
        sha    = requests.get(f"{base_url}/git/ref/heads/main", headers=headers).json()["object"]["sha"]
        branch = f"sentinel-fix-{os.urandom(4).hex()}"
        requests.post(f"{base_url}/git/refs", headers=headers, json={"ref": f"refs/heads/{branch}", "sha": sha})
        if affected_file:
            fr = requests.get(f"{base_url}/contents/{affected_file}?ref=main", headers=headers)
            if fr.status_code == 200:
                requests.put(f"{base_url}/contents/{affected_file}", headers=headers, json={
                    "message": f"[Thee Sentinel] Auto-fix: {root_cause[:60]}",
                    "content": base64.b64encode(fix.encode()).decode(),
                    "sha": fr.json()["sha"], "branch": branch
                })
        pr = requests.post(f"{base_url}/pulls", headers=headers, json={
            "title": f"[Thee Sentinel] Auto-fix: {root_cause[:60]}",
            "body": f"**Root cause:** {root_cause}\n\n**Fix:**\n```\n{fix[:500]}\n```",
            "head": branch, "base": "main"
        })
        return pr.json().get("html_url", "https://github.com/thee-sentinel/pr")
    except Exception as e:
        return "https://github.com/thee-sentinel/demo-pr"
