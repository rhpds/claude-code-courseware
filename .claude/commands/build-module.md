# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "22 -- Workshop Intake")
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
    - The restart instruction with the verification contract wording

5. Generate the module file at `modules/NN-TOPIC.md`.
   Follow TEMPLATE.md exactly. Fill in every placeholder.

6. **Validate the module** before generating other files:

   ```bash
   python3 scripts/validate.py
   ```

   If the module is missing required sections, fix it before proceeding.

7. **Auto-generate the dispatcher** at `.claude/commands/learn-NN-TOPIC.md`:

   ```
   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read modules/NN-TOPIC.md but present it in phases:

   Phase 1: Read only the Quick Setup and Orientation sections. Present them.
            Ask: "Ready to check prerequisites?"

   Phase 2: Read only the Preflight section. Run the checks.
            Skip any step that passes. Report results.
            Ask: "Ready to start the walkthrough?"

   Phase 3: Read and present one Step at a time.
            After each step's verification passes, proceed to the next.
            Do not read ahead -- load each step only when needed.

   Phase 4: Read only the Verification section. Run all checks.
            Report results.

   Phase 5: Read only the Challenge and Challenge Verification sections.
            Present the challenge. After the user completes it, verify.

   Use .claude/commands/references/context.md for team-specific values.
   Track progress in ~/.claude/courseware-progress/.
   ```

8. **Add to catalog** -- Ask the user: "Which section should this go in?"
   Show the section list from `courseware.md`. Insert the module entry
   in the correct section. Update the module count in the Footer.

9. **Add to README** -- Insert a row in the correct section table in `README.md`.

10. **Run full validation:**

    ```bash
    python3 scripts/validate.py
    ```

    All 6 checks must pass before proceeding.

11. Commit all generated files:

    ```bash
    git add modules/NN-TOPIC.md .claude/commands/learn-NN-TOPIC.md .claude/commands/courseware.md README.md
    git commit -m "add Module NN -- TITLE"
    ```

12. Report what was created and suggest `git push origin main` for the user to approve.
