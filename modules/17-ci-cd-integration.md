# Module 17 — CI/CD Integration

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Use Claude Code in CI/CD pipelines — GitHub Actions and OpenShift Pipelines — for automated code review, testing, and deployment assistance.

## Orientation

Print this once at the start:

```
You're learning CI/CD integration with Claude Code.
This takes about 15 minutes.

We'll cover:
  1. Claude Code in GitHub Actions (code review, PR assistance)
  2. Claude Code in OpenShift Pipelines (deployment validation)
  3. Non-interactive mode and API key management
  4. Deciding where Claude Code adds value in your pipeline

You'll need:
  - Claude Code installed and working (Module 01)
  - A GitHub repository you can modify (for Actions)
  - Optional: OpenShift cluster access (for Pipelines)

You can stop at any section if a particular CI/CD system
doesn't apply to your workflow.
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/17.started
```

## Preflight

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — GitHub CLI available?
if command -v gh &>/dev/null; then
  echo "EXISTS: GitHub CLI $(gh --version 2>/dev/null | head -1)"
  # Check if authenticated
  gh auth status &>/dev/null 2>&1 && echo "EXISTS: GitHub CLI authenticated" || echo "MISSING: GitHub CLI not authenticated — run: gh auth login"
else
  echo "INFO: GitHub CLI not installed (optional for this module)"
fi

# Check 3 — Current repo has GitHub remote?
if git remote -v 2>/dev/null | grep -q "github.com"; then
  REMOTE=$(git remote -v 2>/dev/null | grep "github.com" | head -1 | awk '{print $2}')
  echo "EXISTS: GitHub remote: $REMOTE"
else
  echo "INFO: No GitHub remote detected"
fi

# Check 4 — Existing GitHub Actions?
if [ -d ".github/workflows" ]; then
  WF_COUNT=$(ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: $WF_COUNT GitHub Actions workflow(s)"
else
  echo "INFO: No .github/workflows/ directory"
fi

# Check 5 — OpenShift CLI available?
if command -v oc &>/dev/null; then
  echo "EXISTS: OpenShift CLI (oc)"
  oc whoami &>/dev/null 2>&1 && echo "EXISTS: Logged in to OpenShift as $(oc whoami 2>/dev/null)" || echo "INFO: Not logged in to OpenShift"
else
  echo "INFO: OpenShift CLI not installed (optional)"
fi
```

Print a summary. This module has two main tracks — GitHub Actions and OpenShift Pipelines. The user can do either or both.

```
Based on preflight results, this module covers:

  GitHub Actions:  [Available/Not Available based on checks]
  OpenShift Pipelines: [Available/Not Available based on checks]

You can focus on whichever applies to your workflow,
or skip sections that don't apply.
```

## Step 1 — Claude Code in Non-Interactive Mode

Before using Claude Code in pipelines, understand how it runs without a human.

Tell the user:
```
In CI/CD, Claude Code runs non-interactively. Key differences:

  Interactive (your terminal):
    - Prompts for permission on each tool call
    - Shows streaming output
    - Waits for your input

  Non-interactive (CI pipeline):
    - Must pre-approve all actions (--dangerously-skip-permissions
      or allowlisted tool patterns)
    - Output captured in logs
    - Runs to completion or timeout
    - Needs API credentials via environment variables

The basic pattern:

  claude --print -p "Review this PR for security issues" \
    --dangerously-skip-permissions

  Flags:
    --print (-p)  Output the response as text (no interactive UI)
    --dangerously-skip-permissions  Skip all permission prompts
    --model sonnet  Use a specific model (cost control)
    --max-tokens 4096  Limit response length
```

## Step 2 — GitHub Actions: PR Review

Tell the user:
```
A common CI use case: Claude Code reviews pull requests
automatically when they're opened or updated.

Here's a workflow structure (don't create this yet — we'll
discuss what makes sense for your project):
```

Show the workflow pattern:
```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Review PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Get the diff
          DIFF=$(git diff origin/main...HEAD)

          # Ask Claude to review
          claude --print -p "Review this diff for:
          1. Security issues
          2. Bug risks
          3. Style violations per our CLAUDE.md

          Diff:
          $DIFF" --dangerously-skip-permissions --model sonnet

      - name: Post review comment
        # Optionally post the review as a PR comment
        # using gh pr comment
```

Explain the trade-offs:
```
Considerations before adding this:

  COST: Every PR push triggers a review. With Sonnet, a typical
  diff review costs $0.05-0.50 depending on diff size.
  Budget: ~$15-50/month for an active repo.

  VALUE: Best for catching security issues and style violations
  that humans miss in review fatigue. Less useful for architectural
  review (needs more context than a diff provides).

  SECRETS: The API key must be stored as a GitHub secret.
  Never put it in the workflow file.

  SCOPE: Start with security-only review. Add more checks
  as you validate the value.
