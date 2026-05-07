# Module 08 — Container and Podman MCP

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Connect Claude Code to your container runtime so you can build, run, inspect, and debug containers from the CLI.

## External Dependencies

This module depends on services outside your local environment:

- **Container MCP ecosystem** — the container/Podman MCP server landscape is immature and changing rapidly. Available packages may not install cleanly, may lack features, or may be deprecated without notice. This module has a built-in fallback to shell commands if no MCP server works.
- **Container runtime** — requires Podman or Docker installed and running. The module auto-detects which is available.
- **npm registry** (conditional) — if a container MCP package is attempted, it comes from npmjs.org. Package names and availability may change.

## Install-Only Option

After printing the Orientation, check if a container MCP server is already configured:

```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
if os.path.exists(path):
    s = json.load(open(path))
    servers = s.get('mcpServers', {})
    container_found = any(k for k in servers if any(w in k.lower() for w in ['podman', 'docker', 'container']))
    print('INSTALLED' if container_found else 'NOT_INSTALLED')
else:
    print('NOT_INSTALLED')
"
```

If INSTALLED: print "A container MCP server is already configured. Proceeding with the full walkthrough." Then continue to Progress Tracking.

If NOT_INSTALLED, ask the user:

```
Two paths available:

  INSTALL ONLY (~3 min)
    Detect your container runtime, configure MCP if a server
    package is available, or confirm shell fallback.

  FULL WALKTHROUGH (~15 min)
    Step-by-step tutorial covering container builds, inspection,
    debugging, and MCP vs shell workflows.

Which do you prefer? (install-only / full)
```

If the user chooses "install only":
1. Write the progress marker (see Progress Tracking below)
2. Detect container runtime (podman or docker)
3. If no runtime found, stop and tell the user to install one first
4. Attempt to find and install a container MCP server package
5. If no MCP server works, confirm shell fallback is available
6. Write completion marker:
   ```bash
   date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/08.done
   ```
7. Print:
   ```
   Module 08 complete (install-only path).

   Container runtime detected. MCP server configured (or shell fallback active).
   Run /learn-08-container-podman-mcp again any time for the full walkthrough.

   Next module: /learn-09-writing-custom-skills
   ```

If the user chooses "full" or gives no clear answer: continue with the existing module content from Progress Tracking onward.

## Orientation

Print this once at the start:

```
You're connecting Claude Code to your container runtime.
This takes about 15 minutes.

We'll set up:
  1. Discover your container runtime (Podman or Docker)
  2. Install and configure a container MCP server if needed
  3. Run, inspect, and debug containers from Claude Code

You'll need:
  - Claude Code installed and working (Module 01)
  - A container runtime (Podman or Docker) installed
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/08.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Container runtime available?
if command -v podman &>/dev/null; then
  echo "EXISTS: Podman $(podman --version 2>/dev/null | head -1)"
elif command -v docker &>/dev/null; then
  echo "EXISTS: Docker $(docker --version 2>/dev/null | head -1)"
else
  echo "MISSING: No container runtime found (Podman or Docker)"
  echo "  Install Podman: https://podman.io/getting-started/installation"
  echo "  Install Docker: https://docs.docker.com/get-docker/"
fi

# Check 3 — Container runtime is running?
if command -v podman &>/dev/null; then
  podman info &>/dev/null 2>&1 && echo "EXISTS: Podman daemon reachable" || echo "MISSING: Podman daemon not running — try: podman machine start"
elif command -v docker &>/dev/null; then
  docker info &>/dev/null 2>&1 && echo "EXISTS: Docker daemon reachable" || echo "MISSING: Docker daemon not running — start Docker Desktop or run: sudo systemctl start docker"
fi

# Check 4 — Container MCP server configured?
if [ -f "$HOME/.claude/settings.json" ]; then
  if python3 -c "
import json, sys
d = json.load(open('$HOME/.claude/settings.json'))
servers = d.get('mcpServers', {})
for name in servers:
  if 'podman' in name.lower() or 'docker' in name.lower() or 'container' in name.lower():
    print(f'EXISTS: Container MCP server found: {name}')
    sys.exit(0)
print('MISSING: No container MCP server in settings.json')
" 2>/dev/null; then
    :
  fi
else
  echo "MISSING: No ~/.claude/settings.json found"
fi

# Check 5 — Node.js available (needed for npx-based MCP servers)?
NODE_PATH=$(command -v node 2>/dev/null)
if [ -z "$NODE_PATH" ]; then
  echo "INFO: Node.js not found — may be needed if installing an MCP server"
else
  echo "EXISTS: Node.js $(node --version) at $NODE_PATH"
fi
```

Print a summary of what was found. Skip any step below where the item already exists and is valid.

If Claude Code is MISSING, stop:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

If no container runtime is found, present the two-track option:
```
No container runtime detected. Two options:

  FULL EXPERIENCE (recommended):
    Install Podman or Docker, then re-run this module.
    Podman: brew install podman && podman machine init && podman machine start
    Docker: Install Docker Desktop from https://docs.docker.com/get-docker/

  CONCEPTUAL OVERVIEW:
    Continue without a runtime. You'll learn what container MCP
    enables and see the configuration, but you won't be able
    to run or inspect containers interactively.
```

