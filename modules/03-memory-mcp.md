# Module 03 — Memory MCP

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Teach Claude Code to remember across sessions using the Memory MCP knowledge graph. When complete, you can persist project context, team findings, and cross-session notes that survive restarts.

## Install-Only Option

After printing the Orientation, check if Memory MCP is already installed:

```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
if os.path.exists(path):
    s = json.load(open(path))
    if 'memory' in s.get('mcpServers', {}):
        print('INSTALLED')
    else:
        print('NOT_INSTALLED')
else:
    print('NOT_INSTALLED')
"
```

If INSTALLED: print "Memory MCP is already installed and configured. Proceeding with the full walkthrough." Then continue to Progress Tracking.

If NOT_INSTALLED, ask the user:

```
Two paths available:

  INSTALL ONLY (~2 min)
    Install Memory MCP, verify it works, done.

  FULL WALKTHROUGH (~10 min)
    Step-by-step tutorial covering what Memory MCP does, knowledge
    graph basics, and hands-on practice with entities and relations.

Which do you prefer? (install-only / full)
```

If the user chooses "install only":
1. Write the progress marker (see Progress Tracking below)
2. Run Phase 1 through Phase 4 from Step 1 (dependency check, npm install, smoke test, config write)
3. Print restart instructions
4. On re-entry after restart, verify `mcp__memory__*` tools are available
5. Write completion marker:
   ```bash
   date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/03.done
   ```
6. Print:
   ```
   Module 03 complete (install-only path).

   Memory MCP is installed and configured.
   Run /learn-03-memory-mcp again any time for the full walkthrough.

   Next module: /learn-04-git-mcp
   ```

If the user chooses "full" or gives no clear answer: continue with the existing module content from Progress Tracking onward.

## External Dependencies

This module depends on services outside your local environment:

- **npm registry** — the `@modelcontextprotocol/server-memory` package is installed from npmjs.org. If the package is renamed, deprecated, or unpublished, installation will fail.
- **Node.js / npx** — the MCP server runs via `npx`. Config must use the full path to `npx` (not bare `npx`) or Claude Code may fail to find it on restart.

The server itself runs entirely locally with no network calls after installation. Data is stored in a local JSON file.

## Orientation

Print this once at the start:

```
You're setting up the Memory MCP server — a persistent knowledge graph
for Claude Code. This takes about 10 minutes.

Memory MCP gives Claude Code long-term memory that survives between sessions.
It stores a knowledge graph of entities (things), observations (facts about
things), and relations (connections between things) in a local JSON file.

We'll set up:
  1. Memory MCP server configuration
  2. Knowledge graph basics — entities, observations, relations
  3. Reading and searching the graph
  4. Creating and updating entities

Why this matters:
  When you start a new Claude Code session, context from previous sessions
  is gone. Memory MCP lets you persist project findings, architectural
  decisions, and team knowledge so Claude can pick up where it left off.
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/03.started
```

## Preflight

Check prerequisites and current state:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

### Phase 1 — Dependency Check

```bash
# Node.js
NODE_PATH=$(command -v node 2>/dev/null)
if [ -z "$NODE_PATH" ]; then
  echo "MISSING: Node.js — install from https://nodejs.org or via Homebrew: brew install node"
else
  echo "EXISTS: Node.js $(node --version) at $NODE_PATH"
fi

# npm
NPM_PATH=$(command -v npm 2>/dev/null)
if [ -z "$NPM_PATH" ]; then
  echo "MISSING: npm — should come with Node.js, reinstall Node"
else
  echo "EXISTS: npm $(npm --version) at $NPM_PATH"
fi

# npx
NPX_PATH=$(command -v npx 2>/dev/null)
if [ -z "$NPX_PATH" ]; then
  echo "MISSING: npx — should come with npm, reinstall Node"
else
  echo "EXISTS: npx at $NPX_PATH"
fi
```

If any of Node.js, npm, or npx are MISSING, stop and tell the user what to install.

