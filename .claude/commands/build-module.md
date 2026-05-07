# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "03 — Memory MCP")
   If the user already specified it, skip this question.

2. Read `modules/TEMPLATE.md` for the exact structure to follow.

3. Read `.claude/commands/references/context.md` for team-specific values.

4. Ask: "Any specific source material I should read?" (e.g., a repo path, skill file, or MCP server docs)
   If the user provides a path, read it for content. If not, use your built-in knowledge of the tool.

4b. **Detect MCP module**: If the topic contains "MCP" or the user mentions
    an MCP server, ask: "This looks like an MCP module. What's the npm package name?"
    Then gather:
    - **npm package**: e.g., `@playwright/mcp`
    - **server name**: key in mcpServers (e.g., `playwright`)
    - **npx args**: args array (e.g., `["@playwright/mcp@latest", "--browser", "chrome"]`)
    - **tool prefix**: expected MCP tool prefix (e.g., `mcp__playwright__`)
    - **extra deps**: any server-specific dependencies (e.g., Chrome)

    When generating the module content in step 5, use the **MCP Module Variant**
    section from `modules/TEMPLATE.md` instead of the generic Preflight and Step 1.
    Fill in all `<PLACEHOLDER>` values with the gathered information.

    The generated module MUST include:
    - Phase 1 dependency checks (node, npm, npx, PATH consistency, extra deps)
    - Phase 2 global npm install + smoke test (Step 1a + 1b)
    - Phase 3 full-path config write using `shutil.which("npx")` (Step 1c)
    - Phase 4 post-restart verification with diagnostic ladder
    - The restart instruction with the verification contract wording:
      "On re-entry, we'll verify the server is live before continuing.
       If it isn't, we'll diagnose why — you won't be left stuck."

5. Generate four files:

   **Module content** — `modules/NN-TOPIC.md`
   Follow TEMPLATE.md exactly. Fill in every placeholder. Every bash check must be
   a real, runnable command. Every step must have skip-if logic, user instructions
   (system-modifying via `!` prefix), and a verification command.

   **Dispatcher command** — `.claude/commands/learn-NN-TOPIC.md`
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
   - `git add .claude/commands/learn-NN-TOPIC.md && git commit -m "add /learn-NN-TOPIC dispatcher"`
   - `git add .claude/commands/courseware.md README.md && git commit -m "update catalog and README for Module NN"`

8. Report what was created and suggest `git push origin main` for the user to approve.
