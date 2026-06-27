import sqlite3
import os
from datetime import datetime
 
DB_PATH = os.getenv("DB_PATH", "/app/data/sentinel.db")
 
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            pipeline TEXT,
            issue_type TEXT,
            root_cause TEXT,
            fix_suggestion TEXT,
            affected_file TEXT,
            confidence INTEGER,
            status TEXT DEFAULT 'open',
            action_taken TEXT,
            pr_url TEXT,
            ticket_url TEXT,
            created_at TEXT,
            resolved_at TEXT,
            mttr_seconds INTEGER
        )
    """)
    conn.commit()
    conn.close()
 
def save_incident(data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incidents
        (project, pipeline, issue_type, root_cause, fix_suggestion,
         affected_file, confidence, status, action_taken, pr_url, ticket_url, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("project"), data.get("pipeline"), data.get("issue_type"),
        data.get("root_cause"), data.get("fix_suggestion"), data.get("affected_file"),
        data.get("confidence"), data.get("status", "open"), data.get("action_taken"),
        data.get("pr_url"), data.get("ticket_url"),
        datetime.utcnow().isoformat()
    ))
    incident_id = cur.lastrowid
    conn.commit()
    conn.close()
    return incident_id
 
def resolve_incident(incident_id: int, action_taken: str, pr_url: str = None, ticket_url: str = None):
    conn = sqlite3.connect(DB_PATH)
    resolved_at = datetime.utcnow().isoformat()
    conn.execute("""
        UPDATE incidents SET status='resolved', action_taken=?, pr_url=?,
        ticket_url=?, resolved_at=? WHERE id=?
    """, (action_taken, pr_url, ticket_url, resolved_at, incident_id))
    conn.commit()
    conn.close()
 
def get_all_incidents(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM incidents WHERE status='resolved'").fetchone()[0]
    conn.close()
    return {"total": total, "resolved": resolved, "active": total - resolved}
