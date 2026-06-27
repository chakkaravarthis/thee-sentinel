import os, subprocess
 
def handle_infra_issue(incident: dict, config: dict) -> dict:
    root_cause = incident.get("root_cause", "")
    service = incident.get("project", "unknown")
 
    result = _restart_service(service, root_cause)
    return {
        "action_taken": result,
        "ticket_url": None
    }
 
def _restart_service(service: str, root_cause: str) -> str:
    namespace = os.getenv("K8S_NAMESPACE", "default")
 
    if "OOMKilled" in root_cause or "CrashLoopBackOff" in root_cause:
        try:
            result = subprocess.run(
                ["kubectl", "rollout", "restart", f"deployment/{service}", "-n", namespace],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return f"kubectl rollout restart triggered for {service} in {namespace}"
        except Exception as e:
            pass
 
    try:
        result = subprocess.run(
            ["docker", "restart", service],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"Docker container {service} restarted successfully"
    except Exception:
        pass
 
    return f"Infra recovery attempted for {service}. Manual verification recommended."
