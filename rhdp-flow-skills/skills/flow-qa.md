---
name: flow-qa
description: Run QA checks on deployed workshops and present pass/fail results
---

# Flow QA

Run QA verification checks on deployed workshops and present results with actionable next steps.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Determine QA scope

Ask the user which checks to run:
- **QA1** (setup verification): confirms workshop resources exist and are configured
- **QA2** (deployment health): checks running pods, routes, services
- **QA3** (showroom): validates landing page accessibility
- **Both** (QA1 + QA2): recommended for standard checks
- **All** (QA1 + QA2 + QA3): full audit

If the user doesn't specify, default to "all".

Optionally ask if they want to limit to a specific namespace (comma-separated for multiple).

### Step 2: Run QA

Call `flow_qa_run` with the selected `qa_type` and optional `namespace`.

### Step 3: Get results

Call `flow_qa_results` to retrieve the check results.

### Step 4: Present results

Format results as a pass/fail summary:

```
QA Results
----------
Total checks:  <N>
Passed:        <N>
Failed:        <N>
Warnings:      <N>

Failed Checks:
  [FAIL] <namespace> -- <check_name>: <details>
         Fix: <suggested action>

  [FAIL] <namespace> -- <check_name>: <details>
         Fix: <suggested action>

Warnings:
  [WARN] <namespace> -- <check_name>: <details>
```

For each failure, suggest a concrete fix:
- Pod not running: "Check pod logs with `oc logs -n <ns> <pod>`"
- Route not found: "Verify the route exists: `oc get routes -n <ns>`"
- Service missing: "Check the deployment completed: `flow_deploy_status`"
- Showroom unreachable: "Verify the showroom URL is accessible and DNS resolves"

### Step 5: Offer follow-up

If there are failures, ask:
> "Would you like to re-run QA after fixing these issues, or extend/redeploy the affected workshops?"
