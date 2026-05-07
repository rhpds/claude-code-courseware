# Module 21 -- Plugin Marketplace

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 09 recommended (Writing Custom Skills)

Discover, install, and manage Claude Code plugins from marketplace registries. When complete, you'll have marketplaces configured, understand how to evaluate plugins, and know how to install, inspect, and remove them.

## External Dependencies

This module depends on services outside your local environment:

- **GitHub** -- marketplace repos are hosted on GitHub. You need network access and (for private marketplaces) SSH access to the org.
- **Claude Code CLI** -- plugin management uses `claude plugin add`, `claude plugin remove`, and related commands. If the CLI syntax changes in a future Claude Code release, these commands may need updating.
- **Marketplace repositories** -- plugin availability depends on what the marketplace maintainers have published. Plugins may be added, removed, or renamed at any time.

## Orientation

Print this once at the start:

```
You're learning the Claude Code plugin ecosystem.
This takes about 15 minutes.

Plugins extend Claude Code with new skills, MCP servers, hooks, and
agent definitions -- packaged for easy installation and updates.
Marketplaces are registries of plugins you can browse and install.

We'll cover:
  1. Plugins vs skills vs MCP servers -- what's what
  2. Browsing available plugins
  3. Installing a plugin
  4. Inspecting installed plugins
  5. Removing a plugin

You'll need:
  - Claude Code installed and working (Module 01)
  - GitHub access (for marketplace repos)
```

## Install-Only Option

This module is conceptual -- there is no single thing to "install." If the user just wants to install specific plugins quickly, direct them to `/quick-install` instead.

```
This module teaches the plugin ecosystem. If you just want to install
a specific plugin or MCP server, run /quick-install instead.

Continue with the full walkthrough? (yes / switch to /quick-install)
```

If the user wants to switch, tell them to run `/quick-install`. Otherwise continue.

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/21.started
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Plugins directory?
[ -d "$HOME/.claude/plugins" ] && echo "EXISTS: ~/.claude/plugins/ directory" || echo "MISSING: ~/.claude/plugins/ directory (will be created on first plugin install)"