## Step 1 — Configure the Container MCP Server

Skip if a container MCP server is already configured and working.

If a container MCP server was found in preflight, test that its tools are available. If tools like `mcp__podman__*` or similar prefixes are present, skip to Step 2.

If no container MCP server is configured, we need to set one up. The approach depends on what's available:

Tell the user:
```
No container MCP server is configured yet. Let me check what's
available for your container runtime.
```

Search for the user's container runtime MCP server. Check if there's a known MCP server package for their runtime:

```bash
# Check for known container MCP packages
echo "Searching for container MCP packages..."

# Check if @anthropic/podman-mcp or similar exists
npm search podman mcp 2>/dev/null | head -5
npm search docker mcp 2>/dev/null | head -5

# Check if the user has a custom/internal MCP server
if [ -f "$HOME/.claude/settings.json" ]; then
  echo ""
  echo "Current MCP servers in settings.json:"
  python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
for name in d.get('mcpServers', {}):
  print(f'  {name}')
" 2>/dev/null
fi
```

Based on results, guide the user to install and configure the appropriate MCP server. Use the four-phase MCP install pattern from the template:

1. Install the package globally
2. Smoke test the server process
3. Write the config to `~/.claude/settings.json` with full paths
4. Restart Claude Code and verify tools are available

If no suitable MCP package is found:
```
No pre-built container MCP server package was found.
You can still use Claude Code with containers via shell commands.

Claude Code can run podman/docker commands directly through the
Bash tool — this module will show you how to use that effectively.
```

## Step 2 — Pull and Run a Container

Demonstrate basic container operations. Use whichever MCP tools are available, or fall back to Bash tool with podman/docker commands.

Tell the user:
```
Let's pull and run a lightweight container to test the setup.
We'll use a simple HTTP server image.
```

Run these operations (via MCP tools if available, otherwise Bash):

```bash
# Detect runtime
RUNTIME=$(command -v podman || command -v docker)

# Pull a lightweight image
$RUNTIME pull docker.io/library/httpd:alpine 2>&1

# Run it
$RUNTIME run -d --name claude-test-container -p 8199:80 httpd:alpine 2>&1

# Verify it's running
$RUNTIME ps --filter name=claude-test-container 2>&1

# Test the HTTP server
sleep 2
curl -sf http://localhost:8199/ && echo "PASS: Container responding" || echo "FAIL: Container not responding"
```

Show the user the running container details.

## Step 3 — Inspect and Debug

Demonstrate container inspection and log viewing.

```bash
RUNTIME=$(command -v podman || command -v docker)

# Inspect container metadata
$RUNTIME inspect claude-test-container --format '{{.Config.Image}} - {{.State.Status}}' 2>&1

# View logs
$RUNTIME logs claude-test-container 2>&1

# Check resource usage
$RUNTIME stats claude-test-container --no-stream 2>&1
```

Explain:
```
These operations — inspect, logs, stats — are the core debugging
workflow for containers. With the MCP server (or shell access),
you can ask Claude Code natural language questions like:
  "What containers are running?"
  "Show me the logs for my app container"
  "Why is the container restarting?"
```

## Step 4 — Cleanup

```bash
RUNTIME=$(command -v podman || command -v docker)
$RUNTIME stop claude-test-container 2>&1
$RUNTIME rm claude-test-container 2>&1
echo "Test container cleaned up."
```

## Verification

Run all checks as PASS/FAIL:

```bash
PASS=0
TOTAL=3

# 1. Container runtime available
(command -v podman &>/dev/null || command -v docker &>/dev/null) && { echo "PASS: Container runtime available"; PASS=$((PASS+1)); } || echo "FAIL: No container runtime"

# 2. Runtime is responsive
RUNTIME=$(command -v podman || command -v docker)
$RUNTIME info &>/dev/null 2>&1 && { echo "PASS: Runtime responsive"; PASS=$((PASS+1)); } || echo "FAIL: Runtime not responding"

# 3. Can pull and run containers
$RUNTIME pull docker.io/library/alpine:latest &>/dev/null 2>&1 && { echo "PASS: Image pull works"; PASS=$((PASS+1)); } || echo "FAIL: Cannot pull images"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. Container operations are working with Claude Code.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Using Claude Code, do the following container operations:

1. Pull the nginx:alpine image
2. Run it on port 8200 with the name "courseware-nginx"
3. Verify it responds with curl
4. Check the container logs
5. Stop and remove the container

Tell me:
  1. The image digest from the pull
  2. The first line of the nginx access log after your curl request
```

## Challenge Verification

Verify by checking:
1. The user provided an image digest (sha256:...)
2. The log line contains a GET request to /

If the container is still running, clean it up.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/08.done
```

If successful, print:
```
Module 08 complete.

You can now manage containers from Claude Code.
Key operations:
  - Pull images: "pull the redis image"
  - Run containers: "run nginx on port 8080"
  - Inspect: "what containers are running?"
  - Logs: "show me the app container logs"
  - Debug: "why is the container crashing?"
  - Cleanup: "stop and remove all test containers"

Natural language workflows:
  "Build and run the Dockerfile in this directory"
  "Check if any containers are using too much memory"
  "Show me the environment variables in the running container"

Next module: /learn-09-writing-custom-skills

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```

<!-- NEW -->
