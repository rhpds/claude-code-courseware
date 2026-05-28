#!/usr/bin/env python3
"""Convert all dispatcher files to lazy-load phased format."""

import re
from pathlib import Path

# Template for the new phased format
PHASED_TEMPLATE = """
Read modules/{module_file} but present it in phases:

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
"""


def convert_dispatcher(file_path: Path) -> bool:
    """Convert a single dispatcher file to phased format."""
    content = file_path.read_text()
    lines = content.splitlines()

    # Extract header (lines 1-4: title, blank, description, time/prereqs)
    if len(lines) < 4:
        print(f"SKIP {file_path.name}: too short")
        return False

    title = lines[0]  # line 1: # Title
    description = lines[2]  # line 3: description
    time_prereqs = lines[3]  # line 4: Estimated time...

    # Extract module filename from old format
    module_match = re.search(r'modules/(\d+-[^`]+\.md)', content)
    if not module_match:
        print(f"SKIP {file_path.name}: no module reference found")
        return False

    module_file = module_match.group(1)

    # Build new content
    new_content = f"{title}\n\n{description}\n{time_prereqs}\n"
    new_content += PHASED_TEMPLATE.format(module_file=module_file)

    # Write back
    file_path.write_text(new_content)
    print(f"CONVERTED {file_path.name} -> {module_file}")
    return True


def main():
    """Convert all dispatcher files."""
    commands_dir = Path(".claude/commands")
    dispatcher_files = sorted(commands_dir.glob("learn-*.md"))

    print(f"Found {len(dispatcher_files)} dispatcher files\n")

    converted = 0
    for file_path in dispatcher_files:
        if convert_dispatcher(file_path):
            converted += 1

    print(f"\nConverted {converted}/{len(dispatcher_files)} files")

    # Verify Phase 1 appears in all files
    print("\nVerifying Phase 1 in all files:")
    for file_path in dispatcher_files:
        content = file_path.read_text()
        if "Phase 1:" in content:
            print(f"  ✓ {file_path.name}")
        else:
            print(f"  ✗ {file_path.name} MISSING Phase 1")


if __name__ == "__main__":
    main()
