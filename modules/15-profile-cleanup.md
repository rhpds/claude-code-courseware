# Module 15 — Claude Code Profile Cleanup

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Audit your Claude Code profile (`~/.claude/`) for duplicate skills, orphaned plugins, redundant agents, stale settings, and context window bloat. When complete, you'll have a lean profile that loads faster and consumes less of your context window on every session start.

## Orientation

Print this once at the start:

```
You're auditing and cleaning up your Claude Code profile.
This takes about 15 minutes.

Over time, ~/.claude/ accumulates clutter:
  - Duplicate skills (same skill registered in multiple places)
  - Orphaned plugin files (plugins removed but files left behind)
  - User-level agents that duplicate project-level ones
  - Stale MCP server entries that no longer work
  - Example or template skills that consume context but aren't used

Every skill file in ~/.claude/skills/ is loaded into your context
window at session start. Duplicates and unused skills directly
reduce the space available for your actual work.

We'll run:
  1. Skills audit — find duplicates, orphans, and bloat
  2. Agents audit — find redundant user-level agents
  3. Plugins audit — find orphaned or broken plugin installs
  4. MCP servers audit — find stale or duplicate server configs
  5. Context impact report — measure total profile footprint
  6. Guided cleanup — remove what you approve

No files are deleted without your confirmation.
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# ~/.claude/ directory exists?
[ -d "$HOME/.claude" ] && echo "EXISTS: ~/.claude/ directory" || echo "MISSING: ~/.claude/ directory"

# Skills directory exists?
if [ -d "$HOME/.claude/skills" ]; then
  count=$(ls -d "$HOME/.claude/skills"/*/ 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: ~/.claude/skills/ ($count skill directories)"
else
  echo "MISSING: ~/.claude/skills/ (no skills installed)"
fi

# Agents directory exists?
if [ -d "$HOME/.claude/agents" ]; then
  count=$(ls "$HOME/.claude/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: ~/.claude/agents/ ($count agent definitions)"
else
  echo "INFO: ~/.claude/agents/ does not exist (no user-level agents)"
fi

# Plugins directory exists?
if [ -d "$HOME/.claude/plugins" ]; then
  echo "EXISTS: ~/.claude/plugins/ directory"
else
  echo "INFO: ~/.claude/plugins/ does not exist (no plugins installed)"
fi

# Settings file exists?
[ -f "$HOME/.claude/settings.json" ] && echo "EXISTS: ~/.claude/settings.json" || echo "INFO: ~/.claude/settings.json does not exist"

# Installed plugins registry?
[ -f "$HOME/.claude/installed-plugins.json" ] && echo "EXISTS: ~/.claude/installed-plugins.json" || echo "INFO: ~/.claude/installed-plugins.json does not exist"
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found.

## Step 1 — Skills audit

Explain:
```
Skills are the biggest source of context window bloat. Every
SKILL.md file under ~/.claude/skills/ is loaded into your
conversation at session start — even if you never use that skill.

We'll check for:
  a. Duplicate skills (same skill name in multiple directories)
  b. Broken symlinks (skill directories that point to nothing)
  c. Empty or near-empty skill files (placeholder installs)
  d. Total character count (your context footprint)
```

Run the skills audit:

```bash
python3 << 'PYEOF'
import os, glob, collections

skills_dir = os.path.expanduser("~/.claude/skills")
if not os.path.isdir(skills_dir):
    print("No skills directory found. Nothing to audit.")
    exit(0)

entries = sorted(glob.glob(os.path.join(skills_dir, "*")))

total_chars = 0
total_files = 0
broken_links = []
empty_skills = []
skill_sizes = []

for entry in entries:
    name = os.path.basename(entry)

    # Check for broken symlinks
    if os.path.islink(entry) and not os.path.exists(entry):
        broken_links.append((name, os.readlink(entry)))
        continue

    # Find the SKILL.md file
    skill_file = None
    for candidate in ["SKILL.md", "skill.md"]:
        path = os.path.join(entry, candidate)
        if os.path.isfile(path):
            skill_file = path
            break

    if not skill_file:
        if os.path.isdir(entry):
            empty_skills.append(name)
        continue

    try:
        size = os.path.getsize(skill_file)
        with open(skill_file) as f:
            content = f.read()
        chars = len(content)
        total_chars += chars
        total_files += 1
        skill_sizes.append((name, chars, size))
    except (OSError, UnicodeDecodeError):
        empty_skills.append(name)

