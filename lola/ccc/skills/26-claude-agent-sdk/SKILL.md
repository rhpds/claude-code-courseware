---
name: 26-claude-agent-sdk
description: "Build programmatic AI agents using the Claude Agent SDK -- the same engine that powers Claude Code, available as a Python and TypeScript library."
---

# - Claude Agent SDK
<!-- NEW -->

Estimated time: 25 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 11 recommended (Building MCP Servers)

Build programmatic AI agents using the Claude Agent SDK -- the same engine that powers Claude Code, available as a Python and TypeScript library.

## Quick Setup (skip the walkthrough)

If you already understand agentic patterns and just want the SDK running:

1. `pip3 install claude-agent-sdk`
2. Write `agent.py`:
   ```python
   import asyncio
   from claude_agent_sdk import query, ClaudeAgentOptions

   async def main():
       async for message in query(
           prompt="What files are in this directory?",
           options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
       ):
           if hasattr(message, "result"):
               print(message.result)

   asyncio.run(main())
   ```
3. `python3 agent.py`

Verify: you see a listing of the current directory. Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module depends on services outside your local environment:

- **PyPI** -- the `claude-agent-sdk` package is installed from pypi.org (maintained by Anthropic).
- **npm** -- the `@anthropic-ai/claude-agent-sdk` package for the TypeScript path (optional).
- **Python 3.10+** -- required by the SDK.
- **Claude Code CLI** -- the SDK wraps it as a subprocess. The Python package bundles the CLI automatically, so no separate install is needed.
- **API key or Vertex AI** -- the SDK authenticates via `ANTHROPIC_API_KEY`, or via `CLAUDE_CODE_USE_VERTEX=1` for Google Vertex AI (which Red Hat uses).

## Orientation

Print this once at the start:

```
You're learning the Claude Agent SDK -- how to build programmatic agents
that have the same capabilities as Claude Code, controlled from Python
or TypeScript.

This takes about 25 minutes.

We'll cover:
  1. What the Agent SDK is and how it relates to Claude Code
  2. Installing the Python SDK
  3. Agent SDK vs Client SDK -- when to use each
  4. Building your first agent
  5. Key primitives: tools, hooks, MCP, subagents
  6. Production patterns: permissions, sessions, error handling
  7. Headless execution with claude -p

After this module you'll know how to build agents that read files, run
commands, fix bugs, and interact with external systems -- all from a
Python script.

You'll need:
  - Claude Code installed and working (Module 01)
  - Python 3.10+ installed
  - pip for package management
  - An Anthropic API key or Vertex AI configured
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/26.started
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code $(claude --version 2>/dev/null | head -1)" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Python 3.10+?
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
  if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
    echo "EXISTS: Python $PY_VERSION"
  else
    echo "MISSING: Python 3.10+ required (found $PY_VERSION)"
  fi
else
  echo "MISSING: Python 3 -- install Python 3.10 or later"
fi

# pip available?
python3 -m pip --version &>/dev/null && echo "EXISTS: pip $(python3 -m pip --version | awk '{print $2}')" || echo "MISSING: pip -- install with: python3 -m ensurepip"

# claude-agent-sdk already installed?
python3 -c "import claude_agent_sdk" &>/dev/null 2>&1 && echo "EXISTS: claude-agent-sdk Python package" || echo "MISSING: claude-agent-sdk Python package (will install in Step 2)"

# Node.js 18+ (optional, for TypeScript path)?
if command -v node &>/dev/null; then
  NODE_VERSION=$(node --version | sed 's/v//')
  NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 18 ]; then
    echo "EXISTS: Node.js $NODE_VERSION (TypeScript path available)"
  else
    echo "INFO: Node.js $NODE_VERSION found but 18+ recommended for TypeScript path"
  fi
else
  echo "INFO: Node.js not found -- TypeScript path unavailable (Python path works fine)"
fi

# API key or Vertex AI configured?
if [ -n "$ANTHROPIC_API_KEY" ]; then
  echo "EXISTS: ANTHROPIC_API_KEY set"
elif [ "$CLAUDE_CODE_USE_VERTEX" = "1" ]; then
  echo "EXISTS: Vertex AI configured (CLAUDE_CODE_USE_VERTEX=1)"
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
  echo "EXISTS: Google Cloud credentials found (Vertex AI likely configured)"
else
  echo "INFO: No API key or Vertex AI detected -- SDK will use Claude Code's existing auth"
fi
```

If Claude Code or Python 3.10+ is MISSING, stop and tell the user:
```
Claude Code or Python 3.10+ is not installed.
  - Claude Code: complete Module 01 first (/learn-01-vertex-setup)
  - Python: install from https://www.python.org or via your package manager
```

