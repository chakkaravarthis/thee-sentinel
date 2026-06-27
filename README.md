# Thee Sentinel
 
Autonomous CI/CD, SAP/ABAP and Dependency Intelligence using Agentic AI.
 
**BCS AI Hackathon 2026 — Team: Thee Agents**
 
## Quick Start
 
\`\`\`bash
cp .env.example .env
# Fill in your API keys in .env
docker-compose up --build
\`\`\`
 
Dashboard: http://localhost  
API: http://localhost/health  
Webhook: POST http://localhost/webhook/failure
 
## Test a failure
 
\`\`\`bash
curl -X POST http://localhost/webhook/failure \
  -H "Content-Type: application/json" \
  -d '{
    "project": "thee-sentinel-demo",
    "pipeline": "build",
    "log": "ERROR: NullPointerException at PaymentService.java:142\n  at com.example.PaymentService.processPayment(PaymentService.java:142)\nBuild FAILED"
  }'
\`\`\`
 
## Architecture
 
5-type agentic loop: Code Issue → DevOps Config → Infrastructure → ABAP/SAP → Dependency Risk
 
Powered by Claude AI (claude-haiku-4-5-20251001)