# Check for duplicate skill names across sources
# Skills can come from: direct files, symlinks to plugin repos, symlinks to project skills
link_targets = {}
for entry in entries:
    name = os.path.basename(entry)
    if os.path.islink(entry):
        target = os.path.realpath(entry)
        link_targets[name] = target

# Find skills that share content (potential duplicates)
content_hashes = collections.defaultdict(list)
for entry in entries:
    name = os.path.basename(entry)
    if os.path.islink(entry) and not os.path.exists(entry):
        continue
    for candidate in ["SKILL.md", "skill.md"]:
        path = os.path.join(entry, candidate)
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    h = hash(f.read())
                content_hashes[h].append(name)
            except:
                pass
            break

duplicates = {h: names for h, names in content_hashes.items() if len(names) > 1}

# Report
print("=" * 60)
print("SKILLS AUDIT")
print("=" * 60)
print()
print(f"Total skill directories: {len(entries)}")
print(f"Valid skill files:       {total_files}")
print(f"Broken symlinks:         {len(broken_links)}")
print(f"Empty/missing SKILL.md:  {len(empty_skills)}")
print(f"Total characters:        {total_chars:,}")
print(f"Context impact:          ~{total_chars // 1000}K chars loaded every session")
print()

if broken_links:
    print("BROKEN SYMLINKS (safe to remove):")
    for name, target in broken_links:
        print(f"  {name} -> {target}")
    print()

if empty_skills:
    print("EMPTY / NO SKILL.md (safe to remove):")
    for name in empty_skills:
        print(f"  {name}")
    print()

if duplicates:
    print("DUPLICATE CONTENT (same SKILL.md content):")
    for h, names in duplicates.items():
        print(f"  {', '.join(names)}")
    print()

# Top 10 by size
if skill_sizes:
    print("TOP 10 BY SIZE (largest context consumers):")
    for name, chars, size in sorted(skill_sizes, key=lambda x: -x[1])[:10]:
        is_link = " (symlink)" if os.path.islink(os.path.join(skills_dir, name)) else ""
        print(f"  {chars:>8,} chars  {name}{is_link}")
    print()
PYEOF
```

After the audit, explain the findings:
```
Each category above is a potential cleanup target:

  Broken symlinks — the target was deleted but the link remains.
    These are always safe to remove.

  Empty / no SKILL.md — directories that exist but have no skill
    content. Often left behind by incomplete installs or removals.

  Duplicate content — two skill directories with identical SKILL.md.
    One is redundant and can be removed.

  Large skills — not necessarily bad, but worth knowing which skills
    consume the most context. If you never use a skill that takes
    20K+ chars, removing it frees significant context space.
```

## Step 2 — Agents audit

Explain:
```
User-level agents in ~/.claude/agents/ load into every session
across all projects. If the same agent also exists in a project's
.claude/agents/, you get redundant definitions.

User-level agents are best for truly global agents you use
everywhere. Project-specific agents belong in the project.
```

Run the agents audit:

```bash
python3 << 'PYEOF'
import os, glob

user_agents_dir = os.path.expanduser("~/.claude/agents")
if not os.path.isdir(user_agents_dir):
    print("No user-level agents directory. Nothing to audit.")
    exit(0)

user_agents = {}
for f in glob.glob(os.path.join(user_agents_dir, "*.md")):
    name = os.path.basename(f)
    try:
        with open(f) as fh:
            content = fh.read()
        user_agents[name] = {"path": f, "size": len(content)}
    except:
        pass

if not user_agents:
    print("No user-level agent definitions found.")
    exit(0)

print("=" * 60)
print("AGENTS AUDIT")
print("=" * 60)
print()
print(f"User-level agents (~/.claude/agents/): {len(user_agents)}")
print()

total_chars = 0
for name, info in sorted(user_agents.items()):
    total_chars += info["size"]
    print(f"  {info['size']:>6,} chars  {name}")

print()
print(f"Total agent footprint: {total_chars:,} chars")
print()