Print a summary of what was found. Skip steps where the item already exists.

## Step 1 -- What the Agent SDK is

This step is informational. No commands to run.

Explain:

```
What the Agent SDK gives you:

  The Claude Agent SDK is a Python and TypeScript library that wraps the
  Claude Code CLI as a subprocess. It gives you programmatic access to
  the same tools, agent loop, and context management that power Claude
  Code -- Read, Write, Edit, Bash, Glob, Grep, WebSearch, and more.

  How it works:

     Your script          Agent SDK           Claude Code (subprocess)
     -----------          ---------           ------------------------
     query(prompt)   ->   Launches CLI   ->   Claude thinks, calls tools
                     <-   Streams msgs   <-   Returns results
                          (async for)

  The SDK handles:
    - Spawning the Claude Code process
    - Serializing prompts and options
    - Streaming messages back as Claude works
    - Tool execution (Claude runs the tools directly)
    - Session management and context

  You just write a prompt and iterate over the results.

  History: Originally released as "Claude Code SDK" in mid-2025, renamed
  to "Claude Agent SDK" in September 2025 to reflect its use beyond
  coding tasks.

  The Python package is claude-agent-sdk on PyPI.
  The TypeScript package is @anthropic-ai/claude-agent-sdk on npm.
  Both bundle the Claude Code CLI, so no separate install is needed.
```

## Step 2 -- Install the Python SDK

Skip if `claude_agent_sdk` is already importable.

Explain:
```
The Python SDK requires Python 3.10 or later. It bundles the Claude
Code CLI automatically, so you don't need to install it separately.
```

Tell the user:
```
Install the Agent SDK:

  ! pip3 install claude-agent-sdk
```

Verify:
```bash
# Can we import it?
python3 -c "
import claude_agent_sdk
print('PASS: claude-agent-sdk is installed')
" 2>/dev/null || echo "FAIL: claude-agent-sdk not importable -- check pip install output"

# Verify the key imports work
python3 -c "
from claude_agent_sdk import query, ClaudeAgentOptions
print('PASS: query and ClaudeAgentOptions importable')
" 2>/dev/null || echo "FAIL: could not import query or ClaudeAgentOptions"
```

## Step 3 -- Agent SDK vs Client SDK

This step is informational. No commands to run.

Explain:
```
There are two Anthropic SDKs. They solve different problems:

  AGENT SDK (claude-agent-sdk)
  ----------------------------
  - Claude handles tool execution autonomously
  - Built-in tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch
  - You write a prompt, Claude figures out the rest
  - Best for: CI/CD bots, code review, batch processing, internal tools
  - Install: pip install claude-agent-sdk

    async for message in query(prompt="Fix the bug in auth.py"):
        print(message)  # Claude reads, analyzes, and edits the file

  CLIENT SDK (anthropic)
  ----------------------
  - You implement tool execution yourself
  - Direct Messages API access
  - You define tools, handle the tool loop, parse results
  - Best for: chatbots, RAG, custom tool implementations, fine control
  - Install: pip install anthropic

    response = client.messages.create(...)
    while response.stop_reason == "tool_use":
        result = your_tool_executor(response)  # YOU run the tool
        response = client.messages.create(tool_result=result, ...)

  Rule of thumb:
    - Need Claude to act on files, run commands, edit code? Agent SDK.
    - Need direct API access with your own tools? Client SDK.
    - Building a chatbot or RAG pipeline? Client SDK.
    - Automating code reviews or CI checks? Agent SDK.
```

## Step 4 -- Build your first agent

Explain:
```
We'll write a Python script that uses the Agent SDK to scan a directory
and report its structure. This demonstrates the core pattern: call
query() with a prompt and options, then iterate over the streamed
messages.
```

Tell the user:
```
Create a project directory and write the agent script:

  ! mkdir -p ~/repos/agent-sdk-demo

  ! cat > ~/repos/agent-sdk-demo/file_scanner.py << 'PYEOF'
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    print("Starting file scanner agent...")
    print()

    async for message in query(
        prompt=(
            "List all files in the current directory. "
            "For each file, report its name and size in bytes. "
            "Present the results as a brief summary."
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Bash"],
            permission_mode="dontAsk",
            max_turns=10,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print()
            print(f"Agent finished: {message.subtype}")


asyncio.run(main())
PYEOF
```