```bash
# PATH consistency — ensure Claude Code can find node on restart
LOGIN_PATH=$(zsh -l -c 'echo $PATH' 2>/dev/null || bash -l -c 'echo $PATH' 2>/dev/null)
NODE_DIR=$(dirname "$(command -v node)")
if echo "$LOGIN_PATH" | tr ':' '\n' | grep -q "$NODE_DIR"; then
  echo "PASS: Node directory ($NODE_DIR) is in login shell PATH"
else
  echo "WARNING: $NODE_DIR is not in login shell PATH"
  echo "  Claude Code may not find node/npx on restart."
  echo "  Add this to ~/.zshrc or ~/.zprofile:"
  echo "    export PATH=\"$NODE_DIR:\$PATH\""
fi
```

If PATH consistency fails, stop and tell the user to fix their PATH before continuing.

```bash
# Check for Memory MCP already configured in user settings
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
try:
    d = json.load(open('$HOME/.claude/settings.json'))
    servers = d.get('mcpServers', {})
    found = False
    for name, cfg in servers.items():
        args = ' '.join(cfg.get('args', []))
        cmd = cfg.get('command', '')
        if 'memory' in name.lower() or 'memory' in args.lower():
            print(f'EXISTS: Memory MCP server \"{name}\" in ~/.claude/settings.json')
            print(f'  Command: {cmd}')
            if cmd == 'npx':
                print(f'  WARNING: Config uses bare \"npx\" — should be a full path.')
                print(f'  Step 1 will fix this.')
            found = True
            break
    if not found:
        print('MISSING: No memory MCP server in ~/.claude/settings.json')
except:
    print('MISSING: could not parse ~/.claude/settings.json')
" 2>/dev/null
else
  echo "MISSING: ~/.claude/settings.json does not exist"
fi

# Check for project-level memory config
if [ -f ".mcp.json" ]; then
  python3 -c "
import json
d = json.load(open('.mcp.json'))
servers = d.get('mcpServers', {})
for name, cfg in servers.items():
    args = ' '.join(cfg.get('args', []))
    if 'memory' in name.lower() or 'memory' in args.lower():
        print(f'EXISTS: Memory MCP server \"{name}\" in project .mcp.json')
        break
" 2>/dev/null || true
fi

# Check if a memory file exists in common locations
MEMORY_FOUND=false
for MPATH in "$HOME/.claude/memory.json" "$HOME/memory.json" "$HOME/.memory/memory.json"; do
  if [ -f "$MPATH" ]; then
    ENTITY_COUNT=$(python3 -c "
import json
d = json.load(open('$MPATH'))
entities = d.get('entities', [])
print(len(entities))
" 2>/dev/null || echo "0")
    echo "EXISTS: Memory file ($MPATH) with $ENTITY_COUNT entities"
    MEMORY_FOUND=true
    break
  fi
done
if [ "$MEMORY_FOUND" = false ]; then
  echo "MISSING: No memory file yet (will be created on first use)"
fi
```

Print a summary of what was found. If all Phase 1 checks pass and Memory MCP is already configured with a full path, skip to Step 2.

## Step 1 — Install and configure the Memory MCP server

Skip if Memory MCP is already configured with a full path to npx (not bare `npx`). If configured with bare `npx`, this step will fix it.

### Step 1a — Install the package globally

Explain:
```
We install the Memory MCP package globally so npx never needs to
download it at runtime. This eliminates silent download failures that
can prevent the server from starting.
```

```bash
echo "Installing @modelcontextprotocol/server-memory globally..."
npm install -g @modelcontextprotocol/server-memory
npm list -g @modelcontextprotocol/server-memory --depth=0 2>/dev/null
if [ $? -ne 0 ]; then
  echo "FAIL: npm install failed"
  echo "  Try: sudo npm install -g @modelcontextprotocol/server-memory"
  echo "  Or configure a user prefix: npm config set prefix ~/.npm-global"
  echo "  Then add ~/.npm-global/bin to your PATH"
else
  echo "PASS: @modelcontextprotocol/server-memory installed globally"
fi
```

