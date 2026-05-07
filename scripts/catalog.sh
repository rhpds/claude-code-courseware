#!/usr/bin/env bash
# Courseware catalog with ANSI colors

R='\033[0m'
B='\033[1m'
D='\033[2m'
H='\033[1;36m'
N='\033[1;33m'

printf "\n${B}Claude Code Courseware${R}\n\n"

printf "${H}  Setup & Foundation${R}\n"
printf "  ${N}01${R}  Vertex AI Setup                    ${D}10 min${R}\n"
printf "  ${N}02${R}  Writing CLAUDE.md                  ${D}15 min${R}\n\n"

printf "${H}  Core MCP Servers${R}\n"
printf "  ${N}03${R}  Memory MCP                         ${D}10 min${R}\n"
printf "  ${N}04${R}  Git MCP                            ${D}10 min${R}\n"
printf "  ${N}05${R}  Atlassian MCP (Jira)               ${D}5 min${R}\n"
printf "  ${N}06${R}  Playwright MCP                     ${D}10 min${R}\n"
printf "  ${N}07${R}  Notion MCP                         ${D}15 min${R}\n"
printf "  ${N}08${R}  Container & Podman MCP             ${D}15 min${R}\n\n"

printf "${H}  Skills & Customization${R}\n"
printf "  ${N}09${R}  Writing Custom Skills              ${D}15 min${R}\n"
printf "  ${N}10${R}  Hooks                              ${D}15 min${R}\n\n"

printf "${H}  Advanced Patterns${R}\n"
printf "  ${N}11${R}  Building MCP Servers               ${D}30 min${R}\n"
printf "  ${N}12${R}  Review Agents                      ${D}15 min${R}\n"
printf "  ${N}13${R}  Agent Teams vs Superpowers         ${D}15 min${R}\n\n"

printf "${H}  Workflow & Operations${R}\n"
printf "  ${N}14${R}  Debugging & Troubleshooting        ${D}15 min${R}\n"
printf "  ${N}15${R}  Cost & Context Management          ${D}15 min${R}\n"
printf "  ${N}16${R}  Multi-Repo Workspaces              ${D}15 min${R}\n"
printf "  ${N}17${R}  CI/CD Integration                  ${D}15 min${R}\n"
printf "  ${N}18${R}  Profile Cleanup                    ${D}15 min${R}\n\n"

printf "${H}  Team-Customizable${R}\n"
printf "  ${N}19${R}  Red Hat Quick Deck                 ${D}10 min${R}\n"
printf "  ${N}20${R}  Hivemind Knowledge Base            ${D}15 min${R}\n\n"

printf "${D}  Coming Soon${R}\n"
printf "  ${D}21  Workshop Intake                    15 min${R}\n\n"

printf "${D}──────────────────────────────────────────────${R}\n"
printf "  Type a module ${B}number${R} to start\n"
printf "  or a ${B}section name${R} for full descriptions.\n"
printf "  Tab completion: ${B}/learn-${R} then Tab.\n\n"
