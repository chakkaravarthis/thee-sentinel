import os, requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
def notify_all(incident: dict, result: dict):
    _send_teams(incident, result)
    _send_email(incident, result)
 
def _send_teams(incident: dict, result: dict):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = {
        "project":      str(incident.get("project", "")),
        "issue_type":   str(incident.get("issue_type", "")),
        "root_cause":   str(incident.get("root_cause", ""))[:200],
        "action_taken": str(result.get("action_taken", ""))[:200],
        "confidence":   incident.get("confidence", 0)
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception:
        pass
 
def _send_email(incident: dict, result: dict):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_to   = os.getenv("SMTP_TO")
    if not all([smtp_host, smtp_user, smtp_pass, smtp_to]):
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Thee Sentinel] {incident.get('issue_type')} — {incident.get('project')}"
    msg["From"]    = smtp_user
    msg["To"]      = smtp_to
    html = f"""<html><body style="font-family:Arial,sans-serif">
<h2 style="color:#1F3864">Thee Sentinel — Incident Report</h2>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;max-width:600px">
<tr><td><b>Project</b></td><td>{incident.get('project')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Type</b></td><td>{incident.get('issue_type')}</td></tr>
<tr><td><b>Root Cause</b></td><td>{incident.get('root_cause')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Fix</b></td><td>{incident.get('fix_suggestion')}</td></tr>
<tr><td><b>Action Taken</b></td><td>{result.get('action_taken')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Confidence</b></td><td>{incident.get('confidence')}%</td></tr>
</table>
</body></html>"""
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP(smtp_host, 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, smtp_to, msg.as_string())
    except Exception:
        pass
