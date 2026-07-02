---
tags:
  - linux
  - command-line
  - practice
created: 2026-07-03
source: E:\heikev1\linux-command-practice-guide.md
---

# Linux 命令练习大全

## 核心思想

- 一切皆文件
- 小工具组合（管道）
- 文本优先（配置/日志/脚本）
- 权限清晰（用户/组/读写执行）
- 先观察再修改

## 章节索引

| 章 | 内容 | 关键命令 |
|:--:|------|---------|
| 1 | 命令结构 | `pwd whoami man` |
| 2 | 目录与路径 | `cd mkdir rmdir` |
| 3 | 查看目录 | `ls -lah` |
| 4 | 文件操作 | `cp mv rm touch` |
| 5 | 通配符 | `*.log data?.csv {a,b}.py` |
| 6 | 查看内容 | `cat less head tail wc` |
| 7 | 重定向与管道 | `> >> 2> \| tee` |
| 8 | 搜索 | `find grep` |
| 9 | 文本处理 | `sort uniq cut column` |
| 10 | sed 与 awk | `sed 's/x/y/' awk -F,` |
| 11 | 权限 | `chmod chown id` |
| 12 | 进程 | `ps top kill jobs fg bg` |
| 13 | 系统信息 | `df du free uptime lscpu` |
| 14 | 网络 | `ip addr ping curl ss` |
| 15 | 压缩 | `tar gzip zip` |
| 16 | 包管理 | `apt dnf pacman` |
| 17 | 变量 | `$PATH export $(cmd)` |
| 18 | 脚本 | `#!/bin/bash $1 [ -f ] for` |
| 19-20 | 日志+systemd | `grepawk journalctl` |
| 21-22 | cron+vim | `crontab -e vim` |
| 23-25 | 综合项目 | 整理目录、日志报告、备份脚本 |

## 数字权限速查

- `r=4, w=2, x=1`
- `7=rwx, 6=rw-, 5=r-x`

## 综合练习项目

1. **整理下载目录** — 分类移动文件 + 打包
2. **日志统计报告** — grep+awk 生成汇总
3. **备份脚本** — 带日期、参数化、磁盘检查

## 每日练习路线

- Day 1: 导航 (ls/cd/mkdir)
- Day 2: 文件查看 (cat/less/head/tail)
- Day 3: 搜索 (find/grep)
- Day 4: 文本处理 (sort/uniq/cut/sed/awk)
- Day 5: 权限与脚本
- Day 6: 进程与系统
- Day 7: 综合复盘
