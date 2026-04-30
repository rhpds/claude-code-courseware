# Module 08 — Hivemind Knowledge Base

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working), GitHub access to rhpds org

Contribute to and search the team's shared Hive Mind knowledge base. When complete, you'll know how to write articles, query for existing knowledge, and keep the team in sync.

## Orientation

Print this once at the start:

```
You're learning to use the Hive Mind knowledge base.
This takes about 15 minutes.

The Hive Mind is the RHDP team's shared knowledge base, stored as
Obsidian-compatible markdown files in a GitHub repository. Team members
contribute articles about what they've built, fixed, learned, or
decided — so the whole team benefits from individual discoveries.

We'll cover:
  1. How the Hive Mind is structured
  2. Setting up the local clone and preferences
  3. Writing an article with hivemind-write
  4. Searching with hivemind-query
  5. Tags and cross-references

Two skills power the Hive Mind:
  hivemind-write  — contribute articles from any project
  hivemind-query  — search across all team knowledge
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Git installed?
command -v git &>/dev/null && echo "EXISTS: Git $(git --version | cut -d' ' -f3)" || echo "MISSING: Git"

# GitHub CLI (used for contributor identification)
command -v gh &>/dev/null && echo "EXISTS: GitHub CLI $(gh --version | head -1 | awk '{print $3}')" || echo "INFO: GitHub CLI not installed (optional, will use git config fallback)"

# Check for hivemind-write skill
if [ -f "$HOME/.claude/skills/hivemind-write/SKILL.md" ]; then
  echo "EXISTS: hivemind-write skill installed"
else
  echo "MISSING: hivemind-write skill — will install"
fi

# Check for hivemind-query skill
if [ -f "$HOME/.claude/skills/hivemind-query/SKILL.md" ]; then
  echo "EXISTS: hivemind-query skill installed"
else
  echo "MISSING: hivemind-query skill — will install"
fi

# Check for preferences file
if [ -f "$HOME/.config/hivemind/hivemind-preferences.md" ]; then
  echo "EXISTS: Hive Mind preferences"
  grep "clone_path" "$HOME/.config/hivemind/hivemind-preferences.md" 2>/dev/null
else
  echo "MISSING: Hive Mind preferences (~/.config/hivemind/hivemind-preferences.md)"
fi

# Check for existing hivemind clone
for path in "$HOME/.hivemind" "$HOME/repos/hivemind"; do
  if [ -d "$path/.git" ]; then
    echo "EXISTS: Hive Mind clone at $path"
    break
  fi
done

# Check for hivemind repo (source of skills)
if [ -d "$HOME/repos/hivemind/.claude/skills" ]; then
  echo "EXISTS: hivemind repo at ~/repos/hivemind (skill source)"
else
  echo "INFO: hivemind repo not found at ~/repos/hivemind"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where things already exist.

## Step 1 — Understand the Hive Mind structure

Explain:
```
The Hive Mind is a Git repository with Obsidian-compatible markdown files.
Here's how it's organized:
```

Show the structure:
```
  github.com/rhpds/hivemind
  └── vault/
      ├── templates/
      │   └── article.md           # template for new articles
      ├── team_docs/               # canonical team documentation
      │   ├── maas-documentation.md
      │   └── ...
      └── people/
          ├── alice/               # each contributor has a folder
          │   ├── ocp-module-fix.md
          │   └── antora-build-issue.md
          ├── bob/
          │   └── jurassic-tool-overview.md
          └── ...

Key principles:
  - Every article is a standalone markdown file
  - Articles use YAML frontmatter for metadata (author, date, tags, type)
  - Cross-references use Obsidian [[wikilinks]]
  - Tags use #hashtag format in the frontmatter
  - team_docs/ is canonical (authoritative reference)
  - people/ is per-contributor (individual discoveries and fixes)
```

Show an example article format:
```
Here's what a Hive Mind article looks like:

  ---
  author: Alice
  date: 2025-04-15
  project: agnosticd
  type: fix
  tags: [ocp, idp, certificates]
  ---

  # IdP Certificate Rotation Fix

  Fixed the recurring IdP certificate expiration issue in OCP clusters
  provisioned through AgnosticD.

  ## Details

  The root cause was...

  ## Links

  - [[maas-documentation]] — related MaaS docs
  - https://github.com/rhpds/agnosticd/pull/1234

Article types: feature, fix, tool, decision, issue, knowledge
```

## Step 2 — Set up the Hive Mind locally

Skip if the hivemind-write skill is already installed and preferences exist.

Explain:
```
The Hive Mind skills need two things:
  1. The hivemind repo cloned locally
  2. A preferences file telling the skills where to find it
