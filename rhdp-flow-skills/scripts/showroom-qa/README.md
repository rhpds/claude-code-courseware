# Showroom QA Scripts

Standalone Playwright scripts that perform end-to-end QA checks on RHDP workshop showrooms. Each script targets a specific showroom variant.

## Available Scripts

| Script | Variant | Description |
|--------|---------|-------------|
| `showroom-qa-antora.py` | Antora | Split-panel showroom with Antora docs + service tabs |

## Requirements

- Python 3.10+
- Playwright (`pip install playwright && playwright install chromium`)

No Claude Code, Webwright, or API keys required to run these scripts.

## Usage

```bash
python showroom-qa-antora.py \
  --url "https://showroom-user-...-showroom.apps.cluster-....dyn.redhatworkshops.io/" \
  --user "user-xxxxx" \
  --pass "password" \
  --output-dir ./results
```

### Arguments

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--url` | Yes | -- | Showroom URL |
| `--user` | Yes | -- | Login username |
| `--pass` | Yes | -- | Login password |
| `--output-dir` | No | `./showroom-qa-results` | Screenshot output directory |
| `--checks` | No | all | Comma-separated: `page_load,content,modules,tabs` |

### Output

JSON report to stdout:

```json
{
  "url": "https://showroom-...",
  "variant": "antora",
  "timestamp": "2026-05-24T12:00:00Z",
  "checks": [
    {"name": "page_load", "status": "pass", "screenshot": "01-landing.png"},
    {"name": "module_list", "status": "pass", "module_count": 7}
  ],
  "summary": {"total": 15, "passed": 14, "failed": 1}
}
```

Exit code: 0 = all pass, 1 = any failure.

Screenshots saved to `--output-dir` with numbered filenames.

## Adding New Variants

Use Webwright's `/webwright:craft` command to generate a script for a new showroom type. See the design spec at `docs/superpowers/specs/2026-05-24-webwright-showroom-qa-design.md` for the variant detection approach.
