# Module 05 — Red Hat Quick Deck

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Install the Red Hat Quick Deck skill so Claude Code can generate branded HTML slide presentations on any topic. When complete, you can ask Claude to create a "quick deck" and get a self-contained HTML file with Red Hat branding, story-arc narrative structure, and keyboard navigation.

## Orientation

Print this once at the start:

```
You're installing the Red Hat Quick Deck skill.
This takes about 10 minutes.

The Quick Deck skill lets Claude Code generate branded HTML slide
presentations from a topic or outline. Each deck is a single HTML file
with Red Hat fonts, colors, logo, and design tokens — no dependencies
beyond a browser.

We'll set up:
  1. Clone the red-hat-quick-deck repository
  2. Install the skill into Claude Code
  3. Tour the skill capabilities
  4. Verify the installation

After this module, you'll restart Claude Code and create your first
presentation as the challenge.
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Git installed?
command -v git &>/dev/null && echo "EXISTS: Git" || echo "MISSING: Git"

# red-hat-quick-deck repo cloned?
if [ -d "$HOME/repos/red-hat-quick-deck" ]; then
  echo "EXISTS: red-hat-quick-deck repo at ~/repos/red-hat-quick-deck"
elif [ -d "$HOME/red-hat-quick-deck" ]; then
  echo "EXISTS: red-hat-quick-deck repo at ~/red-hat-quick-deck"
else
  echo "MISSING: red-hat-quick-deck repo not found"
fi

# Skill installed in Claude Code?
if [ -L "$HOME/.claude/skills/red-hat-quick-deck" ] || [ -d "$HOME/.claude/skills/red-hat-quick-deck" ]; then
  if [ -f "$HOME/.claude/skills/red-hat-quick-deck/SKILL.md" ]; then
    echo "EXISTS: Quick Deck skill installed in ~/.claude/skills/red-hat-quick-deck"
  else
    echo "MISSING: Skill directory exists but SKILL.md not found"
  fi
else
  echo "MISSING: Quick Deck skill not in ~/.claude/skills/"
fi

# Reference files present?
if [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/redhat-brand.md" ] && \
   [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/story-arcs.md" ] && \
   [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/rhds-icons.md" ]; then
  echo "EXISTS: All reference files present (brand, story arcs, icons)"
else
  echo "MISSING: Reference files not found alongside skill"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where items already exist.

## Step 1 — Clone the red-hat-quick-deck repository

Skip if the repo is already cloned (EXISTS in preflight).

Explain:
```
The Quick Deck skill lives in its own Git repository. It contains the
skill definition (SKILL.md), Red Hat brand reference files, story arc
patterns, and an icon inventory. We'll clone it to your repos directory.
```

Tell the user:
```
Clone the repository:

  ! mkdir -p ~/repos && git clone https://github.com/rhpds/red-hat-quick-deck.git ~/repos/red-hat-quick-deck
```

If the user doesn't have access to the GitHub repo, try the alternate:
```
If the repo is private or you don't have access, ask a teammate who
has it cloned to share the folder, or check with the repo owner for access.
```

Verify:
```bash
[ -f "$HOME/repos/red-hat-quick-deck/SKILL.md" ] && echo "PASS: Repository cloned with SKILL.md" || echo "FAIL: SKILL.md not found in repo"
```

## Step 2 — Install the skill into Claude Code

Skip if the skill is already installed (EXISTS in preflight).

Explain:
```
Claude Code discovers skills from ~/.claude/skills/. Each skill is a
directory containing a SKILL.md file. The Quick Deck repo also has
reference files (brand colors, story arcs, icon inventory) that the
skill reads at generation time, so we'll symlink the entire repo
directory rather than copying just the SKILL.md.
```

Determine the repo path (it may be in `~/repos/` or `~/`):
```bash
if [ -d "$HOME/repos/red-hat-quick-deck" ]; then
  DECK_REPO="$HOME/repos/red-hat-quick-deck"
elif [ -d "$HOME/red-hat-quick-deck" ]; then
  DECK_REPO="$HOME/red-hat-quick-deck"
else
  echo "ERROR: Cannot find red-hat-quick-deck repo. Run Step 1 first."
  exit 1
fi
echo "Found repo at: $DECK_REPO"
```

Create the symlink:
```bash
mkdir -p ~/.claude/skills
ln -sfn "$DECK_REPO" ~/.claude/skills/red-hat-quick-deck
echo "Symlink created: ~/.claude/skills/red-hat-quick-deck -> $DECK_REPO"
```

Verify:
```bash
if [ -f "$HOME/.claude/skills/red-hat-quick-deck/SKILL.md" ]; then
  echo "PASS: SKILL.md accessible via skill path"
else
  echo "FAIL: SKILL.md not found at ~/.claude/skills/red-hat-quick-deck/SKILL.md"
fi

