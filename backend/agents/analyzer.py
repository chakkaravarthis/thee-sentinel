import anthropic, os, json, re
 
def analyze_log(log_text: str) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
 
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
 
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
 
    raw = message.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
 
    try:
        return json.loads(raw)
    except Exception:
        return {
            "type": "code_issue",
            "root_cause": raw[:200],
            "fix_suggestion": "Manual investigation required",
            "affected_file": None,
            "confidence": 40
        }
