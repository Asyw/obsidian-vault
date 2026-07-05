---
type: project
status: active
project_path: "/Users/xiaosong/Documents/Obsidian"
memory: "/Users/xiaosong/Documents/Obsidian/.projectmem"
tags:
  - project
  - ai-memory
  - obsidian
---

# Obsidian AI 记忆库

## 项目路径

`/Users/xiaosong/Documents/Obsidian`

## 记忆入口

- Obsidian MCP: `obsidian`
- 主动记忆 MCP: `projectmem`
- projectmem 数据: `.projectmem/`
- MCP 配置说明: [[Agent-Configs/MCP 配置总览]]

## 当前选择

- 使用 MCPVault 作为 Obsidian vault 的通用 MCP 读写层。
- 使用 projectmem 作为主动记忆和跨项目经验层。
- Codex 已写入全局 MCP 配置；其他 agent 可参考配置说明接入同一套工具。

## 工作记录

- 已安装 MCPVault 与 projectmem，并完成本地 MCP smoke test。
- 已将同一套 `obsidian` 与 `projectmem` MCP server 接入 OpenClaw，并通过 `openclaw mcp probe` 验证。