Explain the key parts:
```
Breaking down the code:

  query(prompt, options)
    The main entry point. Returns an async iterator of messages.
    Claude reads the prompt, decides which tools to use, and streams
    results back.

  ClaudeAgentOptions(...)
    Controls agent behavior:
    - allowed_tools: which tools are auto-approved (no user prompt)
    - permission_mode: "dontAsk" denies anything not in allowed_tools
    - max_turns: limits how many tool calls the agent can make

  async for message in query(...):
    The agentic loop. Each iteration yields a message:
    - AssistantMessage: Claude's reasoning or a tool call
    - ResultMessage: the final outcome (success, error, or limit hit)

  The loop ends when Claude finishes the task or hits a limit.
```

Tell the user:
```
Run the agent to verify it works:

  ! cd ~/repos/agent-sdk-demo && python3 file_scanner.py
```

Verify:
```bash
# Script exists and has valid syntax?
[ -f "$HOME/repos/agent-sdk-demo/file_scanner.py" ] && echo "PASS: file_scanner.py exists" || echo "FAIL: file_scanner.py not found"
python3 -c "import ast; ast.parse(open('$HOME/repos/agent-sdk-demo/file_scanner.py').read()); print('PASS: valid Python syntax')" 2>/dev/null || echo "FAIL: syntax errors in file_scanner.py"

# Contains the key imports?
grep -q 'from claude_agent_sdk import query' "$HOME/repos/agent-sdk-demo/file_scanner.py" 2>/dev/null && echo "PASS: imports query from claude_agent_sdk" || echo "FAIL: missing query import"
grep -q 'ClaudeAgentOptions' "$HOME/repos/agent-sdk-demo/file_scanner.py" 2>/dev/null && echo "PASS: uses ClaudeAgentOptions" || echo "FAIL: missing ClaudeAgentOptions"
```

## Step 5 -- Key primitives

This step is informational with code examples. No commands to run.

Explain:
```
The Agent SDK has four key primitives beyond the basic query() call:

1. TOOLS -- Built-in and custom

   Built-in tools are the same ones Claude Code uses:
   Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Monitor

   You control access with allowed_tools and permission_mode:
     - allowed_tools: auto-approve listed tools (no prompts)
     - disallowed_tools: block specific tools entirely
     - permission_mode: controls what happens for unlisted tools

   Permission modes:
     dontAsk       -- deny anything not in allowed_tools (safest)
     acceptEdits   -- auto-approve file edits, ask for other actions
     bypassPermissions -- run everything without prompts (sandboxed only)
     default       -- require a canUseTool callback for decisions

2. HOOKS -- Lifecycle callbacks

   SDK hooks let you run custom Python code at key points:
     PreToolUse    -- before a tool runs (validate, block, log)
     PostToolUse   -- after a tool runs (audit, transform results)
     Stop          -- when the agent finishes
     SessionStart  -- when a session begins
     SessionEnd    -- when a session ends

   Example -- log every file edit to an audit trail:

     from claude_agent_sdk import HookMatcher

     async def log_edit(input_data, tool_use_id, context):
         path = input_data.get("tool_input", {}).get("file_path", "?")
         with open("audit.log", "a") as f:
             f.write(f"edited: {path}\n")
         return {}

     options = ClaudeAgentOptions(
         hooks={
             "PostToolUse": [
                 HookMatcher(matcher="Edit|Write", hooks=[log_edit])
             ]
         },
     )

3. MCP INTEGRATION -- External servers

   Connect MCP servers just like in Claude Code settings:

     options = ClaudeAgentOptions(
         mcp_servers={
             "playwright": {
                 "command": "npx",
                 "args": ["@playwright/mcp@latest"]
             }
         }
     )

   The agent can then use any tools exposed by that MCP server.
   This is how you connect databases, browsers, APIs, or your own
   custom MCP servers (Module 11).

4. SUBAGENTS -- Delegating work

   Spawn specialized child agents for focused subtasks:

     from claude_agent_sdk import AgentDefinition

     options = ClaudeAgentOptions(
         allowed_tools=["Read", "Glob", "Agent"],
         agents={
             "security-reviewer": AgentDefinition(
                 description="Reviews code for security issues.",
                 prompt="Analyze for vulnerabilities and report findings.",
                 tools=["Read", "Glob", "Grep"],
             )
         },
     )

   The main agent can invoke "security-reviewer" when it decides a
   security review is needed. Include "Agent" in allowed_tools to
   auto-approve subagent invocations.
```

## Step 6 -- Production patterns

This step is informational. No commands to run.