# Check for project-level duplicates in common locations
home = os.path.expanduser("~")
repos_dir = os.path.join(home, "repos")
if os.path.isdir(repos_dir):
    print("CHECKING FOR PROJECT-LEVEL DUPLICATES:")
    found_any = False
    for project in os.listdir(repos_dir):
        project_agents = os.path.join(repos_dir, project, ".claude", "agents")
        if os.path.isdir(project_agents):
            for name in user_agents:
                project_file = os.path.join(project_agents, name)
                if os.path.isfile(project_file):
                    found_any = True
                    print(f"  DUPLICATE: {name}")
                    print(f"    User:    ~/.claude/agents/{name}")
                    print(f"    Project: ~/repos/{project}/.claude/agents/{name}")
    if not found_any:
        print("  No duplicates found between user-level and project-level agents.")
    print()

print("RECOMMENDATION:")
print("  Keep agents at user level only if you use them across")
print("  multiple projects. Move project-specific agents to the")
print("  project's .claude/agents/ directory instead.")
PYEOF
```

## Step 3 — Plugins audit

Explain:
```
Installed plugins register skills, MCP servers, and hooks. If a
plugin was partially removed or its repo was deleted, orphaned
files and broken registrations can linger.

We'll cross-reference the installed-plugins registry with what
actually exists on disk.
```

Run the plugins audit:

```bash
python3 << 'PYEOF'
import json, os, glob

installed_path = os.path.expanduser("~/.claude/installed-plugins.json")
plugins_dir = os.path.expanduser("~/.claude/plugins")
skills_dir = os.path.expanduser("~/.claude/skills")

print("=" * 60)
print("PLUGINS AUDIT")
print("=" * 60)
print()

# Load registry
registry = {}
if os.path.isfile(installed_path):
    try:
        with open(installed_path) as f:
            registry = json.load(f)
    except json.JSONDecodeError:
        print("WARNING: installed-plugins.json is corrupted")
        registry = {}

if not registry and not os.path.isdir(plugins_dir):
    print("No plugins installed. Nothing to audit.")
    exit(0)

print(f"Registered plugins: {len(registry)}")
for name, info in sorted(registry.items()):
    version = info.get("version", "unknown")
    marketplace = info.get("marketplace", "unknown")
    print(f"  {name} v{version} ({marketplace})")
print()

# Check for plugin directories not in registry
if os.path.isdir(plugins_dir):
    disk_plugins = set()
    for entry in os.listdir(plugins_dir):
        full = os.path.join(plugins_dir, entry)
        if os.path.isdir(full) and entry != "cache":
            disk_plugins.add(entry)

    orphaned_dirs = disk_plugins - set(registry.keys())
    if orphaned_dirs:
        print("ORPHANED PLUGIN DIRECTORIES (on disk but not in registry):")
        for name in sorted(orphaned_dirs):
            path = os.path.join(plugins_dir, name)
            size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, fnames in os.walk(path)
                for f in fnames
            )
            print(f"  {name}/ ({size:,} bytes)")
        print()

    missing_dirs = set(registry.keys()) - disk_plugins
    if missing_dirs:
        print("GHOST REGISTRATIONS (in registry but no directory on disk):")
        for name in sorted(missing_dirs):
            print(f"  {name}")
        print()

# Check for skill symlinks pointing into missing plugin dirs
if os.path.isdir(skills_dir):
    orphaned_skills = []
    for entry in os.listdir(skills_dir):
        full = os.path.join(skills_dir, entry)
        if os.path.islink(full):
            target = os.readlink(full)
            if "plugins" in target and not os.path.exists(full):
                orphaned_skills.append((entry, target))

    if orphaned_skills:
        print("ORPHANED SKILL SYMLINKS (point to removed plugins):")
        for name, target in orphaned_skills:
            print(f"  {name} -> {target}")
        print()

if not orphaned_dirs and not missing_dirs and not orphaned_skills:
    print("All plugins are clean. No orphans or ghost registrations.")
PYEOF
```

## Step 4 — MCP servers audit

Explain:
```
MCP server configurations can accumulate in multiple places:
  - ~/.claude/settings.json (user-level)
  - .mcp.json (project-level)
  - Registered via 'claude mcp add'

Stale entries for servers that no longer exist waste startup time
and can cause error messages on every session launch.
```

Run the MCP servers audit:

```bash
python3 << 'PYEOF'
import json, os

settings_path = os.path.expanduser("~/.claude/settings.json")

print("=" * 60)
print("MCP SERVERS AUDIT")
print("=" * 60)
print()

