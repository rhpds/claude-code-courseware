---
name: 28-voice-vim-terminal-customization
description: "Customize your Claude Code terminal experience with voice dictation, vim keybindings, custom themes, and keyboard shortcuts."
---

# - Voice, Vim & Terminal Customization
<!-- NEW -->

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Customize your Claude Code terminal experience with voice dictation, vim keybindings, custom themes, and keyboard shortcuts.

## Orientation

Print this once at the start:

```
You're setting up terminal customization for Claude Code.
This takes about 10 minutes.

Claude Code is more than a prompt box. You can:
  - Dictate prompts with your voice instead of typing
  - Use vim keybindings in the prompt input area
  - Remap any keyboard shortcut via a JSON config
  - Create custom color themes
  - Run in a fullscreen TUI with mouse support
  - Define custom output styles for how Claude responds

We'll set up:
  1. Voice dictation (push-to-talk)
  2. Vim mode for prompt editing
  3. Keyboard shortcut customization
  4. Custom themes
  5. Fullscreen TUI mode
  6. Output styles and the status line

You'll need: Claude Code installed and working (Module 01).
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/28.started
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Operating system check (voice requires macOS, Linux, or Windows -- not remote/SSH)
OS_NAME=$(uname -s 2>/dev/null)
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ] || [ -n "$SSH_CONNECTION" ]; then
  echo "INFO: Remote/SSH session detected -- voice dictation will not be available"
elif [ "$OS_NAME" = "Darwin" ] || [ "$OS_NAME" = "Linux" ]; then
  echo "EXISTS: Local $OS_NAME environment (voice dictation supported)"
else
  echo "INFO: OS is $OS_NAME -- voice dictation support varies"
fi

# Existing keybindings.json?
[ -f "$HOME/.claude/keybindings.json" ] && echo "EXISTS: ~/.claude/keybindings.json (custom keybindings already configured)" || echo "MISSING: ~/.claude/keybindings.json (default keybindings in use)"

# Existing themes directory?
if [ -d "$HOME/.claude/themes" ]; then
  count=$(ls "$HOME/.claude/themes"/*.json 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: ~/.claude/themes/ ($count theme files)"
else
  echo "MISSING: ~/.claude/themes/ (no custom themes)"
fi

# Existing output styles directory?
if [ -d "$HOME/.claude/output-styles" ]; then
  count=$(ls "$HOME/.claude/output-styles"/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: ~/.claude/output-styles/ ($count output style files)"
else
  echo "MISSING: ~/.claude/output-styles/ (no custom output styles)"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found.

## Step 1 -- Voice dictation

Explain:
```
Voice dictation lets you speak your prompts instead of typing them.
The /voice command enables push-to-talk in your Claude Code session.

How it works:
  - Run /voice to enable voice mode
  - Hold the spacebar to record your voice
  - Release the spacebar to stop recording and transcribe
  - The transcribed text appears in your prompt input
  - You can also use tap mode: tap spacebar to start, tap again to stop

Auto-submit option:
  When enabled, the transcribed text is submitted as a prompt
  immediately after transcription -- no manual Enter needed.

Technical details:
  - Transcription happens on Anthropic's servers (not local)
  - Audio is sent securely and not stored after transcription
  - Voice dictation does NOT consume tokens from your usage
  - Requires a microphone and a local terminal (not SSH/remote)

Platform support:
  - macOS: supported
  - Linux: supported
  - Windows: supported
  - Remote/SSH sessions: NOT supported (no microphone access)
```

Tell the user:
```
To try voice dictation, run:

  /voice

Then hold the spacebar and speak a prompt. Release to transcribe.

If you are in a remote/SSH session, skip this step -- voice
requires local microphone access.
```

There is no automated verification for this step. Ask the user if voice worked or if they skipped it.

## Step 2 -- Vim mode

Explain:
```
Vim mode brings vim keybindings to the Claude Code prompt input area.
The /vim command toggles it on and off within your session.

What vim mode covers:
  - Mode switching: Normal mode and Insert mode
  - Navigation: h/j/k/l (character/line), w/b/e (word), 0/$ (line start/end)
  - Search within input: f/F (find char forward/backward), t/T (till char)
  - Editing operators: d (delete), c (change), y (yank/copy), p (paste)
  - Text objects: iw (inner word), aw (a word), i" (inner quotes), a( (a paren group)

Important distinction:
  Vim mode controls TEXT INPUT in the prompt area.
  Keybindings (Step 3) control APPLICATION ACTIONS like submit, cancel, scroll.
  They operate on different layers and do not conflict.

Behavior notes:
  - Escape enters Normal mode (it does NOT cancel the chat)
  - /vim toggles vim mode off again if you want to return to normal editing
  - Vim mode persists within the current session
  - It resets when you start a new session (not persisted across sessions)
```

Tell the user:
```
To enable vim mode, run:

  /vim

Try typing a prompt, then press Escape to enter Normal mode.
Use h/j/k/l to navigate, i to re-enter Insert mode.