Explain:
```
When moving from experimentation to production, apply these patterns:

PRINCIPLE OF LEAST PRIVILEGE
  Only allow the tools your agent actually needs:

    # Read-only analysis agent
    ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="dontAsk",
    )

    # Code modification agent (scoped)
    ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob"],
        permission_mode="acceptEdits",
    )

    # Full automation (sandboxed environments only)
    ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="bypassPermissions",
    )

HOOK-BASED VALIDATION
  Use PreToolUse hooks to enforce guardrails:

    async def block_dangerous_commands(input_data, tool_use_id, ctx):
        cmd = input_data.get("tool_input", {}).get("command", "")
        if any(word in cmd for word in ["rm -rf", "sudo", "chmod 777"]):
            return {"decision": "block", "reason": "Blocked dangerous command"}
        return {}

    options = ClaudeAgentOptions(
        hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_dangerous_commands])]},
    )

SESSION MANAGEMENT
  Continue conversations across multiple queries:

    # First query -- capture session ID
    session_id = None
    async for msg in query(prompt="Read the config files", options=opts):
        if isinstance(msg, SystemMessage) and msg.subtype == "init":
            session_id = msg.data["session_id"]

    # Second query -- resume with full context
    async for msg in query(
        prompt="Now check for misconfigurations",
        options=ClaudeAgentOptions(resume=session_id),
    ):
        ...

ERROR HANDLING
  Wrap the agent loop and handle failures:

    try:
        async for message in query(prompt=task, options=opts):
            if isinstance(message, ResultMessage):
                if message.subtype == "error":
                    print(f"Agent error: {message.result}")
                else:
                    print(f"Success: {message.result}")
    except Exception as e:
        print(f"SDK error: {e}")
```

## Step 7 -- Headless execution with claude -p

Explain:
```
For CI/CD and automation, you can run Claude as a one-shot command
without the Agent SDK -- just the CLI. The -p flag runs a prompt
non-interactively:

  claude -p "Review this code for bugs" --output-format json

This is the simplest path for:
  - GitHub Actions workflows
  - Pre-commit hooks
  - Batch processing scripts
  - Quick one-off automation

Key flags:
  -p "prompt"           -- run non-interactively with this prompt
  --output-format json  -- return structured JSON output
  --json-schema FILE    -- validate output against a JSON schema
  --allowedTools TOOLS  -- restrict which tools the agent can use
  --max-turns N         -- limit the number of tool calls

Example -- structured output with a schema:
```

Tell the user:
```
Try headless execution with a simple prompt:

  ! claude -p "What files are in the current directory? Reply with just the filenames, one per line." --output-format text

For structured output, you can pipe through jq:

  ! claude -p "List the Python files in the current directory. Return a JSON object with a 'files' key containing an array of filenames." --output-format json 2>/dev/null | python3 -m json.tool
```

Explain:
```
When to use the CLI vs the SDK:

  CLI (claude -p):
    - One-shot tasks, CI/CD pipelines, shell scripts
    - No Python/TypeScript dependency needed
    - Simple prompt-in, result-out

  SDK (query()):
    - Multi-step agents, session management
    - Custom hooks and callbacks
    - Programmatic control over the agent loop
    - Integration with larger Python applications
    - Subagent orchestration

Both use the same underlying engine. The SDK is for when you need
programmatic control; the CLI is for when a shell command is enough.

For CI/CD integration, see Module 17 (/learn-17-ci-cd-integration).
```

## Verification

Run all checks and report:

```bash
PASS_COUNT=0
TOTAL=5

# 1. Python 3.10+
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
if [ "$PY_MINOR" -ge 10 ]; then
  echo "PASS: Python 3.10+ installed"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: Python 3.10+ required"
fi

# 2. claude-agent-sdk installed
if python3 -c "from claude_agent_sdk import query, ClaudeAgentOptions" 2>/dev/null; then
  echo "PASS: claude-agent-sdk installed and importable"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: claude-agent-sdk not importable"
fi

# 3. Demo script exists with valid syntax
if python3 -c "import ast; ast.parse(open('$HOME/repos/agent-sdk-demo/file_scanner.py').read())" 2>/dev/null; then
  echo "PASS: file_scanner.py exists with valid syntax"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: file_scanner.py missing or has syntax errors"
fi

# 4. Demo script uses Agent SDK correctly
if grep -q 'from claude_agent_sdk import query' "$HOME/repos/agent-sdk-demo/file_scanner.py" 2>/dev/null && \
   grep -q 'ClaudeAgentOptions' "$HOME/repos/agent-sdk-demo/file_scanner.py" 2>/dev/null; then
  echo "PASS: file_scanner.py uses Agent SDK correctly"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: file_scanner.py missing Agent SDK imports"
fi

# 5. Claude Code CLI available
if command -v claude &>/dev/null; then
  echo "PASS: Claude Code CLI available"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: Claude Code CLI not found"
fi

echo ""
echo "$PASS_COUNT/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. The Agent SDK is installed and your demo agent is ready.
```

