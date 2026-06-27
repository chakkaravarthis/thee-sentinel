import { useState, useEffect } from "react";
 
const COLORS = {
  code_issue: "#378ADD",
  devops_config: "#EF9F27",
  infrastructure: "#D85A30",
  abap_sap: "#1D9E75",
  dependency_risk: "#7F77DD",
};
 
const LABELS = {
  code_issue: "Code Issue",
  devops_config: "DevOps Config",
  infrastructure: "Infrastructure",
  abap_sap: "ABAP / SAP",
  dependency_risk: "Dependency Risk",
};
 
export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({ total: 0, resolved: 0, active: 0 });
 
  useEffect(() => {
    const load = () => {
      fetch("/api/incidents")
        .then(r => r.json())
        .then(d => setIncidents(d))
        .catch(() => {});
      fetch("/api/stats")
        .then(r => r.json())
        .then(d => setStats(d))
        .catch(() => {});
    };
    load();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, []);
 
  return (
<div style={{fontFamily:"Arial,sans-serif",background:"#f4f7fb",minHeight:"100vh",padding:24}}>
<div style={{maxWidth:1100,margin:"0 auto"}}>
 
        <h1 style={{color:"#1F3864",marginBottom:4}}>Thee Sentinel</h1>
<p style={{color:"#666",marginTop:0,marginBottom:24}}>
          Autonomous CI/CD Pipeline Healing — BCS AI Hackathon 2026 — Team: Thee Agents
</p>
 
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:16,marginBottom:24}}>
          {[
            {label:"Total Incidents", value:stats.total,    color:"#1F3864"},
            {label:"Resolved",        value:stats.resolved, color:"#3B6D11"},
            {label:"Active",          value:stats.active,   color:"#993C1D"},
          ].map(s => (
<div key={s.label} style={{background:"#fff",borderRadius:10,padding:"20px 24px",borderTop:`4px solid ${s.color}`}}>
<div style={{fontSize:36,fontWeight:"bold",color:s.color}}>{s.value}</div>
<div style={{fontSize:14,color:"#666"}}>{s.label}</div>
</div>
          ))}
</div>
 
        <div style={{background:"#fff",borderRadius:10,overflowX:"auto"}}>
<div style={{padding:"14px 20px",borderBottom:"1px solid #eee",fontWeight:"bold",color:"#1F3864"}}>
            Incident Log
</div>
<table style={{width:"100%",borderCollapse:"collapse",fontSize:13}}>
<thead>
<tr style={{background:"#f8f9fc"}}>
                {["ID","Project","Type","Root Cause","Action","Status","Time"].map(h => (
<th key={h} style={{padding:"10px 14px",textAlign:"left",color:"#444",fontWeight:600,borderBottom:"1px solid #eee"}}>
                    {h}
</th>
                ))}
</tr>
</thead>
<tbody>
              {incidents.length === 0 ? (
<tr>
<td colSpan={7} style={{padding:40,textAlign:"center",color:"#bbb"}}>
                    No incidents yet — send a webhook to trigger one
</td>
</tr>
              ) : incidents.map((inc, i) => (
<tr key={inc.id} style={{background: i%2===0?"#fff":"#fafbfd",borderBottom:"1px solid #f0f0f0"}}>
<td style={{padding:"10px 14px",fontWeight:"bold",color:"#1F3864"}}>#{inc.id}</td>
<td style={{padding:"10px 14px"}}>{inc.project}</td>
<td style={{padding:"10px 14px"}}>
<span style={{
                      background:(COLORS[inc.issue_type]||"#888")+"20",
                      color:COLORS[inc.issue_type]||"#888",
                      padding:"3px 8px",borderRadius:4,fontSize:11,fontWeight:600
                    }}>
                      {LABELS[inc.issue_type]||inc.issue_type}
</span>
</td>
<td style={{padding:"10px 14px",maxWidth:180,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}
                      title={inc.root_cause}>{inc.root_cause}</td>
<td style={{padding:"10px 14px",maxWidth:180,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}
                      title={inc.action_taken}>{inc.action_taken}</td>
<td style={{padding:"10px 14px",fontWeight:600,color:inc.status==="resolved"?"#3B6D11":"#993C1D"}}>
                    {inc.status}
</td>
<td style={{padding:"10px 14px",color:"#888",whiteSpace:"nowrap"}}>
                    {inc.created_at?inc.created_at.slice(0,16).replace("T"," "):"—"}
</td>
</tr>
              ))}
</tbody>
</table>
</div>
 
        <div style={{marginTop:12,padding:"10px 16px",background:"#fff",borderRadius:8,fontSize:12,color:"#888"}}>
          Webhook: <code style={{background:"#f0f4ff",padding:"2px 6px",borderRadius:3}}>POST http://localhost:3000/webhook/failure</code>
&nbsp;·&nbsp;Auto-refresh every 10s
</div>
 
      </div>
</div>
  );
}
