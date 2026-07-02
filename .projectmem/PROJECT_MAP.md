# Project Map - Obsidian

## Project purpose

This repository is the shared Obsidian AI memory vault at `C:\Users\NINGMEI\Documents\Obsidian` on Windows. It mirrors the Mac mini vault at `/Users/xiaosong/Documents/Obsidian Vault` and stores human-readable project notes, agent configuration notes, templates, and the projectmem active-memory database used by coding agents. The vault helps Codex, OpenClaw, Claude, Cursor, OpenCode, and related tools share durable context without storing secrets in notes.

## Main folders

- `.obsidian/` - Obsidian app settings for the vault.
- `.integrations/` - local integration sources, including MCPVault used to expose the vault over MCP.
- `.projectmem/` - projectmem instructions, append-only events, generated summary, and this structural map.
- `.venv-projectmem/` - Python virtual environment for the projectmem CLI and MCP server.
- `01-Projects/` - project index and per-project memory notes.
- `Agent-Configs/` - setup notes for MCP configuration across agents.
- `Scripts/` - helper scripts, including `connect-project-memory.ps1` for adding projectmem to another project on Windows.
- `Templates/` - Obsidian templates for project records.

## Entry points

- `AGENTS.md` - repository-level instructions for AI agents, including Chinese responses and memory workflow.
- `Agent-Configs/MCP 配置总览.md` - canonical MCP configuration snippets for Codex, Claude, Cursor, OpenCode, and OpenClaw.
- `Scripts/connect-project-memory.ps1` - initializes projectmem in a target project and creates/updates the Obsidian project note on Windows.
- `Scripts/connect-project-memory.sh` - Mac/Git Bash version kept for cross-machine reference.
- `01-Projects/项目索引.md` - index of projects connected to the vault.

## Suggested first reads

1. `AGENTS.md`
2. `.projectmem/summary.md`
3. `.projectmem/PROJECT_MAP.md`
4. `Agent-Configs/MCP 配置总览.md`
5. `01-Projects/项目索引.md`
