<!-- NEW -->
# Module 23 — RHDP-Flow MCP

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 11 recommended (Building MCP Servers -- for context on how MCP servers work)

Install and use the RHDP-Flow MCP server to manage OpenShift workshop deployments through 15 structured tools.

## Quick Setup (skip the walkthrough)

If you already understand MCP servers and just want the tools working:

1. `pip install -e /path/to/rhdp-flow-mcp` (or install from the plugin)
2. Add to `.claude/settings.json`:
   ```json
   {
     "mcpServers": {
       "rhdp-flow": {
         "type": "stdio",
         "command": "python3",
         "args": ["-m", "rhdp_flow_mcp"],
         "env": { "FLOW_API_URL": "http://localhost:8000" }
       }
     }
   }
   ```
3. Restart Claude Code
4. Verify: ask Claude "check flow health" -- it should call `flow_health`

Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module depends on services outside your local environment:

- **Flow API backend** -- the MCP server wraps the RHDP-Flow REST API. You need either a local dev server (`http://localhost:8000`), a local container, or access to the production OCP route.
- **OpenShift cluster** -- the Flow backend connects to a cluster for workshop provisioning. `oc whoami` must succeed.
- **PyPI** -- `mcp[cli]`, `httpx`, and `pydantic` packages.

## Orientation

Print this once at the start:

```
You're setting up the RHDP-Flow MCP server, which gives Claude Code 15 tools
for workshop deployment automation. This takes about 20 minutes.

RHDP-Flow is the team's workshop automation system. It deploys OpenShift
workshops from CSV schedules, manages operations (lock, extend, scale),
runs QA checks, and handles resource pools. The MCP server wraps all of
this into structured tools that Claude Code can call directly.

We'll cover:
  1. Configure the MCP server and connect to the Flow backend
  2. Explore the catalog of available workshops
  3. Check resource pool availability
  4. Generate a deployment CSV from structured input
  5. Validate and dry-run a deployment

After this module you'll be able to manage workshops through Claude Code
instead of the Flow UI or CLI.

You'll need:
  - Claude Code installed and working (Module 01)
  - Access to the Flow API (local or OCP route)
  - oc CLI configured with cluster access
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.started
```

## Preflight

Run these checks automatically. Show results as EXISTS/MISSING.

### Check 1: Claude Code installed

```bash
which claude >/dev/null 2>&1 && echo "EXISTS: Claude Code CLI" || echo "MISSING: Claude Code CLI -- complete Module 01 first"
```

### Check 2: Python 3.10+ available

```bash
python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null && echo "EXISTS: Python 3.10+" || echo "MISSING: Python 3.10+ required"
```

### Check 3: oc CLI configured

```bash
oc whoami >/dev/null 2>&1 && echo "EXISTS: oc CLI authenticated as $(oc whoami)" || echo "MISSING: oc CLI not authenticated -- run 'oc login' first"
```

### Check 4: rhdp-flow-mcp installed

```bash
python3 -c "import rhdp_flow_mcp" 2>/dev/null && echo "EXISTS: rhdp-flow-mcp package" || echo "MISSING: rhdp-flow-mcp package -- will install in Step 1"
```

### Check 5: MCP server registered

```bash
if [ -f .claude/settings.json ] && grep -q "rhdp-flow" .claude/settings.json 2>/dev/null; then
  echo "EXISTS: rhdp-flow MCP server in settings"
else
  echo "MISSING: rhdp-flow MCP server not registered -- will configure in Step 1"
fi
```

Print summary: how many checks passed, what needs to be done.

---

## Step 1 — Configure the MCP server

**Goal:** Install the rhdp-flow-mcp package and register it with Claude Code.

### Install the package

```bash
pip install -e /path/to/rhdp-flow-mcp
```

### Determine the Flow API URL

Ask the user which backend they want to connect to:

| Option | URL | When to use |
|--------|-----|-------------|
| Local dev server | `http://localhost:8000` | Running `rhdp_flow.py serve` locally |
| Local container | `http://localhost:<port>` | Running Flow in podman/docker |
| OCP route | `https://rhdp-flow.apps.<cluster>` | Production/staging cluster |

### Register the MCP server

```bash
claude mcp add rhdp-flow -- python3 -m rhdp_flow_mcp
```

Or add to `.claude/settings.json` manually with the `FLOW_API_URL` environment variable.

### Verification

Ask Claude: "check flow health"

Expected: Claude calls `flow_health` and returns backend status including cluster URL, user identity, and connection status.

```
{
  "status": "ok",
  "oc_connected": true,
  "cluster_url": "https://api.cluster.example.com:6443",
  "user": "system:serviceaccount:...",
  "message": "Connected to cluster"
}
```

