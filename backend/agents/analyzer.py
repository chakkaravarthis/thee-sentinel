import os, json, re, requests
 
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "http://10.10.19.109:4000")
API_KEY  = os.getenv("ANTHROPIC_API_KEY")
MODEL    = "gpt-4.1"
 
def analyze_log(log_text: str) -> dict:
    prompt = f"""You are an expert CI/CD and DevOps failure analyst.
Read the pipeline log below and classify the failure. Return ONLY valid JSON, no markdown, no explanation.
Return exactly this structure:
{{
  "type": "code_issue | devops_config | infrastructure | abap_sap | dependency_risk",
  "root_cause": "one clear sentence describing the exact failure",
  "fix_suggestion": "exact actionable fix",
  "affected_file": "filepath or null",
  "confidence": 85
}}
PIPELINE LOG:
{log_text[:4000]}"""
 
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512
            },
            timeout=30
        )
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "type": "code_issue",
            "root_cause": f"Analysis error: {str(e)[:100]}",
            "fix_suggestion": "Manual investigation required",
            "affected_file": None,
            "confidence": 40
        }