```

## Step 3 — OpenShift Pipelines: Deployment Validation

Skip if OpenShift CLI is not available.

Tell the user:
```
Claude Code can validate deployments in OpenShift Pipelines
(Tekton). Common use cases:

  PRE-DEPLOY: Validate manifests, check for security issues
  POST-DEPLOY: Verify health endpoints, check pod status
  INCIDENT: Analyze logs when pods crash

Here's a Tekton task pattern:
```

Show the pattern:
```yaml
# tekton/tasks/claude-validate.yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: claude-validate-deployment
spec:
  params:
    - name: namespace
      type: string
    - name: app-name
      type: string
  steps:
    - name: validate
      image: node:20-slim
      env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: claude-api-key
              key: api-key
      script: |
        npm install -g @anthropic-ai/claude-code
        
        # Post-deploy validation
        claude --print -p "Check the deployment status:
        1. Are all pods running?
        2. Is the health endpoint responding?
        3. Any error patterns in recent logs?
        
        Namespace: $(params.namespace)
        App: $(params.app-name)" \
        --dangerously-skip-permissions --model sonnet
```

Explain:
```
OpenShift-specific considerations:

  RBAC: The Tekton service account needs read access to pods,
  logs, and routes. Don't give it write access unless Claude
  needs to take remediation actions.

  SECRETS: Store the API key as a Kubernetes secret, reference
  it via secretKeyRef. Never bake it into the image.

  COST: Post-deploy validation is infrequent (per deployment),
  so cost is usually low ($0.10-0.50 per deployment check).
```

## Step 4 — Deciding Where Claude Code Adds Value

Tell the user:
```
Not every pipeline step benefits from Claude Code. Use this
decision framework:

  HIGH VALUE (add Claude):
    - Security review of diffs
    - Post-deploy health validation
    - Incident log analysis
    - Documentation generation from code changes
    - Changelog generation from commits

  MODERATE VALUE (consider):
    - Style/convention checking (linters may be cheaper)
    - Test generation for new code
    - PR description writing

  LOW VALUE (skip):
    - Build compilation (deterministic, no AI needed)
    - Unit test execution (just run the tests)
    - Static analysis (dedicated tools are better)
    - Image scanning (use Trivy, Grype, etc.)

The rule: use Claude for tasks that require judgment,
not for tasks that have deterministic answers.
```

## Verification

Ask the user:
```
Let's verify understanding:

1. What flag makes Claude Code run without permission prompts
   in a CI pipeline?

2. You want to add PR review to your GitHub Actions. What's
   the main cost consideration?

3. Should you use Claude Code to run your unit tests in CI?
   Why or why not?
```

Expected answers:
1. `--dangerously-skip-permissions` (or pre-configured allowlists)
2. Every PR push triggers a review — cost scales with PR frequency and diff size. Budget accordingly.
3. No — running tests is deterministic. Just run `pytest` or `npm test`. Claude adds value for tasks requiring judgment, not mechanical execution.

If successful, print:
```
All checks passed. You understand CI/CD integration patterns.
```

## Challenge

```
Design (don't implement yet) a CI/CD integration for one
of your projects:

1. Pick a project and a pipeline stage (PR review, deploy
   validation, or incident analysis)
2. Write the Claude Code command that would run in that stage
   (include flags, model choice, and prompt)
3. Estimate the monthly cost based on your team's activity
4. Identify what secrets/credentials the pipeline needs

Tell me:
  1. Which project and stage you chose
  2. Your Claude Code command
  3. Your cost estimate
  4. Required secrets
```

## Challenge Verification

Review the user's design. Check:
- The command uses `--print` and `--dangerously-skip-permissions` (or equivalent)
- A model is specified (cost control)
- The prompt is focused on a judgment task, not a deterministic one
- Secrets are mentioned (API key at minimum)

Accept any reasonable design.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/17.done
```

If successful, print:
```
Module 17 complete.

You can now integrate Claude Code into CI/CD pipelines.
Key patterns:
  - Non-interactive: --print --dangerously-skip-permissions
  - Model routing: --model sonnet for cost control
  - Secrets: API key via environment variables, never in code
  - Scope: judgment tasks (review, validation), not mechanical tasks

GitHub Actions:
  - PR review on pull_request events
  - Post as PR comments with gh cli
  - Budget: ~$15-50/month for active repos

OpenShift Pipelines:
  - Tekton tasks for deploy validation
  - Secret via secretKeyRef
  - RBAC: read-only for validation steps

Decision framework:
  Requires judgment?  --> Claude Code
  Deterministic?      --> Use a dedicated tool

Next module: /learn-18-profile-cleanup

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```

<!-- NEW -->