```

### Install the skills (if not already installed)

Check if the hivemind repo exists as a source for skills:

```bash
if [ -d "$HOME/repos/hivemind/.claude/skills" ]; then
  echo "Hivemind repo found — will symlink skills from it"
  ls "$HOME/repos/hivemind/.claude/skills/"
else
  echo "Hivemind repo not found — will clone it first"
fi
```

If the hivemind repo is not cloned:

Tell the user:
```
First, let's clone the hivemind repo. This is the source of both the
knowledge base and the skills that interact with it.

  ! git clone https://github.com/rhpds/hivemind ~/repos/hivemind
```

Then install the skills by symlinking:

```bash
mkdir -p "$HOME/.claude/skills"

# Symlink hivemind-write
if [ ! -L "$HOME/.claude/skills/hivemind-write" ] && [ -d "$HOME/repos/hivemind/.claude/skills/hivemind-write" ]; then
  ln -s "$HOME/repos/hivemind/.claude/skills/hivemind-write" "$HOME/.claude/skills/hivemind-write"
  echo "INSTALLED: hivemind-write (symlinked from repo)"
fi

# Symlink hivemind-query
if [ ! -L "$HOME/.claude/skills/hivemind-query" ] && [ -d "$HOME/repos/hivemind/.claude/skills/hivemind-query" ]; then
  ln -s "$HOME/repos/hivemind/.claude/skills/hivemind-query" "$HOME/.claude/skills/hivemind-query"
  echo "INSTALLED: hivemind-query (symlinked from repo)"
fi
```

### Set up preferences

```bash
if [ ! -f "$HOME/.config/hivemind/hivemind-preferences.md" ]; then
  mkdir -p "$HOME/.config/hivemind"
fi
```

Ask the user:
```
Where would you like to keep the Hive Mind clone?

The default is ~/.hivemind, but if you already have it cloned
somewhere (like ~/repos/hivemind), we can use that path.

Options:
  A) Use the repo we just cloned: ~/repos/hivemind
  B) Use the default: ~/.hivemind (will clone a separate copy)
  C) Specify a custom path