# Known marketplaces configured?
if [ -f "$HOME/.claude/plugins/known_marketplaces.json" ]; then
  count=$(python3 -c "
import json
with open('$HOME/.claude/plugins/known_marketplaces.json') as f:
    data = json.load(f)
print(len(data))
" 2>/dev/null)
  echo "EXISTS: known_marketplaces.json ($count marketplace(s) configured)"
else
  echo "MISSING: No marketplaces configured yet"
fi

# Count installed plugins
if [ -d "$HOME/.claude/plugins/cache" ]; then
  count=$(find "$HOME/.claude/plugins/cache" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: $count plugin(s) installed"
else
  echo "MISSING: No plugins installed yet"
fi

# Git available?
command -v git &>/dev/null && echo "EXISTS: git $(git --version | head -1)" || echo "MISSING: git not found"

# GitHub SSH access?
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "EXISTS: GitHub SSH access" || echo "MISSING: GitHub SSH access (some marketplaces may require it)"
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found.

## Step 1 -- Understand plugins vs skills vs MCP servers

This step is informational -- nothing to install.

Explain:
```
Three ways to extend Claude Code:

  SKILLS
    A single SKILL.md file in a named directory.
    Teaches Claude a repeatable workflow.
    Location: ~/.claude/skills/<name>/SKILL.md (global)
              .claude/commands/<name>.md (project)
    Example: /quick-deck generates a branded HTML presentation

  PLUGINS
    A package containing: plugin.json manifest + one or more skills +
    optional MCP servers + optional hooks + optional agent definitions.
    Versioned, updatable, distributable via marketplaces.
    Location: ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/
    Example: superpowers plugin provides TDD, debugging, and
             collaboration skills as a coordinated package

  MCP SERVERS
    A running process that gives Claude structured access to an
    external system (Git, Jira, Playwright, etc.).
    Configured in ~/.claude/settings.json under "mcpServers".
    Example: @modelcontextprotocol/server-git provides git_status,
             git_log, git_diff tools

  Key differences:
    Skills are standalone files. Plugins bundle multiple skills.
    MCP servers are running processes. Plugins can include MCP servers.
    Skills and MCP servers can exist without plugins.
    Plugins add discoverability, versioning, and one-command install.
```

## Step 2 -- Browse available plugins

Check what marketplaces are configured and what plugins they offer:

```bash
echo "=== Configured Marketplaces ==="
if [ -f "$HOME/.claude/plugins/known_marketplaces.json" ]; then
  python3 -c "
import json
with open('$HOME/.claude/plugins/known_marketplaces.json') as f:
    data = json.load(f)
for name, info in data.items():
    source = info.get('source', 'unknown')
    plugin_count = len(info.get('plugins', {}))
    print(f'  {name}')
    print(f'    Source: {source}')
    print(f'    Plugins: {plugin_count}')
" 2>/dev/null
else
  echo "  No marketplaces configured."
  echo "  We will add one in the next step."
fi

echo ""
echo "=== Installed Plugins ==="
if [ -d "$HOME/.claude/plugins/cache" ]; then
  find "$HOME/.claude/plugins/cache" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | while read dir; do
    marketplace=$(basename "$(dirname "$dir")")
    plugin=$(basename "$dir")
    versions=$(ls "$dir" 2>/dev/null | head -1)
    echo "  $plugin (from $marketplace, version: $versions)"
  done
else
  echo "  No plugins installed yet."
fi
```

If no marketplaces are configured, tell the user to add one. The courseware plugin itself comes from a marketplace, so check if `rhpds-marketplace` or `claude-plugins-official` is already present. If neither exists:

```
No marketplaces configured. Let's add the official Anthropic marketplace:

  ! claude plugin add github:anthropics/claude-plugins-official

This gives you access to plugins like superpowers, atlassian, and more.
```

After adding, verify:
```bash
[ -f "$HOME/.claude/plugins/known_marketplaces.json" ] && echo "PASS: Marketplace configured" || echo "FAIL: Marketplace not found"
```

Explain:
```
Marketplaces are just GitHub repos with a manifest listing available plugins.
When you add a marketplace, Claude Code clones it and reads the plugin catalog.

You can add multiple marketplaces -- your team might have a private one
alongside the official Anthropic marketplace.
```

## Step 3 -- Install a plugin

Check which plugins the user does NOT have installed. Suggest one that is lightweight and useful. Default suggestion: `frontend-design` from `claude-plugins-official` if not installed; otherwise pick another uninstalled plugin.

```bash
# Find an uninstalled plugin to suggest
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official"
for plugin in frontend-design pyright-lsp superpowers; do
  if [ ! -d "$CACHE/$plugin" ]; then
    echo "SUGGEST:$plugin"
    break
  fi
done
```

If the suggested plugin is found in a known marketplace:
```
Let's install PLUGIN_NAME:

  ! claude plugin add github:SOURCE_REPO
```

If not found in a known marketplace:
```
To discover and install plugins interactively, run /install inside
Claude Code and search for the plugin name.
```

After install, verify:
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/PLUGIN_NAME"
if [ -d "$CACHE" ]; then
  version=$(ls "$CACHE" 2>/dev/null | head -1)
  echo "PASS: $PLUGIN_NAME installed (version: $version)"
else
  echo "FAIL: $PLUGIN_NAME not found in cache"
fi
```

## Step 4 -- Inspect installed plugins

Show the user how to examine what a plugin contains:

```bash
echo "=== All Installed Plugins ==="
python3 << 'PYEOF'
import os, json

cache_root = os.path.expanduser("~/.claude/plugins/cache")
if not os.path.isdir(cache_root):
    print("  No plugins installed.")
    exit(0)

total = 0
for marketplace in os.listdir(cache_root):
    marketplace_path = os.path.join(cache_root, marketplace)
    if not os.path.isdir(marketplace_path):
        continue
    for plugin in os.listdir(marketplace_path):
        plugin_path = os.path.join(marketplace_path, plugin)
        if not os.path.isdir(plugin_path):
            continue
        versions = os.listdir(plugin_path)
        if not versions:
            continue
        latest = versions[0]
        version_path = os.path.join(plugin_path, latest)
        total += 1
        print(f"\n  {plugin} (from {marketplace})")
        print(f"    Version: {latest}")

        # Check for plugin.json
        manifest = os.path.join(version_path, "plugin.json")
        if os.path.exists(manifest):
            with open(manifest) as f:
                m = json.load(f)
            print(f"    Description: {m.get('description', 'none')}")

        # Count skills
        skills_dir = os.path.join(version_path, "skills")
        if os.path.isdir(skills_dir):
            skill_names = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
            print(f"    Skills ({len(skill_names)}): {', '.join(skill_names)}")
        else:
            print("    Skills: none")

        # Check for agents
        agents_dir = os.path.join(version_path, ".claude", "agents")
        if os.path.isdir(agents_dir):
            agent_files = [f for f in os.listdir(agents_dir) if f.endswith('.md')]
            print(f"    Agents ({len(agent_files)}): {', '.join(f.replace('.md','') for f in agent_files)}")

print(f"\n  Total: {total} plugin(s)")
PYEOF
```

Explain:
```
Each plugin lives in ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/.

Inside you'll find:
  plugin.json  -- manifest with name, description, version
  skills/      -- SKILL.md files that become available as slash commands
  .claude/     -- optional agents, hooks, and other config

Skills from installed plugins appear in your /slash command list automatically.
```

## Step 5 -- Remove a plugin

Demonstrate removing the plugin installed in Step 3, then offer to reinstall it:

```
To remove a plugin:

  ! claude plugin remove PLUGIN_NAME
```

Verify removal:
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/PLUGIN_NAME"
if [ ! -d "$CACHE" ]; then
  echo "PASS: PLUGIN_NAME removed"
else
  echo "FAIL: PLUGIN_NAME still present"
fi
```

Ask the user:
```
PLUGIN_NAME has been removed. Want to reinstall it?
(If yes, we'll add it back. If no, it stays removed.)
```

If yes, reinstall it.

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=4

# 1. Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. At least one marketplace configured
if [ -f "$HOME/.claude/plugins/known_marketplaces.json" ]; then
  count=$(python3 -c "import json; print(len(json.load(open('$HOME/.claude/plugins/known_marketplaces.json'))))" 2>/dev/null)
  if [ "$count" -gt 0 ] 2>/dev/null; then
    echo "PASS: $count marketplace(s) configured"
    PASS=$((PASS+1))
  else
    echo "FAIL: No marketplaces configured"
  fi
else
  echo "FAIL: No marketplaces file found"
fi

# 3. Can list plugins from cache
if [ -d "$HOME/.claude/plugins/cache" ]; then
  count=$(find "$HOME/.claude/plugins/cache" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo "PASS: Plugin cache exists ($count plugin(s))"
  PASS=$((PASS+1))
else
  echo "FAIL: No plugin cache directory"
fi

# 4. At least one plugin installed
if [ -d "$HOME/.claude/plugins/cache" ]; then
  count=$(find "$HOME/.claude/plugins/cache" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ] 2>/dev/null; then
    echo "PASS: $count plugin(s) installed"
    PASS=$((PASS+1))
  else
    echo "FAIL: No plugins installed"
  fi
else
  echo "FAIL: No plugins installed"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass:
```
All checks passed. You can manage plugins confidently.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Using what you've learned:

1. List all plugins available from your configured marketplaces
2. Pick one plugin you haven't used before and install it
3. Inspect its contents -- what skills does it provide? Any agents?
4. Count your total installed plugins

Tell me:
  a. Which plugin you installed
  b. What skills it added (list the skill names)
  c. Your total installed plugin count
  d. One thing you learned about plugins that was not obvious
```

## Challenge Verification

The user should provide:
1. The name of the plugin they installed
2. A list of skills from that plugin
3. Their total plugin count
4. An insight about the plugin system

To verify, confirm:
- The named plugin exists in their cache directory
- The skill count matches what's in the plugin's skills/ directory
- The total count is plausible given their marketplace configuration

Accept any reasonable answer for item 4.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/21.done
```

If successful, print:
```
Module 21 complete.

You can now manage Claude Code plugins:

  Browse:   check ~/.claude/plugins/cache/ or marketplace repos
  Install:  claude plugin add github:org/repo
  Inspect:  explore the plugin's skills/ and plugin.json
  Remove:   claude plugin remove PLUGIN_NAME
  Audit:    /learn-18-profile-cleanup covers plugin cleanup

For quick installs without the tutorial, use /quick-install.

Key concepts:
  - Skills are standalone files; plugins bundle multiple skills
  - MCP servers are running processes; plugins can include them
  - Marketplaces are GitHub repos with plugin catalogs
  - Plugins are versioned and updatable

Next module: Module 22 (Workshop Intake) is coming soon.

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
