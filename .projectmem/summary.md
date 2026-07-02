# projectmem - Obsidian

_Last updated: 2026-07-02_

## Project purpose
This repository is the shared Obsidian AI memory vault at `C:\Users\NINGMEI\Documents\Obsidian` on Windows. It mirrors the Mac mini vault at `/Users/xiaosong/Documents/Obsidian Vault` and stores human-readable project notes, agent configuration notes, templates, and the projectmem active-memory database used by coding agents. The vault helps Codex, OpenClaw, Claude, Cursor, OpenCode, and related tools share durable context without storing secrets in notes.

## Recent issues
- No issues logged yet.

## Decisions
- Use /Users/xiaosong/Documents/Obsidian as the shared AI memory vault for agents, with Obsidian notes for human-readable project records and projectmem for append-only active development memory. [/Users/xiaosong/Documents/Obsidian]
- Configure supported agents through MCP servers named obsidian and projectmem so Codex, Claude, OpenCode, Cursor, and OpenClaw can share the same vault and memory workflow. [/Users/xiaosong/Documents/Obsidian/Agent-Configs/MCP 配置总览.md]

## Notes
- Connected OpenClaw to the shared Obsidian AI memory vault through MCP servers obsidian and projectmem; OpenClaw probe reports obsidian=15 tools and projectmem=14 tools/resources/prompts.
- gotcha: The conversation cwd /Users/xiaosong/Documents/openclow 2 is currently a 0-byte file, not a directory; use /Users/xiaosong/Documents/Obsidian for the vault and ~/.openclaw for OpenClaw config. [/Users/xiaosong/Documents/openclow 2]
- Installed Obsidian desktop app 1.12.7 to /Applications and opened the shared vault path /Users/xiaosong/Documents/Obsidian.
- Project map initialized for the Obsidian AI memory vault, including purpose, main folders, entry points, and suggested first reads. [/Users/xiaosong/Documents/Obsidian/.projectmem/PROJECT_MAP.md]
- Created visible Obsidian project folders for OpenClaw and Codex under 01-Projects, and initialized projectmem in both real project paths.
- Synchronized the AI memory vault content into the Obsidian app's active vault at /Users/xiaosong/Documents/Obsidian Vault, updated Codex/OpenClaw MCP targets to that visible vault, and kept tool runtimes under /Users/xiaosong/Documents/Obsidian.
- Mirrored the Mac mini Obsidian Vault into the Windows vault at C:\Users\NINGMEI\Documents\Obsidian, copied MCPVault/projectmem integration sources, installed a Windows .venv-projectmem, and added Windows MCP configuration snippets plus Scripts/connect-project-memory.ps1.

## Key files
- `/.openclaw`
- `1.12.7`
- `Scripts/connect-project-memory.ps1`

## Open questions
- None logged yet.