# User-level settings
if os.path.isfile(settings_path):
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        servers = settings.get("mcpServers", {})
        if servers:
            print(f"User-level MCP servers ({len(servers)}):")
            for name, config in sorted(servers.items()):
                server_type = config.get("type", "stdio")
                if server_type == "http":
                    url = config.get("url", "no url")
                    print(f"  {name} (http: {url})")
                else:
                    cmd = config.get("command", "no command")
                    args = config.get("args", [])
                    # Check if the command exists
                    cmd_base = cmd.split("/")[-1] if "/" in cmd else cmd
                    print(f"  {name} ({server_type}: {cmd_base})")
                    if cmd.startswith("/") and not os.path.exists(cmd):
                        print(f"    WARNING: command path does not exist: {cmd}")
                    if args:
                        for arg in args:
                            if isinstance(arg, str) and arg.startswith("/") and not os.path.exists(arg):
                                if "${" not in arg and "$HOME" not in arg:
                                    print(f"    WARNING: arg path does not exist: {arg}")
            print()
        else:
            print("No MCP servers in user-level settings.")
            print()
    except json.JSONDecodeError:
        print("WARNING: ~/.claude/settings.json is corrupted JSON")
        print()
else:
    print("No user-level settings file.")
    print()

# Project-level .mcp.json in current directory
mcp_json = ".mcp.json"
if os.path.isfile(mcp_json):
    try:
        with open(mcp_json) as f:
            mcp = json.load(f)
        servers = mcp.get("mcpServers", {})
        if servers:
            print(f"Project-level MCP servers ({len(servers)}):")
            for name, config in sorted(servers.items()):
                server_type = config.get("type", "stdio")
                cmd = config.get("command", config.get("url", "unknown"))
                print(f"  {name} ({server_type})")
            print()

            # Check for duplicates between user and project level
            if os.path.isfile(settings_path):
                with open(settings_path) as f:
                    user_settings = json.load(f)
                user_servers = set(user_settings.get("mcpServers", {}).keys())
                project_servers = set(servers.keys())
                overlap = user_servers & project_servers
                if overlap:
                    print("DUPLICATE MCP SERVERS (in both user and project config):")
                    for name in sorted(overlap):
                        print(f"  {name}")
                    print("  Project-level takes precedence. User-level entry is redundant")
                    print("  for this project but may be needed in other projects.")
                    print()
    except json.JSONDecodeError:
        print("WARNING: .mcp.json is corrupted JSON")
        print()

# Check settings.local.json too
local_settings = os.path.join(".claude", "settings.local.json")
if os.path.isfile(local_settings):
    try:
        with open(local_settings) as f:
            local = json.load(f)
        local_servers = local.get("mcpServers", {})
        if local_servers:
            print(f"Local settings MCP servers ({len(local_servers)}):")
            for name in sorted(local_servers.keys()):
                print(f"  {name}")
            print()
    except json.JSONDecodeError:
        pass
PYEOF
```

## Step 5 — Context impact report

Explain:
```
Let's measure the total footprint of your Claude Code profile.
Every character loaded at session start reduces the context
available for your actual work.

A clean profile typically uses under 50K chars. Heavy profiles
can exceed 500K — that's context you're paying for every message.
```

Run the full context impact analysis:

```bash
python3 << 'PYEOF'
import os, glob, json

home = os.path.expanduser("~")
claude_dir = os.path.join(home, ".claude")

categories = {}

# Skills
skills_dir = os.path.join(claude_dir, "skills")
skills_chars = 0
skills_count = 0
if os.path.isdir(skills_dir):
    for entry in sorted(os.listdir(skills_dir)):
        full = os.path.join(skills_dir, entry)
        if os.path.islink(full) and not os.path.exists(full):
            continue
        for candidate in ["SKILL.md", "skill.md"]:
            path = os.path.join(full, candidate)
            if os.path.isfile(path):
                try:
                    skills_chars += os.path.getsize(path)
                    skills_count += 1
                except:
                    pass
                break
categories["Skills"] = (skills_count, skills_chars)

# Agents
agents_dir = os.path.join(claude_dir, "agents")
agents_chars = 0
agents_count = 0
if os.path.isdir(agents_dir):
    for f in glob.glob(os.path.join(agents_dir, "*.md")):
        try:
            agents_chars += os.path.getsize(f)
            agents_count += 1
        except:
            pass
categories["Agents"] = (agents_count, agents_chars)

