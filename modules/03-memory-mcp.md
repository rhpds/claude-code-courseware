# Module 03 — Memory MCP

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Teach Claude Code to remember across sessions using the Memory MCP knowledge graph. When complete, you can persist project context, team findings, and cross-session notes that survive restarts.

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

## Preflight

Check prerequisites and current state:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Node.js (required to run the MCP server)
command -v node &>/dev/null && echo "EXISTS: Node.js $(node --version)" || echo "MISSING: Node.js"

# Check for Memory MCP in user settings
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

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Configure the Memory MCP server

Skip if a memory MCP server is already configured in user settings or project config.

Explain:
```
The Memory MCP server runs locally via npx. It stores its knowledge graph
in a JSON file on your machine. We'll add it to your user-level settings
so it's available across all projects.
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

Add the Memory MCP server:

```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

memory_file = os.path.expanduser("~/.claude/memory.json")

settings["mcpServers"]["memory"] = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {
        "MEMORY_FILE_PATH": memory_file
    }
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"Memory MCP server added to ~/.claude/settings.json")
print(f"Knowledge graph file: {memory_file}")
PYEOF
```

Verify:
```bash
python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
if 'memory' in d.get('mcpServers', {}):
    cfg = d['mcpServers']['memory']
    print('PASS: Memory MCP server configured')
    print(f'  Command: {cfg[\"command\"]} {\" \".join(cfg[\"args\"])}')
    print(f'  Memory file: {cfg.get(\"env\", {}).get(\"MEMORY_FILE_PATH\", \"default\")}')
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

The preflight will detect the config and skip Step 1 on re-entry.
```

Note: If the user needed to restart, the module resumes from Step 2 when re-run.

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

Next module: /learn-04-git-mcp (coming soon)
```