If status is "error", check:
- Is the Flow backend running?
- Is `FLOW_API_URL` set correctly?
- Can you reach the URL from your terminal? (`curl -sf $FLOW_API_URL/api/health`)

---

## Step 2 — Explore the catalog

**Goal:** Browse available workshop catalog items and understand their parameters.

### List catalog items

Ask Claude: "list available catalog items"

Expected: Claude calls `flow_catalog_items` and returns the full catalog.

Walk through the output with the user:
- **id**: the catalog item identifier (e.g., `openshift-cnv.ocp-virt-roadshow-multi-user.prod`)
- **description**: what the workshop teaches
- **max_users**: maximum users per deployment (exceeding this causes validation errors)
- **parameters**: configurable settings for the workshop

### Verification

User can identify at least one catalog item ID, its max user limit, and describe what it does.

---

## Step 3 — Check resource pools

**Goal:** Understand pool availability before deploying.

### List all pools

Ask Claude: "show me the resource pools"

Expected: Claude calls `flow_pools` and returns pool status.

Explain the fields:
- **ready**: instances available for immediate claim
- **claimed**: instances currently in use
- **provisioning**: instances being set up

### Look up a specific pool

Ask Claude: "check the pool for `<catalog_item_id>`" (use one from Step 2)

Expected: Claude calls `flow_pool_lookup` with the catalog item.

### Verification

User can read pool status and knows whether instances are available for their chosen catalog item.

---

## Step 4 — Generate a deployment CSV

**Goal:** Create a valid Flow CSV from structured input without manual editing.

### Build the input

Help the user construct a JSON input for a single workshop:

```json
{
  "workshops": [
    {
      "ci": "<catalog_item_from_step_2>",
      "namespace": "user-<username>",
      "users": 10
    }
  ],
  "start_time": "2026-05-07T14:00:00",
  "auto_stop_hours": 8,
  "auto_destroy_days": 14,
  "password": "workshop123"
}
```

### Generate the CSV

Ask Claude: "generate a flow CSV with this input: <json>"

Expected: Claude calls `flow_generate_csv` and returns a valid CSV string.

Walk through the output:
- Date format is DD/MM/YYYY HH:MM (not US format)
- Auto-stop is calculated from start_time + auto_stop_hours
- Auto-destroy is calculated from start_time + auto_destroy_days
- CI Name defaults to the CI value

### Verification

The generated CSV has the correct columns, date format, and calculated stop/destroy times.

---

## Step 5 — Validate and dry-run

**Goal:** Upload the CSV, validate it against catalog rules, and preview the deployment.

### Upload

Ask Claude: "upload this CSV to Flow" and provide the CSV from Step 4.

Expected: Claude calls `flow_upload_csv` and returns the upload result with row count.

### Validate

Ask Claude: "validate the uploaded schedules"

Expected: Claude calls `flow_validate` with check="all" and returns validation results.

If validation finds issues:
- **num_users**: a row exceeds the catalog item's max_users
- **catalog_namespaces**: a namespace doesn't match the expected pattern

### Dry-run

Ask Claude: "do a dry-run deployment"

Expected: Claude calls `flow_deploy` with dry_run=true and returns the manifests that would be applied.

Review the dry-run output: resource names, namespaces, labels.

### Verification

Upload succeeded, validation passed (or user understands the violations), and dry-run shows the expected manifests.

---

## Verification

All five steps produce expected output:

| Step | Check |
|------|-------|
| 1 | `flow_health` returns status "ok" |
| 2 | Can list and describe catalog items |
| 3 | Can read pool availability |
| 4 | CSV generates with correct format and calculations |
| 5 | Upload, validate, and dry-run all succeed |

---

## Challenge

Generate a staggered bulk deployment CSV for a real catalog item on the team cluster:

1. Pick a catalog item from the team's catalog
2. Create a bulk deployment with:
   - 5 workshop instances
   - 10-minute staggered intervals
   - 20 users per instance
   - 8-hour auto-stop, 14-day auto-destroy
3. Generate the CSV using `flow_generate_csv`
4. Validate the CSV using `flow_validate`
5. Dry-run the deployment using `flow_deploy` with dry_run=true

## Challenge Verification

- The generated CSV has 5 rows
- Provisioning dates are staggered by 10 minutes (e.g., 10:00, 10:10, 10:20, 10:30, 10:40)
- Validation passes with no errors
- Dry-run succeeds and shows 5 sets of manifests

---

## Completion

On module completion, write the progress marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.done
```