if [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/redhat-brand.md" ]; then
  echo "PASS: Reference files accessible"
else
  echo "FAIL: Reference files not found"
fi
```

## Step 3 — Tour the skill capabilities

No installation needed for this step — it's an overview of what the skill does.

Explain:
```
Before you use the skill, here's what it produces and how it works.

What you get:
  A single .html file and a .md companion. The HTML is completely
  self-contained — inline CSS, inline JS, fonts and design tokens
  loaded from CDN. Open it in any browser, email it, or host it
  anywhere.

How to invoke it:
  After restarting Claude Code, ask for a presentation:
    "Create a quick deck about Kubernetes operators"
    "Make a presentation on our workshop intake process"
    "Build a brief deck for my team meeting"

What Claude does:
  1. Asks your preferred visual mode (Dark, Light, or Expressive Dark)
  2. Chooses a story arc (Problem/Resolution, Myth-Busting, or Journey)
  3. Writes slide headlines first (the headlines tell the full story)
  4. Generates the complete HTML deck with Red Hat branding

Key features of every deck:
  Navigation    Arrow keys, spacebar, or click to advance
  Notes panel   Press N to see references and context per slide
  Slide types   Title, Content, Big Number, Comparison, Architecture,
                Quote, Call-to-Action, Thank You
  PDF export    Cmd+P / Ctrl+P to save as PDF (dark decks auto-switch
                to light palette for print)
  Media         Videos (YouTube, direct URL) and images can be added
                after initial generation
  Mobile        Responsive and touch-enabled for async viewing

Color modes:
  Core Dark       Black backgrounds, cinematic feel (default)
  Core Light      White backgrounds, clean for print/email
  Expressive Dark Purple/teal accents alongside Red Hat red
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=4

# 1. Repo exists
[ -d "$HOME/repos/red-hat-quick-deck" ] || [ -d "$HOME/red-hat-quick-deck" ] && { echo "PASS: Repository cloned"; PASS=$((PASS+1)); } || echo "FAIL: Repository not found"

# 2. Skill installed
[ -f "$HOME/.claude/skills/red-hat-quick-deck/SKILL.md" ] && { echo "PASS: Skill installed"; PASS=$((PASS+1)); } || echo "FAIL: Skill not installed"

# 3. References accessible
if [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/redhat-brand.md" ] && \
   [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/story-arcs.md" ] && \
   [ -f "$HOME/.claude/skills/red-hat-quick-deck/references/rhds-icons.md" ]; then
  echo "PASS: All reference files accessible"
  PASS=$((PASS+1))
else
  echo "FAIL: Reference files missing"
fi

# 4. Symlink correct
if [ -L "$HOME/.claude/skills/red-hat-quick-deck" ]; then
  TARGET=$(readlink "$HOME/.claude/skills/red-hat-quick-deck")
  echo "PASS: Skill symlinked to $TARGET"
  PASS=$((PASS+1))
elif [ -d "$HOME/.claude/skills/red-hat-quick-deck" ]; then
  echo "PASS: Skill directory exists (not a symlink)"
  PASS=$((PASS+1))
else
  echo "FAIL: Skill path does not exist"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. The Red Hat Quick Deck skill is installed.

IMPORTANT: Claude Code needs to be restarted to discover the new skill.

  1. Exit this Claude Code session (Ctrl+C or type /exit)
  2. Relaunch Claude Code: claude .
  3. Try the challenge below by asking Claude to create a quick deck
```

If any fail, tell the user which step to re-run.

## Challenge

```
Create a Red Hat-branded presentation on a topic relevant to your work.

Pick one of these, or choose your own:
  - A brief update for your team meeting (3-5 slides)
  - An overview of a project you maintain
  - A walkthrough of a process your team follows

Ask Claude:
  "Create a quick deck about [your topic]"

After Claude generates the deck:
  1. Open the .html file in your browser
  2. Navigate with arrow keys
  3. Press N to see the contextual notes
  4. Try Cmd+P / Ctrl+P to preview the PDF export

Tell me:
  - What topic you chose
  - How many slides the deck has
  - Whether the N key shows contextual notes
```

## Challenge Verification

The user should report:
1. A topic (any topic is valid)
2. A slide count (typically 6-10 slides for a brief deck)
3. Confirmation that N toggles the notes panel

To verify, ask the user to confirm they can see the deck in their browser. The file should be a `.html` file they can open directly.

If successful, print:
```
Module 05 complete.

You can now create Red Hat-branded presentations with Claude Code.
Key things to remember:
  - Ask for a "quick deck" on any topic
  - Choose Dark (cinematic) or Light (print-friendly) mode
  - Press N during presentation for references and notes
  - Cmd+P / Ctrl+P exports to PDF
  - After initial generation, ask to add videos or memes
  - The .md companion file mirrors the deck as plain text

The skill follows Red Hat brand standards automatically:
  Red Hat Display for headlines, Red Hat Text for body,
  official logo, design tokens for spacing and typography.

Next module: /learn-06-writing-claude-md (coming soon)
```
