import os, requests, aiosmtplib, asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
def notify_all(incident: dict, result: dict):
    _send_teams(incident, result)
    asyncio.run(_send_email(incident, result))
 
def _send_teams(incident: dict, result: dict):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        return
 
    type_colors = {
        "code_issue": "FF4444",
        "devops_config": "FF8C00",
        "infrastructure": "CC0000",
        "abap_sap": "0078D4",
        "dependency_risk": "7B2FBE"
    }
    color = type_colors.get(incident.get("issue_type"), "888888")
 
    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": "Thee Sentinel — Pipeline Incident",
                     "weight": "Bolder", "size": "Medium", "color": "Accent"},
                    {"type": "FactSet", "facts": [
                        {"title": "Project", "value": incident.get("project", "unknown")},
                        {"title": "Issue Type", "value": incident.get("issue_type", "unknown")},
                        {"title": "Root Cause", "value": incident.get("root_cause", "")[:120]},
                        {"title": "Action Taken", "value": result.get("action_taken", "")[:120]},
                        {"title": "Confidence", "value": f"{incident.get('confidence', 0)}%"},
                        {"title": "Status", "value": incident.get("status", "open")},
                    ]},
                ],
                "actions": [
                    {"type": "Action.OpenUrl", "title": "View PR",
                     "url": result.get("pr_url") or "https://github.com"},
                    {"type": "Action.OpenUrl", "title": "View Ticket",
                     "url": result.get("ticket_url") or "https://dev.azure.com"},
                ] if result.get("pr_url") or result.get("ticket_url") else []
            }
        }]
    }
    try:
        requests.post(webhook_url, json=card, timeout=10)
    except Exception:
        pass
 
async def _send_email(incident: dict, result: dict):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_to = os.getenv("SMTP_TO")
 
    if not all([smtp_host, smtp_user, smtp_pass, smtp_to]):
        return
 
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Thee Sentinel] {incident.get('issue_type', 'Incident')} — {incident.get('project', 'unknown')}"
    msg["From"] = smtp_user
    msg["To"] = smtp_to
 
    html = f"""
<html><body style="font-family:Arial,sans-serif;max-width:600px">
<h2 style="color:#1F3864">Thee Sentinel — Pipeline Incident Report</h2>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
<tr><td><b>Project</b></td><td>{incident.get('project')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Issue Type</b></td><td>{incident.get('issue_type')}</td></tr>
<tr><td><b>Root Cause</b></td><td>{incident.get('root_cause')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Fix Suggestion</b></td><td>{incident.get('fix_suggestion')}</td></tr>
<tr><td><b>Action Taken</b></td><td>{result.get('action_taken')}</td></tr>
<tr style="background:#f0f4ff"><td><b>Confidence</b></td><td>{incident.get('confidence')}%</td></tr>
</table>
    {"<p><a href='" + result.get('pr_url') + "'>View Pull Request</a></p>" if result.get('pr_url') else ""}
    {"<p><a href='" + result.get('ticket_url') + "'>View ADO Ticket</a></p>" if result.get('ticket_url') else ""}
<p style="color:#888;font-size:12px">Thee Sentinel — BCS AI Hackathon 2026</p>
</body></html>"""
 
    msg.attach(MIMEText(html, "html"))
    try:
        await aiosmtplib.send(msg, hostname=smtp_host, port=587,
                              username=smtp_user, password=smtp_pass, start_tls=True)
    except Exception:
        pass
