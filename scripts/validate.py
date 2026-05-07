#!/usr/bin/env python3
"""Courseware integrity validator.

Checks:
  1. Dispatcher coverage -- every module has a dispatcher
  2. No orphan dispatchers -- every dispatcher has a module
  3. Module structure -- required sections present
  4. Catalog count -- courseware.md count matches file count
  5. README sync -- every module in README table
  6. No stale skills/ -- skills/ directory must not exist

Exit 0 on all-pass, 1 on any failure.
"""

import glob
import os
import re
import sys


def get_module_files():
    files = glob.glob("modules/[0-9]*.md")
    return [f for f in files if "TEMPLATE" not in f]


def extract_module_info(path):
    basename = os.path.basename(path)
    match = re.match(r"^(\d+)-(.+)\.md$", basename)
    if match:
        return match.group(1), match.group(2)
    return None, None


def check_dispatcher_coverage(modules):
    errors = []
    for mod in modules:
        num, topic = extract_module_info(mod)
        if num is None:
            errors.append(f"  Cannot parse module filename: {mod}")
            continue
        dispatcher = f".claude/commands/learn-{num}-{topic}.md"
        if not os.path.exists(dispatcher):
            errors.append(f"  MISSING dispatcher: {dispatcher} (for {mod})")
    return errors


def check_orphan_dispatchers(modules):
    errors = []
    module_keys = set()
    for mod in modules:
        num, topic = extract_module_info(mod)
        if num and topic:
            module_keys.add(f"{num}-{topic}")

    dispatchers = glob.glob(".claude/commands/learn-[0-9]*.md")
    for disp in dispatchers:
        basename = os.path.basename(disp)
        match = re.match(r"^learn-(\d+)-(.+)\.md$", basename)
        if match:
            key = f"{match.group(1)}-{match.group(2)}"
            if key not in module_keys:
                errors.append(f"  ORPHAN dispatcher: {disp} (no matching module)")
    return errors


def check_module_structure(modules):
    errors = []
    required_sections = [
        (r"##\s+(Orientation|Quick Setup)", "Orientation or Quick Setup"),
        (r"##\s+Preflight", "Preflight"),
        (r"##\s+Step\s+\d", "at least one Step"),
        (r"##\s+Verification", "Verification"),
        (r"##\s+Challenge", "Challenge"),
    ]
    for mod in modules:
        with open(mod, "r") as f:
            content = f.read()
        missing = []
        for pattern, label in required_sections:
            if not re.search(pattern, content):
                missing.append(label)
        if missing:
            errors.append(f"  {mod}: missing sections: {', '.join(missing)}")
    return errors


def check_catalog_count(modules):
    errors = []
    catalog_path = ".claude/commands/courseware.md"
    if not os.path.exists(catalog_path):
        errors.append(f"  Catalog not found: {catalog_path}")
        return errors

    with open(catalog_path, "r") as f:
        content = f.read()

    static_match = re.search(r"\*\*(\d+)\s+modules?\s+available", content)
    dynamic_match = re.search(r"\[COUNT\]\s+modules?\s+available", content)

    if static_match:
        catalog_count = int(static_match.group(1))
        actual_count = len(modules)
        if catalog_count != actual_count:
            errors.append(
                f"  Catalog says {catalog_count} modules, but found {actual_count} module files"
            )
    elif dynamic_match:
        pass
    else:
        errors.append("  No module count found in catalog (expected '**N modules available' or dynamic [COUNT])")
    return errors


def check_readme_sync(modules):
    errors = []
    if not os.path.exists("README.md"):
        errors.append("  README.md not found")
        return errors

    with open("README.md", "r") as f:
        readme = f.read()

    for mod in modules:
        num, topic = extract_module_info(mod)
        if num is None:
            continue
        num_stripped = num.lstrip("0") or "0"
        if f"| {num_stripped} " not in readme and f"| {num} " not in readme:
            errors.append(f"  Module {num} ({topic}) not found in README table")
    return errors


def check_no_stale_skills():
    errors = []
    if os.path.isdir("skills"):
        count = len(glob.glob("skills/*/SKILL.md"))
        errors.append(f"  skills/ directory still exists ({count} SKILL.md files)")
    return errors


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    modules = get_module_files()
    if not modules:
        print("FAIL: No module files found in modules/")
        sys.exit(1)

    checks = [
        ("Dispatcher coverage", check_dispatcher_coverage(modules)),
        ("No orphan dispatchers", check_orphan_dispatchers(modules)),
        ("Module structure", check_module_structure(modules)),
        ("Catalog count", check_catalog_count(modules)),
        ("README sync", check_readme_sync(modules)),
        ("No stale skills/", check_no_stale_skills()),
    ]

    failed = False
    for name, errors in checks:
        if errors:
            print(f"FAIL: {name}")
            for e in errors:
                print(e)
            failed = True
        else:
            print(f"PASS: {name}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