```

Write the preferences file based on their answer:

```bash
# Determine contributor name
contributor=$(gh api user --jq .login 2>/dev/null || git config user.name | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

cat > "$HOME/.config/hivemind/hivemind-preferences.md" << EOF
---
clone_path: <chosen-path>
default_folder: vault/people/$contributor
---
EOF

echo "Preferences saved to ~/.config/hivemind/hivemind-preferences.md"
```

Verify:
```bash
echo "=== Preferences ==="
cat "$HOME/.config/hivemind/hivemind-preferences.md"

echo ""
echo "=== Skill Installation ==="
[ -f "$HOME/.claude/skills/hivemind-write/SKILL.md" ] && echo "PASS: hivemind-write installed" || echo "FAIL: hivemind-write missing"
[ -f "$HOME/.claude/skills/hivemind-query/SKILL.md" ] && echo "PASS: hivemind-query installed" || echo "FAIL: hivemind-query missing"

echo ""
echo "=== Clone ==="
clone_path=$(python3 -c "
import re
with open('$HOME/.config/hivemind/hivemind-preferences.md') as f:
    m = re.search(r'clone_path:\s*(.+)', f.read())
    if m: print(m.group(1).strip())
" 2>/dev/null)
[ -d "$clone_path/.git" ] && echo "PASS: Hive Mind clone at $clone_path" || echo "FAIL: No git repo at $clone_path"
```

Tell the user:
```
IMPORTANT: If you just installed the hivemind skills, you need to
restart Claude Code for them to become available.

1. Exit this session (Ctrl+C or /exit)
2. Relaunch: claude .
3. Re-run: /learn-08-hivemind-knowledge-base

The preflight will skip the setup steps on re-entry.
```

## Step 3 — Explore existing articles

Explain:
```
Before writing, let's see what's already in the Hive Mind.
This is exactly what hivemind-query does — but we'll do it manually
first so you understand the underlying structure.
```

Pull the latest content:

```bash
clone_path=$(python3 -c "
import re
with open('$HOME/.config/hivemind/hivemind-preferences.md') as f:
    m = re.search(r'clone_path:\s*(.+)', f.read())
    if m: print(m.group(1).strip())
" 2>/dev/null)

cd "$clone_path" && git pull --rebase 2>/dev/null
echo ""

# Count articles
total=$(find vault/people -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "Total articles: $total"

# Count contributors
contributors=$(ls vault/people/ 2>/dev/null | wc -l | tr -d ' ')
echo "Contributors: $contributors"

# List contributors
echo ""
echo "Contributors:"
ls vault/people/ 2>/dev/null | while read name; do
  count=$(find "vault/people/$name" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "  $name ($count articles)"
done

# Show recent articles
echo ""
echo "Recent articles (last 5 commits):"
git log --oneline -5 --no-merges 2>/dev/null
```

Show the tags in use:
```bash
cd "$clone_path"
echo "Tags in use:"
grep -rh "^tags:" vault/people/ vault/team_docs/ 2>/dev/null | \
  python3 -c "
import sys, re
tags = {}
for line in sys.stdin:
    for tag in re.findall(r'#?(\w[\w-]*)', line.replace('tags:', '')):
        tags[tag] = tags.get(tag, 0) + 1
for tag, count in sorted(tags.items(), key=lambda x: -x[1])[:15]:
    print(f'  #{tag} ({count})')
" 2>/dev/null || echo "  (no tags found)"
```

Explain:
```
Tags are how the Hive Mind connects related articles across contributors.
When you write an article, reuse existing tags whenever possible.
Only create new tags when nothing existing fits.
```

## Step 4 — Write a practice article

Explain:
```
Now let's write an article. In real use, you'd invoke the hivemind-write
skill (just say "write to hivemind" or "share with the team"), and it
gathers context from your current session automatically.

For this practice, we'll write an article about completing this
courseware module.
```

Guide the user through the article structure:

```
We'll write an article about your courseware progress. Here's what
we need:

  Frontmatter:
    author:   <your name from git config>
    date:     <today's date>
    project:  claude-code-courseware
    type:     knowledge
    tags:     [claude-code, courseware, training]

  Title: Completed Claude Code Courseware Modules

  Body:
    - What modules you've completed
    - Key things you learned
    - Any tips for other team members
```

Ask the user:
```
What have you found most useful so far in the courseware?
I'll include your answer in the article.

(This is how hivemind-write works — it asks what you want to share,
then generates the article.)
```

After getting their input, generate the article and show it:

```
Here's your draft article:

  ---
  author: <name>
  date: <today>
  project: claude-code-courseware
  type: knowledge
  tags: [claude-code, courseware, training]
  ---

  # Completed Claude Code Courseware Modules

  <summary based on their input>

  ## Details

  Completed modules: <list based on what they've done>

  ## Tips for the Team

  <tips based on their input>

  ## Links

  - https://github.com/rhpds/claude-code-courseware

File: vault/people/<contributor>/<filename>.md

Does this look right? I can adjust before saving.
```

After approval, explain (but don't push):
```
In a real workflow, hivemind-write would save, commit, and push this
article to the Hive Mind repository. For this practice exercise,
we'll skip the push — but the process is:

  1. Save the file to vault/people/<you>/<filename>.md
  2. git add && git commit
  3. git push origin main

The hivemind-write skill handles all of this automatically.
```

## Step 5 — Search the Hive Mind

Explain:
```
The hivemind-query skill searches across all articles, tags, git history,
and even external sources (GitHub repos, Confluence) to answer questions
about team knowledge.

Let's try some searches to see what the team has documented.
```

Demonstrate searching by doing a few queries against the local clone:

```bash
clone_path=$(python3 -c "
import re
with open('$HOME/.config/hivemind/hivemind-preferences.md') as f:
    m = re.search(r'clone_path:\s*(.+)', f.read())
    if m: print(m.group(1).strip())
" 2>/dev/null)

cd "$clone_path"

# Search by keyword
echo "=== Search: 'ocp' ==="
grep -rl "ocp" vault/ 2>/dev/null | head -5

echo ""

# Search by tag
echo "=== Tag search: articles tagged with common tags ==="
grep -rl "tags:.*claude" vault/ 2>/dev/null | head -5

echo ""

# Search by contributor
echo "=== Recent contributions ==="
git log --format="%an: %s" --no-merges -10 2>/dev/null
```

Explain:
```
In practice, you don't run these commands yourself. Just ask Claude:

  "Has anyone documented the IdP cert fix?"
  "What has the team been working on this week?"
  "Search the hive mind for Babylon core"

The hivemind-query skill handles the search strategy, reads matching
articles, follows wikilinks to related content, and synthesizes
an answer.

Search signal priority:
  1. Canonical team_docs (authoritative reference)
  2. Article content (full-text search)
  3. Tags (topic discovery)
  4. Git history (time-based queries)
  5. Wikilinks (related content traversal)
  6. External sources (GitHub, Confluence)
```

## Verification

Run all checks and report:

```bash
# 1. hivemind-write skill installed
[ -f "$HOME/.claude/skills/hivemind-write/SKILL.md" ] && echo "PASS: hivemind-write skill installed" || echo "FAIL: hivemind-write not found"

# 2. hivemind-query skill installed
[ -f "$HOME/.claude/skills/hivemind-query/SKILL.md" ] && echo "PASS: hivemind-query skill installed" || echo "FAIL: hivemind-query not found"

# 3. Preferences file exists
[ -f "$HOME/.config/hivemind/hivemind-preferences.md" ] && echo "PASS: preferences configured" || echo "FAIL: preferences not found"

# 4. Clone exists and has content
clone_path=$(python3 -c "
import re
with open('$HOME/.config/hivemind/hivemind-preferences.md') as f:
    m = re.search(r'clone_path:\s*(.+)', f.read())
    if m: print(m.group(1).strip())
" 2>/dev/null)

if [ -d "$clone_path/.git" ]; then
  count=$(find "$clone_path/vault" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "PASS: Hive Mind clone exists ($count articles)"
else
  echo "FAIL: No git repo at $clone_path"
fi

# 5. Skills are symlinked (not copied)
if [ -L "$HOME/.claude/skills/hivemind-write" ]; then
  echo "PASS: hivemind-write is a symlink (stays in sync with repo)"
else
  echo "INFO: hivemind-write is a direct copy (won't auto-update)"
fi
```

Print:
```
All Hive Mind checks passed.
```

If any fail:
```
Troubleshooting:

  Skills not installed:
    Clone the hivemind repo and symlink the skills:
      git clone https://github.com/rhpds/hivemind ~/repos/hivemind
      ln -s ~/repos/hivemind/.claude/skills/hivemind-write ~/.claude/skills/hivemind-write
      ln -s ~/repos/hivemind/.claude/skills/hivemind-query ~/.claude/skills/hivemind-query

  Preferences not found:
    Create ~/.config/hivemind/hivemind-preferences.md with:
      ---
      clone_path: ~/repos/hivemind
      default_folder: vault/people/<your-github-username>
      ---

  Clone not working:
    Make sure you have access to https://github.com/rhpds/hivemind
    Try: gh repo view rhpds/hivemind
```

## Challenge

```
Use the Hive Mind to answer these questions:

1. How many total articles are in the Hive Mind?
   (Count all .md files in vault/people/ and vault/team_docs/)

2. Which contributor has written the most articles?

3. What are the 5 most commonly used tags?

4. Find one article about a fix or issue and summarize what
   problem it solved (read the full article).

Tell me:
  - Total article count
  - Top contributor and their article count
  - Top 5 tags
  - A one-sentence summary of the fix/issue article you found
```

## Challenge Verification

The user should report:
1. A total article count
2. The top contributor with their count
3. Top 5 tags
4. A summary of an article they read

To verify, run the same queries against the clone:
```bash
clone_path=$(python3 -c "
import re
with open('$HOME/.config/hivemind/hivemind-preferences.md') as f:
    m = re.search(r'clone_path:\s*(.+)', f.read())
    if m: print(m.group(1).strip())
" 2>/dev/null)

cd "$clone_path"

# Total articles
total=$(find vault/people vault/team_docs -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "Total articles: $total"

# Top contributor
echo ""
echo "Articles per contributor:"
ls vault/people/ 2>/dev/null | while read name; do
  count=$(find "vault/people/$name" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "  $name: $count"
done | sort -t: -k2 -rn

# Top tags
echo ""
echo "Top tags:"
grep -rh "^tags:" vault/ 2>/dev/null | python3 -c "
import sys, re
tags = {}
for line in sys.stdin:
    for tag in re.findall(r'#?(\w[\w-]*)', line.replace('tags:', '')):
        tags[tag] = tags.get(tag, 0) + 1
for tag, count in sorted(tags.items(), key=lambda x: -x[1])[:5]:
    print(f'  #{tag} ({count})')
" 2>/dev/null
```

If the answers are reasonable, print:
```
Module 08 complete.

You can now contribute to and search the Hive Mind knowledge base.
Key skills:
  hivemind-write  — "share with the team", "write to hivemind"
  hivemind-query  — "search hivemind", "has anyone documented..."

Article format:
  - YAML frontmatter: author, date, project, type, tags
  - Obsidian-compatible: [[wikilinks]], #tags
  - Stored in vault/people/<your-name>/

Best practices:
  - Reuse existing tags whenever possible
  - Include [[wikilinks]] to related articles
  - Write articles when you fix something non-obvious
  - Search before writing — someone may have documented it already

Next module: /learn-09-workshop-ops (coming soon)
```