To turn it off: run /vim again.
```

There is no automated verification for this step. Ask the user if they tried vim mode.

## Step 3 -- Keybinding customization

Explain:
```
Every keyboard shortcut in Claude Code can be customized via:

  ~/.claude/keybindings.json

This file defines shortcuts organized by context. Claude Code has
17 application contexts (prompt input, chat view, dialog, etc.),
and each context has its own set of bindable actions.

Features:
  - Modifier combinations: Ctrl, Alt/Option, Shift, Meta/Cmd
  - Chord sequences: press one key combo, then another
    (e.g., Ctrl+X followed by Ctrl+K)
  - Unbinding: set a shortcut to null to disable it
  - Changes apply instantly -- no restart needed
```

Tell the user:
```
Let's create a keybindings.json with a simple customization.

This example shows the structure. We will add one binding that
maps Ctrl+K to the "submit" action in the prompt context:
```

If `~/.claude/keybindings.json` is MISSING, create it:

```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/keybindings.json")
if os.path.isfile(path):
    print("EXISTS: keybindings.json already exists, skipping creation")
else:
    keybindings = [
        {
            "key": "ctrl+k",
            "command": "chat:submit",
            "when": "inputFocused"
        }
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(keybindings, f, indent=2)
    print("CREATED: ~/.claude/keybindings.json with Ctrl+K submit binding")
    print()
    print("You can edit this file to add more bindings.")
    print("Each entry needs: key, command, and when (context).")
    print()
    print("To see all available commands and contexts, run:")
    print("  /keybindings-help")
PYEOF
```

Verify:

```bash
[ -f "$HOME/.claude/keybindings.json" ] && echo "PASS: keybindings.json exists" || echo "FAIL: keybindings.json not found"
```

After verification, explain:
```
Common keybinding customizations:
  - Change the submit key (default: Enter or Ctrl+Enter depending on mode)
  - Add chord shortcuts for frequent actions
  - Unbind keys that conflict with your terminal emulator
  - Add shortcuts for toggling features

For full keybinding documentation, run:
  /keybindings-help
```

## Step 4 -- Custom themes

Explain:
```
Claude Code supports custom color themes that change the appearance
of the terminal UI. Themes are stored as JSON files in:

  ~/.claude/themes/

The /theme command lets you switch between available themes.
You can also create your own theme files by hand.
```

Tell the user:
```
Let's create the themes directory and a simple custom theme.
```

If `~/.claude/themes/` is MISSING, create a sample theme:

```bash
python3 << 'PYEOF'
import json, os

themes_dir = os.path.expanduser("~/.claude/themes")
theme_path = os.path.join(themes_dir, "courseware-demo.json")

if os.path.isdir(themes_dir):
    count = len([f for f in os.listdir(themes_dir) if f.endswith(".json")])
    print(f"EXISTS: ~/.claude/themes/ already exists with {count} theme(s)")
    print("You can switch themes with: /theme")
else:
    os.makedirs(themes_dir, exist_ok=True)
    # Create a minimal custom theme
    theme = {
        "name": "Courseware Demo",
        "colors": {
            "primary": "#4A9FD9",
            "secondary": "#6B7280",
            "accent": "#10B981",
            "background": "default",
            "text": "default"
        }
    }
    with open(theme_path, "w") as f:
        json.dump(theme, f, indent=2)
    print("CREATED: ~/.claude/themes/courseware-demo.json")
    print()
    print("To switch themes, run: /theme")
    print("To edit themes, modify the JSON files in ~/.claude/themes/")
PYEOF
```

Verify:

```bash
[ -d "$HOME/.claude/themes" ] && echo "PASS: themes directory exists" || echo "FAIL: themes directory not found"
```

## Step 5 -- Fullscreen TUI mode

Explain:
```
Claude Code can run in a fullscreen terminal UI (TUI) mode that
uses the alternate screen buffer for flicker-free rendering.

Fullscreen TUI features:
  - Flicker-free rendering via alternate screen buffer
  - Mouse support: click to position cursor, drag to select and copy
  - Ctrl+O opens transcript mode with search functionality
  - Flat memory usage even during very long sessions
  - Cleaner visual experience with no scroll-back clutter

How to enable:
  - Run /tui fullscreen within a session
  - Or set the environment variable: CLAUDE_CODE_NO_FLICKER=1
    to start every session in fullscreen mode

The environment variable approach is useful if you always want
fullscreen mode. Add it to your shell profile:

  export CLAUDE_CODE_NO_FLICKER=1
```

Tell the user:
```
To try fullscreen TUI mode in your current session:

  /tui fullscreen

To make it permanent, add to your ~/.zshrc or ~/.bashrc:

  export CLAUDE_CODE_NO_FLICKER=1

This is purely a display preference -- it does not change
Claude Code's behavior, just how the terminal renders.
```

There is no automated verification for this step. Ask the user if they want to try it.

## Step 6 -- Output styles and status line

Explain:
```
Output styles control how Claude formats its responses. They are
markdown files that set instructions for tone, structure, and detail.

Output style locations:
  - User-level: ~/.claude/output-styles/
  - Project-level: .claude/output-styles/ in any repo

Built-in styles:
  - Default: standard Claude Code responses
  - Explanatory: more detailed explanations with reasoning
  - Learning: step-by-step teaching style

Custom output styles use YAML frontmatter to configure behavior:
  ---
  name: My Custom Style
  keep-coding-instructions: true
  ---
  Your custom instructions here. These shape how Claude
  responds -- tone, verbosity, format, etc.

The keep-coding-instructions flag:
  - true: Claude's normal coding behavior is preserved,
    your style is added on top
  - false: your style fully replaces the default instructions

Status line:
  The bottom bar in Claude Code shows real-time information:
  - Token cost for the current session
  - Active model name
  - Session duration
  - Other contextual info

  The status line is always visible and updates automatically.
  No configuration needed -- it works out of the box.
```

Tell the user:
```
Let's create a sample output style to see how it works.
```

If `~/.claude/output-styles/` is MISSING, create a sample:

```bash
python3 << 'PYEOF'
import os

styles_dir = os.path.expanduser("~/.claude/output-styles")
style_path = os.path.join(styles_dir, "concise.md")

if os.path.isdir(styles_dir):
    count = len([f for f in os.listdir(styles_dir) if f.endswith(".md")])
    print(f"EXISTS: ~/.claude/output-styles/ already exists with {count} style(s)")
else:
    os.makedirs(styles_dir, exist_ok=True)
    content = """---
name: Concise
keep-coding-instructions: true
---
Respond concisely. Use short sentences. Skip preamble.
When showing code, include only the relevant lines -- not full files.
Use bullet points instead of paragraphs when listing information.
"""
    with open(style_path, "w") as f:
        f.write(content)
    print("CREATED: ~/.claude/output-styles/concise.md")
    print()
    print("To switch output styles, run: /output-style")
    print("To edit styles, modify the .md files in ~/.claude/output-styles/")
PYEOF
```

Verify:

```bash
[ -d "$HOME/.claude/output-styles" ] && echo "PASS: output-styles directory exists" || echo "FAIL: output-styles directory not found"
```

## Verification

Run all checks as PASS/FAIL:

```bash
PASS=0
TOTAL=4

# 1. Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not found"

# 2. Keybindings config exists
[ -f "$HOME/.claude/keybindings.json" ] && { echo "PASS: keybindings.json exists"; PASS=$((PASS+1)); } || echo "FAIL: keybindings.json not found"

# 3. Themes directory exists
[ -d "$HOME/.claude/themes" ] && { echo "PASS: themes directory exists"; PASS=$((PASS+1)); } || echo "FAIL: themes directory not found"

# 4. Output styles directory exists
[ -d "$HOME/.claude/output-styles" ] && { echo "PASS: output-styles directory exists"; PASS=$((PASS+1)); } || echo "FAIL: output-styles directory not found"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. Your Claude Code terminal is customized with
keybindings, themes, and output styles ready to use.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Try out the customization features and report:

  1. Enable vim mode (/vim) and navigate a prompt using hjkl.
     Did it work? Could you switch between Normal and Insert mode?

  2. Customize at least one keybinding in ~/.claude/keybindings.json.
     What binding did you add or change?

  3. If on macOS or a local Linux/Windows terminal: try voice
     dictation (/voice) and speak one prompt.
     Did the transcription work? If you are remote, note that.

Tell me:
  - Which features you tried
  - What keybinding you customized
  - Whether voice dictation worked (or if you are remote/skipped it)
```

## Challenge Verification

The user should report on three items:

1. Vim mode: any confirmation that they toggled /vim and used navigation keys is sufficient.
2. Keybinding: verify by reading `~/.claude/keybindings.json`:

```bash
if [ -f "$HOME/.claude/keybindings.json" ]; then
  python3 -c "
import json
data = json.load(open('$HOME/.claude/keybindings.json'))
if isinstance(data, list):
    print(f'Found {len(data)} keybinding(s):')
    for b in data:
        key = b.get('key', 'unknown')
        cmd = b.get('command', 'unknown')
        print(f'  {key} -> {cmd}')
else:
    print('Keybindings file exists but has unexpected format.')
"
else
  echo "No keybindings.json found."
fi
```

3. Voice: accept any answer. If they are remote, "skipped -- remote session" is valid. If they tried it and it worked, great.

Accept any reasonable answers. The goal is that they explored the customization features and understand what is available.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/28.done
```

If successful, print:
```
Module 28 complete.

You've completed the courseware! All 28 modules covered.

Key customization features:
  - /voice: dictate prompts instead of typing (local terminals only)
  - /vim: vim keybindings in the prompt input area
  - ~/.claude/keybindings.json: remap any keyboard shortcut
  - ~/.claude/themes/: custom color themes, switch with /theme
  - /tui fullscreen: flicker-free fullscreen mode with mouse support
  - ~/.claude/output-styles/: control how Claude formats responses

These settings let you tailor Claude Code to your workflow.
Experiment with combinations -- vim mode plus voice dictation
is particularly effective for hands-free coding sessions.

Re-run anytime: /learn-28-voice-vim-terminal-customization

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
