---
tags:
  - reference
  - scrapling
  - crawling
created: 2026-07-03
source: Claude Code 记忆系统
---

# Scrapling 安装记录

## 安装内容

- **Python 库**: `scrapling[all] 0.4.8`，虚拟环境 `/home/ubuntu/venvs/scrapling/`
- **Claude Skill**: `/scrapling-official` 已安装
- **浏览器**: Chromium headless shell 148 已下载到 `~/.cache/ms-playwright/`

## 核心能力

- 自动绕过 Cloudflare Turnstile 等反爬（`StealthyFetcher` 开箱即用）
- 自适应解析：网站改版后自动重新定位元素（`adaptive=True` / `auto_save=True`）
- 完整爬虫框架：多 session 并发、暂停/恢复、代理轮换
- CLI 直接抓取：`scrapling extract get/fetch/stealthy-fetch url file.md`
- 支持 MCP Server 协议

## 环境注意

WSL2 环境下有代理设置（`http://192.168.1.5:7897`），但代理不通外网。需要 `unset http_proxy https_proxy` 后直接连。