### Step 1b — Smoke test the server

Explain:
```
Before writing any config, we verify the server actually starts.
We'll launch it, wait a few seconds, and check if the process is alive.
```

```bash
NPX_FULL=$(command -v npx)
echo "Smoke test: launching server with $NPX_FULL..."
$NPX_FULL -y @modelcontextprotocol/server-memory &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "PASS: Server process started (PID $SERVER_PID)"
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  wait $SERVER_PID 2>/dev/null
  EXIT_CODE=$?
  echo "FAIL: Server process exited immediately (exit code $EXIT_CODE)"
  echo "  Possible causes:"
  echo "    - Permission error on memory file"
  echo "    - Package not installed correctly"
  echo "  Debug with: $NPX_FULL -y @modelcontextprotocol/server-memory 2>&1"
fi
```

If the smoke test fails, stop and help the user diagnose. Do not write config for a server that cannot start.

### Step 1c — Write config with full npx path

Explain:
```
Now we write the MCP server config to ~/.claude/settings.json using the
fully resolved path to npx. This makes the config immune to PATH
differences between your terminal and Claude Code's shell environment.
```

Check if `~/.claude/settings.json` exists:

```bash
if [ -f "$HOME/.claude/settings.json" ]; then
  echo "File exists — will merge the MCP server entry"
  cat "$HOME/.claude/settings.json"
else
  echo "File does not exist — will create it"
fi
```

Write the config:

```bash
python3 << 'PYEOF'
import json, os, shutil, subprocess

path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

# Resolve full path to npx — never use bare "npx"
npx_path = shutil.which("npx")
if not npx_path:
    npx_path = subprocess.check_output(
        "command -v npx", shell=True, text=True
    ).strip()

if not npx_path:
    print("FAIL: Cannot find npx. Install Node.js first.")
    raise SystemExit(1)

memory_file = os.path.expanduser("~/.claude/memory.json")

settings["mcpServers"]["memory"] = {
    "command": npx_path,
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {
        "MEMORY_FILE_PATH": memory_file
    }
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"Memory MCP server added to ~/.claude/settings.json")
print(f"  npx path: {npx_path}")
print(f"  Knowledge graph file: {memory_file}")
PYEOF
```

Verify the config was written correctly:

```bash
python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
if 'memory' in d.get('mcpServers', {}):
    cfg = d['mcpServers']['memory']
    cmd = cfg['command']
    print('PASS: Memory MCP server configured')
    print(f'  Command: {cmd} {\" \".join(cfg[\"args\"])}')
    print(f'  Memory file: {cfg.get(\"env\", {}).get(\"MEMORY_FILE_PATH\", \"default\")}')
    if '/' in cmd:
        print(f'  PASS: Command uses full path')
    else:
        print(f'  FAIL: Command is bare \"{cmd}\" — should be a full path')
else:
    print('FAIL: memory not found in mcpServers')
"
```

Tell the user:
```
IMPORTANT: Claude Code needs to be restarted to pick up the new MCP server.

1. Exit this Claude Code session (Ctrl+C or type /exit)
2. Relaunch Claude Code: claude .
3. Re-run this module: /learn-03-memory-mcp

On re-entry, we'll verify the server is live before continuing.
If it isn't, we'll diagnose why — you won't be left stuck.
```

Note: If the user needed to restart, the module resumes from Step 2 when re-run.

### Post-Restart Verification

On re-entry after restart, verify the Memory MCP tools are actually available in this session before continuing to Step 2.

Check if any `mcp__memory__*` tools are available. If they are:
```
PASS: Memory MCP tools are live in this session.
Continuing to Step 2.
```

If config exists but tools are NOT available, run the diagnostic ladder:

```bash
# Diagnostic Step 1: Is the npx path in config still valid?
NPX_IN_CONFIG=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
print(d['mcpServers']['memory']['command'])
")
if [ -x "$NPX_IN_CONFIG" ]; then
  echo "PASS: npx path in config ($NPX_IN_CONFIG) is executable"
else
  echo "FAIL: npx path in config ($NPX_IN_CONFIG) is not executable"
  echo "  Node.js may have been reinstalled to a different location."
  echo "  Current npx: $(command -v npx)"
  echo "  Fix: re-run Step 1c to update the config path."
fi
```

