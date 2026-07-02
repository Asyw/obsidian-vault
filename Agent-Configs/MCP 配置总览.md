# MCP 配置总览

这些配置让 Windows 上的 Codex、Claude、Cursor、OpenCode 等 agent 共用同一个 Obsidian 知识库和主动记忆系统。

## Windows 路径

- Vault: `C:\Users\NINGMEI\Documents\Obsidian`
- MCPVault server: `C:\Users\NINGMEI\Documents\Obsidian\.integrations\github\mcpvault\dist\server.js`
- projectmem Python: `C:\Users\NINGMEI\Documents\Obsidian\.venv-projectmem\Scripts\python.exe`
- Codex Node: `C:\Users\NINGMEI\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`

## Codex

配置文件：

`C:\Users\NINGMEI\.codex\config.toml`

生效方式：完全退出 Codex 后重新打开。

```toml
[mcp_servers.obsidian]
command = 'C:\Users\NINGMEI\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
args = ['C:\Users\NINGMEI\Documents\Obsidian\.integrations\github\mcpvault\dist\server.js', 'C:\Users\NINGMEI\Documents\Obsidian']
startup_timeout_sec = 120

[mcp_servers.projectmem]
command = 'C:\Users\NINGMEI\Documents\Obsidian\.venv-projectmem\Scripts\python.exe'
args = ['-m', 'projectmem.mcp_server', '--root', 'C:\Users\NINGMEI\Documents\Obsidian']
cwd = 'C:\Users\NINGMEI\Documents\Obsidian'
startup_timeout_sec = 120
```

## Claude Desktop

配置文件：

`C:\Users\NINGMEI\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "C:\\Users\\NINGMEI\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
      "args": [
        "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.integrations\\github\\mcpvault\\dist\\server.js",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ]
    },
    "projectmem": {
      "command": "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.venv-projectmem\\Scripts\\python.exe",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ]
    }
  }
}
```

## Claude Code

用户级配置可写入：

`C:\Users\NINGMEI\.claude.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "C:\\Users\\NINGMEI\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
      "args": [
        "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.integrations\\github\\mcpvault\\dist\\server.js",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ],
      "env": {}
    },
    "projectmem": {
      "command": "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.venv-projectmem\\Scripts\\python.exe",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
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
      "command": "C:\\Users\\NINGMEI\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
      "args": [
        "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.integrations\\github\\mcpvault\\dist\\server.js",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ]
    },
    "projectmem": {
      "command": "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.venv-projectmem\\Scripts\\python.exe",
      "args": [
        "-m",
        "projectmem.mcp_server",
        "--root",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ]
    }
  }
}
```

## OpenCode

配置文件：

`C:\Users\NINGMEI\.config\opencode\opencode.json`

```json
{
  "mcp": {
    "obsidian": {
      "type": "local",
      "command": [
        "C:\\Users\\NINGMEI\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.integrations\\github\\mcpvault\\dist\\server.js",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ],
      "enabled": true
    },
    "projectmem": {
      "type": "local",
      "command": [
        "C:\\Users\\NINGMEI\\Documents\\Obsidian\\.venv-projectmem\\Scripts\\python.exe",
        "-m",
        "projectmem.mcp_server",
        "--root",
        "C:\\Users\\NINGMEI\\Documents\\Obsidian"
      ],
      "enabled": true
    }
  }
}
```

## 验证命令

```powershell
Set-Location -LiteralPath "C:\Users\NINGMEI\Documents\Obsidian"
& ".\.venv-projectmem\Scripts\pjm.exe" show
& "C:\Users\NINGMEI\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" ".\.integrations\github\mcpvault\dist\server.js" "C:\Users\NINGMEI\Documents\Obsidian"
```

第二条是 MCP stdio server，正常情况下会等待客户端输入，不会打印普通帮助文本。

## 使用约定

- `obsidian` 用来读写知识库笔记。
- `projectmem` 用来记录主动记忆和跨项目经验。
- 新项目接入 Windows 知识库时优先运行 `Scripts/connect-project-memory.ps1 <项目路径>`。
- 不记录密钥、token、私人身份信息或大段聊天原文。

## Mac mini 参考

Mac mini 原始 vault 路径是 `/Users/xiaosong/Documents/Obsidian Vault`。Windows 这套知识库是从它同步来的独立副本，后续如果要双向同步，建议通过 Git 或明确的同步脚本处理，避免手动复制时覆盖新记录。
