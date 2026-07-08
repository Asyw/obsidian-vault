---
type: project
status: active
project_path: 'C:\Users\NINGMEI\.codex\plugins\cache'
memory: 'C:\Users\NINGMEI\Documents\Obsidian\.projectmem'
tags:
  - project
  - codex
  - plugin
  - localization
  - ai-memory
---
# Codex 插件中文化项目

## 项目定位

这个项目记录 Codex 插件界面中文化的工作。目标是让 Codex 里常见插件在界面上显示中文名称和中文简介，方便日常使用时快速识别用途。

## 当前状态

- 状态：已完成第一版中文化。
- 操作日期：2026-07-05。
- 主要位置：`C:\Users\NINGMEI\.codex\plugins\cache`。
- 修改对象：各插件缓存目录下的 `.codex-plugin/plugin.json`。
- 修改字段：`interface.displayName`、`interface.shortDescription`、部分 `interface.longDescription`。
- 未修改字段：插件内部 `name`，例如 `browser`、`github`、`computer-use`。这些 ID 必须保持英文，否则 Codex 可能无法识别插件。

## 已中文化插件

| 内部 ID | 原显示名 | 中文显示名 | 用途 |
| --- | --- | --- | --- |
| `browser` | Browser | 浏览器 | 控制 Codex 内置浏览器 |
| `chrome` | Chrome | Chrome 浏览器 | 控制本机 Chrome 浏览器 |
| `computer-use` | Computer Use | 电脑操作 | 控制 Windows 桌面应用 |
| `github` | GitHub | GitHub 代码协作 | 处理仓库、PR、Issue 和 CI |
| `openai-developers` | OpenAI Developers | OpenAI 开发者 | 使用 OpenAI 平台和 API |
| `documents` | Documents | 文档 | 创建和编辑文档文件 |
| `pdf` | PDF | PDF 文件 | 读取、创建和检查 PDF |
| `presentations` | Presentations | 演示文稿 | 创建和编辑幻灯片 |
| `spreadsheets` | Spreadsheets | 电子表格 | 创建、分析和编辑表格 |
| `template-creator` | Template Creator | 模板创建器 | 制作可复用的文档模板 |

## 备份

每个被修改的 `plugin.json` 旁边都保留了一份原始备份：

`plugin.json.bak.zh-20260705`

如果以后想恢复英文显示，可以用这些备份覆盖对应的 `plugin.json`。

## 重要限制

- 这次修改的是 Codex 插件缓存，不是插件源仓库。
- Codex 更新插件或重新安装插件后，中文显示名可能被覆盖。
- 插件内部 ID 仍然应该保留英文，例如 `computer-use` 不能直接改成中文。
- 如果要长期稳定保留中文化，后续可以做成个人 marketplace 或个人本地插件入口，而不是只改缓存。

## 后续维护

1. Codex 更新后，如果显示名恢复英文，检查对应缓存插件的 `.codex-plugin/plugin.json`。
2. 重新应用中文映射表。
3. 保留新的备份后缀，避免覆盖旧备份。
4. 如果插件列表变化，把新增插件追加到本笔记的“已中文化插件”表格。

## 相关记忆

projectmem 已记录一条 gotcha：Codex bundled/remote 插件可以通过缓存 `plugin.json` 的 `interface` 字段中文化显示名，但缓存更新可能覆盖；内部插件 ID 必须保持规范英文。
