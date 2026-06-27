import { useState, useEffect } from "react";
 
const TYPE_COLORS = {
  code_issue: "#378ADD",
  devops_config: "#EF9F27",
  infrastructure: "#D85A30",
  abap_sap: "#1D9E75",
  dependency_risk: "#7F77DD",
};
 
const TYPE_LABELS = {
  code_issue: "Code Issue",
  devops_config: "DevOps Config",
  infrastructure: "Infrastructure",
  abap_sap: "ABAP / SAP",
  dependency_risk: "Dependency Risk",
};
 
export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({ total: 0, resolved: 0, active: 0 });
  const [lastUpdate, setLastUpdate] = useState(null);
 
  const fetchData = async () => {
    try {
      const [incRes, statsRes] = await Promise.all([
        fetch("/api/incidents"),
        fetch("/api/stats")
      ]);
      setIncidents(await incRes.json());
      setStats(await statsRes.json());
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e) {}
  };
 
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);
 
  return (
<div style={{ fontFamily: "Arial, sans-serif", background: "#f4f7fb", minHeight: "100vh", padding: "24px" }}>
<div style={{ maxWidth: 1100, margin: "0 auto" }}>
 
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
<div>
<h1 style={{ margin: 0, color: "#1F3864", fontSize: 24 }}>Thee Sentinel</h1>
<p style={{ margin: 0, color: "#666", fontSize: 13 }}>Autonomous CI/CD Pipeline Healing — BCS AI Hackathon 2026</p>
</div>
<span style={{ fontSize: 12, color: "#999" }}>Last refresh: {lastUpdate} (10s auto)</span>
</div>
 
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 24 }}>
          {[
            { label: "Total Incidents", value: stats.total, color: "#1F3864" },
            { label: "Resolved", value: stats.resolved, color: "#3B6D11" },
            { label: "Active", value: stats.active, color: "#993C1D" },
          ].map(s => (
<div key={s.label} style={{ background: "#fff", borderRadius: 10, padding: "20px 24px", borderTop: `4px solid ${s.color}` }}>
<div style={{ fontSize: 32, fontWeight: "bold", color: s.color }}>{s.value}</div>
<div style={{ fontSize: 14, color: "#666", marginTop: 4 }}>{s.label}</div>
</div>
          ))}
</div>
 
        <div style={{ background: "#fff", borderRadius: 10, overflow: "hidden" }}>
<div style={{ padding: "16px 20px", borderBottom: "1px solid #eee", fontWeight: "bold", color: "#1F3864" }}>
            Incident Log
</div>
<table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
<thead>
<tr style={{ background: "#f8f9fc" }}>
                {["ID", "Project", "Type", "Root Cause", "Action Taken", "Status", "Time"].map(h => (
<th key={h} style={{ padding: "10px 14px", textAlign: "left", color: "#444", fontWeight: 600, borderBottom: "1px solid #eee" }}>{h}</th>
                ))}
</tr>
</thead>
<tbody>
              {incidents.length === 0 ? (
<tr><td colSpan={7} style={{ padding: 32, textAlign: "center", color: "#aaa" }}>
                  No incidents yet. Waiting for pipeline webhooks...
</td></tr>
              ) : incidents.map((inc, i) => (
<tr key={inc.id} style={{ background: i % 2 === 0 ? "#fff" : "#fafbfd", borderBottom: "1px solid #f0f0f0" }}>
<td style={{ padding: "10px 14px", fontWeight: "bold", color: "#1F3864" }}>#{inc.id}</td>
<td style={{ padding: "10px 14px" }}>{inc.project}</td>
<td style={{ padding: "10px 14px" }}>
<span style={{
                      background: TYPE_COLORS[inc.issue_type] + "20",
                      color: TYPE_COLORS[inc.issue_type],
                      padding: "3px 8px", borderRadius: 4, fontSize: 12, fontWeight: 600
                    }}>
                      {TYPE_LABELS[inc.issue_type] || inc.issue_type}
</span>
</td>
<td style={{ padding: "10px 14px", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                      title={inc.root_cause}>{inc.root_cause}</td>
<td style={{ padding: "10px 14px", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                      title={inc.action_taken}>{inc.action_taken}</td>
<td style={{ padding: "10px 14px" }}>
<span style={{
                      color: inc.status === "resolved" ? "#3B6D11" : "#993C1D",
                      fontWeight: 600
                    }}>{inc.status}</span>
</td>
<td style={{ padding: "10px 14px", color: "#888", whiteSpace: "nowrap" }}>
                    {inc.created_at ? inc.created_at.slice(0, 16).replace("T", " ") : "—"}
</td>
</tr>
              ))}
</tbody>
</table>
</div>
 
      </div>
</div>
  );
}
