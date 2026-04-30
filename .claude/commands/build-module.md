# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "03 — Memory MCP")
   If the user already specified it, skip this question.

2. Read `modules/TEMPLATE.md` for the exact structure to follow.

3. Read `.claude/commands/references/context.md` for team-specific values.

4. Ask: "Any specific source material I should read?" (e.g., a repo path, skill file, or MCP server docs)
   If the user provides a path, read it for content. If not, use your built-in knowledge of the tool.

5. Generate three files:

   **Module content** — `modules/NN-TOPIC.md`
   Follow TEMPLATE.md exactly. Fill in every placeholder. Every bash check must be
   a real, runnable command. Every step must have skip-if logic, user instructions
   (system-modifying via `!` prefix), and a verification command.

   **Dispatcher skill** — `.claude/commands/learn-NN-TOPIC.md`
   Use this exact pattern (swap title, description, time, prerequisites, filename):
   ```
   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read and follow the module at `modules/NN-TOPIC.md` step by step.

   Start with the Orientation section, then run the Preflight checks.
   Skip any step where the prerequisite already exists.
   Guide the user through each remaining step, then run Verification.
   Finish with the Challenge.

   Use `.claude/commands/references/context.md` for team-specific values.
   ```

   **Update catalog** — Edit `.claude/commands/courseware.md`
   Move the module from "Coming Soon" to the active section above it.
   Add the full entry with description and prerequisites.

6. Update `README.md` — Move the module from the "Coming Soon" table to the
   "Modules" table.

7. Commit each file separately with plain English commit messages (no prefixes, no emojis):
   - `git add modules/NN-TOPIC.md && git commit -m "add Module NN — TITLE"`
   - `git add .claude/commands/learn-NN-TOPIC.md && git commit -m "add /learn-NN-TOPIC dispatcher skill"`
   - `git add .claude/commands/courseware.md README.md && git commit -m "update catalog and README for Module NN"`

8. Report what was created and suggest `git push origin main` for the user to approve.