```bash
# Diagnostic Step 2: Can we launch the server manually?
NPX_IN_CONFIG=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
print(d['mcpServers']['memory']['command'])
")
echo "Attempting manual server launch..."
$NPX_IN_CONFIG -y @modelcontextprotocol/server-memory &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "Server launches fine — Claude Code may need another restart."
  echo "Try: exit and run 'claude .' again."
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  wait $SERVER_PID 2>/dev/null
  echo "FAIL: Server fails to launch. Checking stderr..."
  $NPX_IN_CONFIG -y @modelcontextprotocol/server-memory 2>&1 | head -20
fi
```

Print exactly what is wrong and what to do next.

## Step 2 — Read the knowledge graph

This step uses the Memory MCP tools directly. If the tools are not available, tell the user to restart Claude Code (see Step 1).

Explain:
```
The knowledge graph has three building blocks:

  Entity      — a thing with a name and type (e.g., "ops-hub" of type "project")
  Observation — a fact about an entity (e.g., "uses React + PatternFly 6")
  Relation    — a link between entities (e.g., ops-hub "depends on" jira-mcp)

Let's see what's already in your graph.
```

Use the `read_graph` MCP tool to read the current knowledge graph.

If the graph is empty:
```
Your knowledge graph is empty — that's normal for a fresh setup.
We'll add some data in the next step.
```

If the graph has data, print a summary:
```
Your graph already has data from previous sessions:
  Entities: <count>
  Relations: <count>

Some entities in your graph:
  <list first 5-10 entity names and types>
```

## Step 3 — Create an entity

Explain:
```
Let's create an entity. We'll document this courseware project in the
knowledge graph so Claude remembers it in future sessions.
```

First, use `search_nodes` with query `claude-code-courseware` to check if the entity already exists. If it does, skip creation and tell the user:
```
Entity "claude-code-courseware" already exists in your graph.
Skipping creation — we'll add a new observation instead in Step 4.
```

If it does not exist, use the `create_entities` MCP tool:
- Name: `claude-code-courseware`
- Type: `project`
- Observations:
  - `Interactive learning modules for the RHDP ops team`
  - `Delivered as Claude Code skills (slash commands)`
  - `Repository: claude-code-courseware`
  - `Modules cover: Vertex AI, Atlassian MCP, Memory MCP, Git MCP, and more`

After creating, use `open_nodes` with name `claude-code-courseware` and show the user:

```
Here's what the entity looks like in the graph:

  Name: claude-code-courseware
  Type: project
  Observations:
    - Interactive learning modules for the RHDP ops team
    - Delivered as Claude Code skills (slash commands)
    - Repository: claude-code-courseware
    - Modules cover: Vertex AI, Atlassian MCP, Memory MCP, Git MCP, and more
```

## Step 4 — Add observations to an existing entity

Explain:
```
Entities grow over time as you learn new things. You add observations
to existing entities without recreating them.
```

Use `add_observations` to add a new observation to the `claude-code-courseware` entity:
- `Module 03 (Memory MCP) completed on <today's date>`

Confirm:
```
Observation added. The entity now has <N> observations.
Observations accumulate — each session can add what it learned.
```

## Step 5 — Create relations

Explain:
```
Relations connect entities. They describe how things relate to each other.
Relations use active voice: "A uses B", "A depends-on B".
```

First, create a second entity so we have something to relate to. Check if `Memory-MCP` already exists via `search_nodes`. If not, create it:
- Name: `Memory-MCP`
- Type: `tool`
- Observations:
  - `MCP server for persistent knowledge graph storage`
  - `Stores entities, observations, and relations in a JSON file`
  - `Package: @modelcontextprotocol/server-memory`