# Settings
for name in ["settings.json", "settings.local.json"]:
    path = os.path.join(claude_dir, name)
    if os.path.isfile(path):
        try:
            categories[name] = (1, os.path.getsize(path))
        except:
            pass

# CLAUDE.md files (loaded per-project, but good to know)
# Check current directory
claude_md = "CLAUDE.md"
if os.path.isfile(claude_md):
    categories["CLAUDE.md (this project)"] = (1, os.path.getsize(claude_md))

# Memory files
memory_dirs = glob.glob(os.path.join(claude_dir, "projects", "*", "memory"))
memory_chars = 0
memory_count = 0
for mdir in memory_dirs:
    for f in glob.glob(os.path.join(mdir, "*.md")):
        try:
            memory_chars += os.path.getsize(f)
            memory_count += 1
        except:
            pass
if memory_count:
    categories["Memory files (all projects)"] = (memory_count, memory_chars)

# Report
print("=" * 60)
print("CONTEXT IMPACT REPORT")
print("=" * 60)
print()
print(f"{'Category':<35} {'Count':>6} {'Size':>12}")
print("-" * 55)

total = 0
for cat, (count, chars) in sorted(categories.items(), key=lambda x: -x[1][1]):
    total += chars
    print(f"  {cat:<33} {count:>6} {chars:>10,} chars")

print("-" * 55)
print(f"  {'TOTAL':<33} {'':>6} {total:>10,} chars")
print()

if total > 500000:
    print("STATUS: HEAVY profile (>500K chars)")
    print("  Significant context consumed before you even start working.")
    print("  Consider removing unused skills and duplicate agents.")
elif total > 200000:
    print("STATUS: MODERATE profile (200-500K chars)")
    print("  Some room for optimization. Check the skills audit for")
    print("  unused or duplicate skills.")
elif total > 50000:
    print("STATUS: NORMAL profile (50-200K chars)")
    print("  Reasonable footprint. Only clean up if specific items")
    print("  are clearly unused.")
else:
    print("STATUS: LEAN profile (<50K chars)")
    print("  Minimal overhead. No cleanup needed.")
PYEOF
```

## Step 6 — Guided cleanup

Explain:
```
Based on the audits above, here are the cleanup actions available.
Each action is optional — I'll confirm before removing anything.

Cleanup priority (highest impact first):
  1. Broken symlinks — always safe, zero risk
  2. Orphaned plugin files — leftover from removed plugins
  3. Duplicate skills — same content in two places
  4. Ghost plugin registrations — registry entries with no files
  5. Unused large skills — skills you never invoke
  6. Duplicate agents — user-level copies of project agents
```

For each category that had findings, offer to clean up:

**Broken symlinks:**
```bash
# For each broken symlink found in Step 1:
# Confirm with user, then:
rm -rf ~/.claude/skills/BROKEN_SKILL_NAME
echo "Removed broken symlink: BROKEN_SKILL_NAME"
```

**Orphaned plugin directories:**
```bash
# For each orphaned plugin directory found in Step 3:
# Confirm with user, then:
rm -rf ~/.claude/plugins/ORPHAN_NAME
echo "Removed orphaned plugin directory: ORPHAN_NAME"
```

**Ghost plugin registrations:**
```bash
# For each ghost registration found in Step 3:
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/installed-plugins.json')
data = json.load(open(path))
data.pop('GHOST_NAME', None)
open(path, 'w').write(json.dumps(data, indent=2))
print('Removed ghost registration: GHOST_NAME')
"
```

**Duplicate skills:**
```bash
# For each duplicate pair, keep the one that is a symlink to a plugin
# (managed by the plugin system) and remove the standalone copy.
# Confirm with user, then:
rm -rf ~/.claude/skills/DUPLICATE_NAME
echo "Removed duplicate skill: DUPLICATE_NAME"
```

**Duplicate agents:**
```bash
# For each user-level agent that also exists at project level:
# Confirm with user, then:
rm ~/.claude/agents/DUPLICATE_AGENT.md
echo "Removed user-level duplicate: DUPLICATE_AGENT.md"
```

After each cleanup action, re-run the context impact calculation to show progress:
```
Context savings so far: X chars removed (Y% reduction)
```

After all approved cleanups, print:
```
Cleanup complete.
  Items removed: N
  Characters freed: N
  New profile size: N chars

