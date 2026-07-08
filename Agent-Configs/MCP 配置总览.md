# MCP 配置总览

这些配置让不同 agent 共用同一个 Obsidian 知识库和主动记忆系统。

## Codex

已写入：

`/Users/xiaosong/.codex/config.toml`

生效方式：完全退出 Codex 后重新打开。

```toml
[mcp_servers.obsidian]
command = "/Users/xiaosong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
args = ["/Users/xiaosong/Documents/Obsidian/.integrations/github/mcpvault/dist/server.js", "/Users/xiaosong/Documents/Obsidian"]
startup_timeout_sec = 120

[mcp_servers.projectmem]
command = "/Users/xiaosong/Documents/Obsidian/.venv-projectmem/bin/python"
args = ["-m", "projectmem.mcp_server", "--root", "/Users/xiaosong/Documents/Obsidian"]
cwd = "/Users/xiaosong/Documents/Obsidian"
startup_timeout_sec = 120
```

## Claude Desktop

配置文件：

`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/Users/xiaosong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
      "args": [
        "/Users/xiaosong/Documents/Obsidian/.integrations/github/mcpvault/dist/server.js",
        "/Users/xiaosong/Documents/Obsidian"
      ]
    },
    "projectmem": {
      "command": "/Users/xiaosong/Documents/Obsidian/.venv-projectmem/bin/python",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "/Users/xiaosong/Documents/Obsidian"
      ]
    }
  }
}
```

## Claude Code

用户级配置可写入：

`~/.claude.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/Users/xiaosong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
      "args": [
        "/Users/xiaosong/Documents/Obsidian/.integrations/github/mcpvault/dist/server.js",
        "/Users/xiaosong/Documents/Obsidian"
      ],
      "env": {}
    },
    "projectmem": {
      "command": "/Users/xiaosong/Documents/Obsidian/.venv-projectmem/bin/python",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "/Users/xiaosong/Documents/Obsidian"
      ],
      "env": {}
    }
  }
}
```

## Cursor

项目级配置可写入项目根目录：

`.cursor/mcp.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/Users/xiaosong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
      "args": [
        "/Users/xiaosong/Documents/Obsidian/.integrations/github/mcpvault/dist/server.js",
        "/Users/xiaosong/Documents/Obsidian"
      ]
    },
    "projectmem": {
      "command": "/Users/xiaosong/Documents/Obsidian/.venv-projectmem/bin/python",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "/Users/xiaosong/Documents/Obsidian"
      ]
    }
  }
}
```

## OpenCode

配置文件：

`~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "obsidian": {
      "type": "local",
      "command": [
        "/Users/xiaosong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
        "/Users/xiaosong/Documents/Obsidian/.integrations/github/mcpvault/dist/server.js",
        "/Users/xiaosong/Documents/Obsidian"
      ],
      "enabled": true
    },
    "projectmem": {
      "type": "local",
      "command": [
        "/Users/xiaosong/Documents/Obsidian/.venv-projectmem/bin/python",
        "-m",
        "projectmem.mcp_server",
        "--root",
        "/Users/xiaosong/Documents/Obsidian"
      ],
      "enabled": true
    }
  }
}
```

## OpenClaw

已写入：

`/Users/xiaosong/.openclaw/openclaw.json`

可用命令：

```bash
openclaw mcp list
openclaw mcp probe obsidian
openclaw mcp probe projectmem
```

当前状态：

- `obsidian`: 已接入，MCPVault 暴露 15 个 Obsidian vault 工具。
- `projectmem`: 已接入，暴露 14 个主动记忆工具/资源/提示。

## 使用约定

- `obsidian` 用来读写知识库笔记。
- `projectmem` 用来记录主动记忆和跨项目经验。
- 其他支持 MCP 的 agent 按同样思路配置：一个 Node 命令启动 MCPVault，一个 Python 命令启动 projectmem。
