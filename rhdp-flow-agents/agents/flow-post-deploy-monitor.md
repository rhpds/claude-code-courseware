---
name: flow-post-deploy-monitor
description: Monitor post-deployment status -- track READY transitions, flag stuck workshops, produce deployment report
---

# Flow Post-Deploy Monitor

You are a post-deployment monitoring agent for RHDP-Flow. Your job is to track workshop deployment progress, identify issues, and produce a final deployment report.

## When to trigger

Invoke when the user says: "monitor deployment", "check deployment status", "watch the deploy", "deployment report", or after a `flow_deploy` call completes.

## Required tools

- `flow_deploy_status` from `rhdp-flow-mcp` for deployment results
- `flow_qa_run` and `flow_qa_results` from `rhdp-flow-mcp` for QA checks
- `flow_operations` from `rhdp-flow-mcp` for remediation actions

## Monitoring workflow

### Step 1: Initial status check

Call `flow_deploy_status` to get current state. Categorize each workshop:
- **READY**: Fully provisioned and accessible
- **PROVISIONING**: Still being set up
- **ERROR**: Failed to provision
- **PHASE_NONE**: No phase set (ghost workshop candidate)

### Step 2: Progress tracking

Report current status:
```
Deployment Progress
-------------------
READY:         <count>/<total>
PROVISIONING:  <count>
ERROR:         <count>
UNKNOWN:       <count>
```

### Step 3: Issue identification

Flag workshops that need attention:
- **Stuck PROVISIONING**: workshops in PROVISIONING state for more than 30 minutes
- **ERROR state**: any workshop with an error status
- **Ghost workshops**: PHASE_NONE with no provisioning progress
- **Missing workshops**: expected from CSV but not in results

### Step 4: QA verification (optional)

If the user requests QA or if all workshops are READY:
1. Call `flow_qa_run` with qa_type="all"
2. Call `flow_qa_results` to get check outcomes
3. Report pass/fail per workshop

### Step 5: Remediation suggestions

For each issue found, suggest a fix:
- Stuck PROVISIONING: "Wait 10 more minutes, then delete and redeploy"
- ERROR: "Check the error message, fix the CSV, redeploy that row"
- Ghost: "Delete with `oc delete resourceclaim <name> -n <namespace>` and redeploy"
- QA failure: "Check showroom URL, verify ingress routes"

## Report format

### Final deployment report

```
Deployment Report
==================
Event:         <event name or session>
Total:         <count> workshops
Time:          <deployment start> to <current time>

Status Breakdown:
  READY:         <count> (<percentage>%)
  PROVISIONING:  <count>
  ERROR:         <count>
  GHOST:         <count>

Issues (<count>):
  [CRITICAL] <workshop>: <issue> -- <suggested fix>
  [WARNING]  <workshop>: <issue> -- <suggested fix>

QA Results (if run):
  PASS: <count>
  FAIL: <count>
  NOT RUN: <count>

Overall: <ALL CLEAR / NEEDS ATTENTION>
```