If any fail:
```
Troubleshooting:

  claude-agent-sdk not importable:
    Run: pip3 install claude-agent-sdk

  Python 3.10+ required:
    Install from https://www.python.org or via your package manager.

  file_scanner.py missing:
    Re-run Step 4 to create the demo agent.

  Claude Code CLI not found:
    Complete Module 01 first (/learn-01-vertex-setup).
```

## Challenge

```
Build a Python agent that scans the current directory for Python files,
counts lines of code and TODO comments, and produces a JSON report.

Your agent script should:
  1. Use query() with allowed_tools=["Read", "Glob", "Bash"]
  2. Ask Claude to scan for all .py files in the current directory
  3. For each file, count total lines and lines containing "TODO"
  4. Write the results to a file called scan_report.json with this structure:
     {
       "files_scanned": 3,
       "total_lines": 150,
       "total_todos": 5,
       "details": [
         {"file": "example.py", "lines": 50, "todos": 2},
         ...
       ]
     }
  5. Print a summary when done

Starter template (fill in the parts marked FILL_IN):

  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

  async def main():
      prompt = """FILL_IN: Write a prompt that tells Claude to:
      - Find all .py files in the current directory
      - Count lines and TODO comments in each
      - Write results to scan_report.json
      """

      async for message in query(
          prompt=prompt,
          options=ClaudeAgentOptions(
              allowed_tools=FILL_IN,  # What tools does the agent need?
              permission_mode=FILL_IN,  # What permission mode is appropriate?
          ),
      ):
          if isinstance(message, ResultMessage):
              print(f"Agent finished: {message.subtype}")

  asyncio.run(main())

After writing the agent, run it:
  python3 your_agent.py

Then verify headless execution works:
  claude -p "Read scan_report.json and summarize the results" --output-format text

Tell me:
  1. How many Python files were scanned
  2. How many total TODOs were found
  3. Whether headless execution with claude -p worked
```

## Challenge Verification

Verify the challenge by checking:

1. The agent script exists and uses the SDK:
```bash
AGENT_FILE=""
for f in "$HOME/repos/agent-sdk-demo"/*.py; do
  if grep -q 'scan_report' "$f" 2>/dev/null; then
    AGENT_FILE="$f"
    break
  fi
done
if [ -n "$AGENT_FILE" ]; then
  echo "PASS: Agent script found at $AGENT_FILE"
  grep -q 'from claude_agent_sdk import' "$AGENT_FILE" && echo "PASS: Uses Agent SDK" || echo "FAIL: Does not import from claude_agent_sdk"
else
  echo "INFO: No agent script with scan_report found -- check the user's working directory"
fi
```

2. A scan report was generated:
```bash
if [ -f "scan_report.json" ]; then
  echo "PASS: scan_report.json exists"
  python3 -c "
import json
with open('scan_report.json') as f:
    data = json.load(f)
files = data.get('files_scanned', data.get('files', len(data.get('details', []))))
todos = data.get('total_todos', data.get('todos', 0))
print(f'  Files scanned: {files}')
print(f'  Total TODOs: {todos}')
print('PASS: valid JSON structure')
" 2>/dev/null || echo "FAIL: scan_report.json is not valid JSON"
else
  echo "MISSING: scan_report.json not found in current directory"
fi
```

3. Ask the user for their results:
```
Confirm:
  - How many Python files were scanned?
  - How many TODOs were found?
  - Did claude -p produce output when reading the report?
```

If the user confirms all three, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/26.done
```

Then print:
```
Module 26 complete.

You can now build programmatic agents with the Claude Agent SDK.
You know how to:
  - Install and import the Agent SDK (claude-agent-sdk)
  - Use query() with ClaudeAgentOptions for the agentic loop
  - Choose between Agent SDK (tool execution) and Client SDK (direct API)
  - Apply production patterns: least privilege, hooks, sessions
  - Run headless agents with claude -p for CI/CD

Architecture recap:
  Your script  --query()-->  Agent SDK  --subprocess-->  Claude Code
                             (streams)                   (tools + reasoning)

Key configuration options:
  allowed_tools      -- which tools to auto-approve
  permission_mode    -- dontAsk, acceptEdits, bypassPermissions
  hooks              -- PreToolUse, PostToolUse callbacks
  mcp_servers        -- connect external MCP servers
  agents             -- define subagents for delegation
  resume / continue  -- session persistence

To clean up the demo:
  rm -rf ~/repos/agent-sdk-demo

Next module: /learn-27-checkpointing-session-management

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
