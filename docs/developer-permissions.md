# Developer / Maintainer Permissions

These permission rules are used by courseware maintainers but are NOT needed by end users running modules. To use them, merge into your `.claude/settings.local.json`:

## GitHub CLI

```json
"Bash(gh api *)",
"Bash(gh pr *)"
```

## Confluence (post-update protocol)

```json
"mcp__plugin_atlassian_atlassian__search",
"mcp__plugin_atlassian_atlassian__getConfluencePage",
"mcp__plugin_atlassian_atlassian__updateConfluencePage"
```

## Notion (build log)

```json
"mcp__claude_ai_Notion__notion-fetch",
"mcp__claude_ai_Notion__notion-create-pages",
"mcp__claude_ai_Notion__notion-update-data-source"
```

## Process Management

```json
"Bash(lsof *)",
"Bash(xargs kill *)"
```

## Symlink Management

```json
"Bash(ln -sf *)"
```