Your Claude Code sessions will now start with more available
context for actual work.
```

## Verification

Run the full audit suite again as a final check:

```bash
python3 << 'PYEOF'
import os, glob

skills_dir = os.path.expanduser("~/.claude/skills")
agents_dir = os.path.expanduser("~/.claude/agents")

PASS = 0
TOTAL = 4

# 1. No broken symlinks
broken = 0
if os.path.isdir(skills_dir):
    for entry in os.listdir(skills_dir):
        full = os.path.join(skills_dir, entry)
        if os.path.islink(full) and not os.path.exists(full):
            broken += 1
if broken == 0:
    print("PASS: No broken symlinks in ~/.claude/skills/")
    PASS += 1
else:
    print(f"FAIL: {broken} broken symlinks remain")

# 2. No empty skill directories
empty = 0
if os.path.isdir(skills_dir):
    for entry in os.listdir(skills_dir):
        full = os.path.join(skills_dir, entry)
        if os.path.isdir(full) and not os.path.islink(full):
            has_skill = any(
                os.path.isfile(os.path.join(full, c))
                for c in ["SKILL.md", "skill.md"]
            )
            if not has_skill:
                empty += 1
if empty == 0:
    print("PASS: No empty skill directories")
    PASS += 1
else:
    print(f"FAIL: {empty} empty skill directories remain")

# 3. No orphaned plugin directories
import json
registry = {}
installed_path = os.path.expanduser("~/.claude/installed-plugins.json")
if os.path.isfile(installed_path):
    try:
        registry = json.load(open(installed_path))
    except:
        pass
plugins_dir = os.path.expanduser("~/.claude/plugins")
orphaned = 0
if os.path.isdir(plugins_dir):
    for entry in os.listdir(plugins_dir):
        if entry == "cache":
            continue
        if os.path.isdir(os.path.join(plugins_dir, entry)) and entry not in registry:
            orphaned += 1
if orphaned == 0:
    print("PASS: No orphaned plugin directories")
    PASS += 1
else:
    print(f"FAIL: {orphaned} orphaned plugin directories remain")

# 4. Context impact is reasonable
total_chars = 0
if os.path.isdir(skills_dir):
    for entry in os.listdir(skills_dir):
        full = os.path.join(skills_dir, entry)
        if os.path.islink(full) and not os.path.exists(full):
            continue
        for candidate in ["SKILL.md", "skill.md"]:
            path = os.path.join(full, candidate)
            if os.path.isfile(path):
                try:
                    total_chars += os.path.getsize(path)
                except:
                    pass
                break
if total_chars < 500000:
    print(f"PASS: Skills footprint is {total_chars:,} chars (under 500K)")
    PASS += 1
else:
    print(f"INFO: Skills footprint is {total_chars:,} chars (over 500K — consider removing unused skills)")
    PASS += 1  # Not a failure, just informational

print()
print(f"{PASS}/{TOTAL} checks passed.")
PYEOF
```

If all pass:
```
All cleanup checks passed. Your profile is clean.
```

## Challenge

```
Run the full audit on your own profile and report:

  1. How many total skill directories do you have?
  2. What is your total context footprint in characters?
  3. What is your largest skill by character count?
  4. Did you find any broken symlinks or orphaned plugins?
  5. What is your profile status (LEAN / NORMAL / MODERATE / HEAVY)?

If your profile is MODERATE or HEAVY, identify at least one
skill you could safely remove and explain why.
```

## Challenge Verification

The user should provide the five answers from the audit output. Verify by re-running the context impact report and comparing their answers.

Accept any reasonable answers — the specific numbers depend on their profile. The important thing is that they ran the audit and understand the impact.

If successful, print:
```
Module 15 complete.

You can now audit and clean your Claude Code profile.
Key concepts:
  - Every skill in ~/.claude/skills/ loads into every session
  - Broken symlinks and orphaned files are always safe to remove
  - User-level agents should only be used for truly global agents
  - Plugin removals can leave behind orphaned directories
  - The context impact report shows your total profile footprint

Run this module periodically to keep your profile lean.
Re-run anytime: /learn-15-profile-cleanup

Cleanup priority:
  1. Broken symlinks (zero risk)
  2. Orphaned plugin files
  3. Duplicate skills
  4. Ghost registrations
  5. Unused large skills
  6. Duplicate agents

A lean profile means more context for your actual work.
```
