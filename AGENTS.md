# AGENTS.md

请始终使用简体中文回复，除非用户明确要求使用其他语言。

## Obsidian 记忆规则

这个目录是用户的 Obsidian AI 记忆知识库，路径固定为：

`/Users/xiaosong/Documents/Obsidian`

可用的标准 MCP 记忆入口：

- `obsidian`: 通过 MCPVault 读写这个 Obsidian vault，适合查笔记、写项目记录、更新 frontmatter、搜索标签。
- `projectmem`: 通过 projectmem 记录主动记忆，适合记录问题、失败尝试、修复、架构决策、跨项目经验。

每次开始项目相关工作时：

1. 优先调用 `projectmem` 的 `get_instructions()`、`get_summary()`、`get_project_map()`。
2. 使用 `obsidian` 搜索或读取 `01-Projects/项目索引.md`，确认这个项目是否已有笔记。
3. 如果当前项目还没有接入记忆，建议运行 `Scripts/connect-project-memory.sh <项目路径>`。

每次结束项目相关工作前：

- 用 `projectmem` 记录本次新增的问题、尝试、修复、决策或重要约束。
- 用 `obsidian` 在对应项目笔记的“工作记录”中追加简短记录。
- 不记录密钥、token、私人身份信息或大段聊天原文。

