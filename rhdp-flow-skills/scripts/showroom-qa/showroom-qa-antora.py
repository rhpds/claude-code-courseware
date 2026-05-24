#!/usr/bin/env python3
"""Playwright QA script for Antora-based RHDP showrooms.

Performs four-phase verification: page load, content, module walkthrough,
and service tab checks. Outputs a JSON report to stdout.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

VIEWPORT = {"width": 1280, "height": 800}
NAV_TIMEOUT = 30_000
IFRAME_TIMEOUT = 15_000
ALL_PHASES = ["page_load", "content", "modules", "tabs"]


def parse_args():
    p = argparse.ArgumentParser(description="QA check for Antora-based RHDP showrooms")
    p.add_argument("--url", required=True, help="Showroom URL")
    p.add_argument("--user", required=True, help="Login username")
    p.add_argument("--pass", dest="password", required=True, help="Login password")
    p.add_argument("--output-dir", default="./showroom-qa-results",
                   help="Screenshot output directory")
    p.add_argument("--checks", default=",".join(ALL_PHASES),
                   help="Comma-separated phases: page_load,content,modules,tabs")
    return p.parse_args()


def screenshot(page, output_dir, name):
    path = os.path.join(output_dir, name)
    page.screenshot(path=path)
    return name


def make_check(name, status, **extra):
    entry = {"name": name, "status": status}
    entry.update(extra)
    return entry


def get_content_frame(page):
    """Find the Antora content frame via page.frames.

    The content iframe src is './www/modules/index.html' (relative to
    the showroom origin). We match on '/www/modules/' in the URL.
    """
    for frame in page.frames:
        if "/www/modules/" in frame.url:
            return frame
    return None


def get_service_frames(page):
    """Return all frames that are NOT the main page or content frame.

    These are the cross-origin service iframes (AAP, Kira, etc.).
    """
    services = []
    for frame in page.frames:
        if frame == page.main_frame:
            continue
        if "/www/modules/" in frame.url:
            continue
        services.append(frame)
    return services


def open_sidebar(content_frame):
    """Click the hamburger menu button to reveal the sidebar navigation."""
    for selector in ["button.nav-toggle", "button[aria-label*='nav']",
                     "nav button"]:
        try:
            btn = content_frame.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False


def collect_module_links(content_frame):
    """Extract module links from the Antora sidebar or footer navigation."""
    modules = []

    open_sidebar(content_frame)

    for selector in [".nav-list a", ".nav-menu a", "nav.nav a",
                     ".navigation a"]:
        try:
            links = content_frame.locator(selector).all()
            for link in links:
                text = (link.text_content() or "").strip()
                href = link.get_attribute("href")
                if text and href and len(text) > 3 and not href.startswith("#"):
                    modules.append({"text": text, "href": href})
            if modules:
                return modules
        except Exception:
            continue

    # Fallback: scan article and footer for module links
    try:
        links = content_frame.locator("article a, nav a").all()
        seen = set()
        for link in links:
            text = (link.text_content() or "").strip()
            href = link.get_attribute("href")
            if (text and href and len(text) > 3
                    and href.endswith(".html")
                    and not href.startswith("#")
                    and href not in seen
                    and "module" in text.lower()):
                modules.append({"text": text, "href": href})
                seen.add(href)
    except Exception:
        pass

    return modules


def phase_page_load(page, url, output_dir):
    checks = []
    try:
        response = page.goto(url, wait_until="domcontentloaded",
                             timeout=NAV_TIMEOUT)
        status_code = response.status if response else 0

        if status_code == 200:
            page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
            title = page.title() or ""
            ss = screenshot(page, output_dir, "01-landing.png")
            checks.append(make_check("page_load", "pass",
                                     title=title, screenshot=ss))
        else:
            checks.append(make_check("page_load", "fail",
                                     error=f"HTTP {status_code}"))
    except PlaywrightTimeout:
        checks.append(make_check("page_load", "fail",
                                 error="Page load timed out"))
    except Exception as e:
        checks.append(make_check("page_load", "fail", error=str(e)))
    return checks


def phase_content(page, output_dir):
    checks = []
    cf = get_content_frame(page)

    if not cf:
        checks.append(make_check("content_iframe", "fail",
                                 error="Content iframe not found"))
        return checks

    checks.append(make_check("content_iframe", "pass"))

    try:
        cf.wait_for_load_state("domcontentloaded", timeout=IFRAME_TIMEOUT)
    except PlaywrightTimeout:
        checks.append(make_check("content_load", "fail",
                                 error="Content iframe timed out"))
        return checks

    # Module list
    modules = collect_module_links(cf)
    if modules:
        checks.append(make_check("module_list", "pass",
                                 module_count=len(modules),
                                 modules=[m["text"] for m in modules]))
    else:
        checks.append(make_check("module_list", "fail",
                                 error="No module links found in navigation"))

    # Credentials box -- Antora renders "Important" admonition as a table
    creds_found = False
    try:
        body_text = cf.locator("article").first.text_content(timeout=5000) or ""
        if ("username" in body_text.lower() or "user-" in body_text.lower()) \
                and "password" in body_text.lower():
            creds_found = True
    except Exception:
        pass

    if creds_found:
        checks.append(make_check("credentials_box", "pass"))
    else:
        checks.append(make_check("credentials_box", "fail",
                                 error="No credentials found on landing page"))

    ss = screenshot(page, output_dir, "02-content.png")
    checks[-1]["screenshot"] = ss
    return checks


def phase_modules(page, output_dir):
    checks = []
    cf = get_content_frame(page)
    if not cf:
        checks.append(make_check("modules_skip", "fail",
                                 error="Content iframe not found"))
        return checks

    modules = collect_module_links(cf)
    if not modules:
        checks.append(make_check("modules_skip", "fail",
                                 error="No module links to walk through"))
        return checks

    for i, mod in enumerate(modules):
        check_name = f"module_{i + 1}_content"
        try:
            href = mod["href"]
            if not href.startswith("http"):
                base = cf.url.rsplit("/", 1)[0] + "/"
                href = base + href

            cf.goto(href, wait_until="domcontentloaded",
                    timeout=IFRAME_TIMEOUT)
            cf.wait_for_load_state("networkidle", timeout=IFRAME_TIMEOUT)

            h1 = None
            try:
                h1_el = cf.locator("h1").first
                if h1_el.is_visible(timeout=3000):
                    h1 = h1_el.text_content().strip()
            except Exception:
                pass

            body_text = ""
            try:
                article = cf.locator("article").first
                if article.is_visible(timeout=2000):
                    body_text = article.text_content().strip()
            except Exception:
                pass

            ss_name = f"{i + 3:02d}-module-{i + 1}.png"
            ss = screenshot(page, output_dir, ss_name)

            if h1 and len(body_text) > 50:
                checks.append(make_check(check_name, "pass",
                                         title=h1, screenshot=ss))
            elif not h1:
                checks.append(make_check(check_name, "fail",
                                         error="No H1 heading found",
                                         screenshot=ss))
            else:
                checks.append(make_check(check_name, "fail",
                                         error="Article body empty or too short",
                                         screenshot=ss))

        except PlaywrightTimeout:
            checks.append(make_check(check_name, "fail",
                                     error=f"Timed out: {mod['text']}"))
        except Exception as e:
            checks.append(make_check(check_name, "fail", error=str(e)))

    return checks


def phase_tabs(page, output_dir):
    checks = []

    try:
        tab_elements = page.locator("[role='tab']").all()
    except Exception:
        tab_elements = []

    if not tab_elements:
        checks.append(make_check("tabs_discovery", "fail",
                                 error="No service tabs found"))
        return checks

    service_frames = get_service_frames(page)

    for i, tab_el in enumerate(tab_elements):
        label = (tab_el.text_content() or "").strip()
        if not label:
            continue

        safe_label = (label.lower()
                      .replace(" ", "_")
                      .replace("/", "_")
                      .replace(".", "_"))
        check_name = f"tab_{safe_label}_load"

        try:
            tab_el.click(timeout=5000)
            time.sleep(2)

            iframe_loaded = False

            # Check the corresponding service frame (tab index maps to
            # service frame index since content iframe is excluded)
            if i < len(service_frames):
                try:
                    sf = service_frames[i]
                    sf.wait_for_load_state("domcontentloaded", timeout=5000)
                    body_text = sf.locator("body").first.text_content(
                        timeout=3000) or ""
                    if len(body_text.strip()) > 5:
                        iframe_loaded = True
                except Exception:
                    pass

            ss_name = f"{20 + i:02d}-tab-{safe_label}.png"
            ss = screenshot(page, output_dir, ss_name)

            if iframe_loaded:
                checks.append(make_check(check_name, "pass",
                                         label=label, screenshot=ss))
            else:
                checks.append(make_check(check_name, "fail",
                                         label=label, screenshot=ss,
                                         error="Tab iframe blank or not loaded"))

        except PlaywrightTimeout:
            checks.append(make_check(check_name, "fail", label=label,
                                     error="Timed out clicking tab"))
        except Exception as e:
            checks.append(make_check(check_name, "fail", label=label,
                                     error=str(e)))

    return checks


def main():
    args = parse_args()
    output_dir = args.output_dir
    phases = [p.strip() for p in args.checks.split(",")]

    for phase in phases:
        if phase not in ALL_PHASES:
            print(f"Unknown check phase: {phase}", file=sys.stderr)
            print(f"Valid phases: {', '.join(ALL_PHASES)}", file=sys.stderr)
            sys.exit(2)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    all_checks = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            ignore_https_errors=True,
        )
        page = context.new_page()

        if "page_load" in phases:
            all_checks.extend(phase_page_load(page, args.url, output_dir))
            if any(c["status"] == "fail" and c["name"] == "page_load"
                   for c in all_checks):
                browser.close()
                print(json.dumps(build_report(args.url, all_checks)))
                sys.exit(1)

        if "content" in phases:
            all_checks.extend(phase_content(page, output_dir))

        if "modules" in phases:
            all_checks.extend(phase_modules(page, output_dir))

        if "tabs" in phases:
            all_checks.extend(phase_tabs(page, output_dir))

        browser.close()

    report = build_report(args.url, all_checks)
    print(json.dumps(report))
    sys.exit(1 if report["summary"]["failed"] > 0 else 0)


def build_report(url, checks):
    total = len(checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "url": url,
        "variant": "antora",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {"total": total, "passed": passed,
                     "failed": total - passed},
    }


if __name__ == "__main__":
    main()