Then use `create_relations`:
- From: `claude-code-courseware`
- To: `Memory-MCP`
- Relation type: `teaches`

Confirm:
```
Relation created: claude-code-courseware --teaches--> Memory-MCP

Relations make the graph navigable. When Claude encounters Memory-MCP
in a future session, it can follow this relation to discover that the
courseware project teaches it.
```

## Step 6 — Search the graph

Explain:
```
The search tool finds entities by matching against names, types, and
observation content. This is how Claude finds relevant context at the
start of a session.
```

Use `search_nodes` with query `courseware` and show the results:

```
Search for "courseware":
  - claude-code-courseware (project)
    "Interactive learning modules for the RHDP ops team"
```

Then use `search_nodes` with query `MCP` and show those results:

```
Search for "MCP":
  - Memory-MCP (tool)
    "MCP server for persistent knowledge graph storage"
  <plus any other MCP-related entities in the graph>
```

Explain:
```
The search tool is how Claude finds relevant memory at the start of a task.
When your CLAUDE.md says "check Memory MCP first," this is what it means —
Claude searches the graph for entities related to what you're working on.
```

## Verification

Run all operations and report:

1. `read_graph` — confirm the graph loads without error, count entities and relations
2. `search_nodes` with query `claude-code-courseware` — confirm the entity is found
3. `open_nodes` with name `claude-code-courseware` — confirm observations are present (should include the "Module 03 completed" observation from Step 4)
4. `open_nodes` with name `Memory-MCP` — confirm the second entity exists

Print:
```
PASS: read_graph — <N> entities, <M> relations
PASS: search — claude-code-courseware found
PASS: open — claude-code-courseware has <N> observations
PASS: open — Memory-MCP entity exists

All Memory MCP operations verified.
```

If any check fails:
```
Troubleshooting:

  Tools not available:
    Memory MCP server may not be running. Run /mcp to check server status.
    If not listed, verify ~/.claude/settings.json and restart Claude Code.

  Empty results:
    The memory file may have been reset. Re-run Steps 3-5.

  Permission errors:
    Check file permissions on the memory JSON file:
      ls -la ~/.claude/memory.json
```

## Challenge

```
Now let's use Memory MCP for a real team task.

Create a knowledge graph entry for yourself:

1. Create an entity for yourself:
   - Name: your first name (e.g., "Josh")
   - Type: "team-member"
   - Add at least 3 observations: your role, what projects you work on,
     and one fact about your Claude Code setup (e.g., which GCP project
     you use)

2. Create a relation connecting you to the courseware project:
   - From: your name
   - To: claude-code-courseware
   - Relation type: "enrolled-in"

3. Search for your name and confirm everything is stored.

Tell me:
  - What entity name did you use?
  - How many observations did you add?
  - What does the relation look like?
```

## Challenge Verification

The user should report:
1. An entity name (their first name or similar)
2. At least 3 observations
3. A relation connecting them to claude-code-courseware

To verify, use `search_nodes` with the user's entity name. Confirm:
- The entity exists with type `team-member`
- It has the observations they described

Then use `open_nodes` for `claude-code-courseware` to confirm it now has a relation from the user's entity.

If the user needs help, guide them:
```
Here's an example of what to tell me:

"Create an entity named Josh, type team-member, with these observations:
  - Senior SRE on the RHDP operations team
  - Works on ops-hub and rhdp-scheduler
  - Uses GCP project rhdp-vertex-01 for Claude Code

Then create a relation: Josh enrolled-in claude-code-courseware"
```

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/03.done
```

If successful, print:
```
Module 03 complete.

Claude Code now has a persistent knowledge graph via Memory MCP.
You can:
  - Create entities to document projects, tools, and team members
  - Add observations as you learn new facts
  - Create relations to map how things connect
  - Search the graph to find context from previous sessions

Key workflow:
  Session start  ->  search Memory for relevant context
  Session end    ->  persist key findings to Memory

Your knowledge graph: ~/.claude/memory.json
Entities so far: <count>

Next module: /learn-04-git-mcp

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
