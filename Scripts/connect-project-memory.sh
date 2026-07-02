#!/usr/bin/env bash
set -euo pipefail

VAULT="/Users/xiaosong/Documents/Obsidian Vault"
PJM="$VAULT/.venv-projectmem/bin/pjm"
PROJECT_PATH="${1:-$PWD}"
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
PROJECT_NAME="${2:-$(basename "$PROJECT_PATH")}"
SAFE_NAME="$(printf '%s' "$PROJECT_NAME" | tr '/:' '--')"
NOTE="$VAULT/01-Projects/$SAFE_NAME.md"
INDEX="$VAULT/01-Projects/项目索引.md"

if [ ! -x "$PJM" ]; then
  echo "projectmem CLI not found: $PJM" >&2
  exit 1
fi

echo "Initializing project memory in: $PROJECT_PATH"
(
  cd "$PROJECT_PATH"
  "$PJM" init
)

mkdir -p "$VAULT/01-Projects"

if [ ! -f "$NOTE" ]; then
  cat > "$NOTE" <<EOF_NOTE
---
type: project
status: active
project_path: "$PROJECT_PATH"
memory: "$PROJECT_PATH/.projectmem"
tags:
  - project
  - ai-memory
---

# $PROJECT_NAME

## 项目路径

\`$PROJECT_PATH\`

## 记忆入口

- projectmem: \`$PROJECT_PATH/.projectmem\`
- Obsidian 笔记: 本页

## 项目目标


## 关键决策


## 已知问题


## 工作记录

- $(date '+%F %T') 已接入 Obsidian AI 记忆库。
EOF_NOTE
fi

if ! grep -Fq "[[$SAFE_NAME]]" "$INDEX"; then
  printf '| %s | `%s` | 已接入 projectmem | [[%s]] |\n' "$PROJECT_NAME" "$PROJECT_PATH" "$SAFE_NAME" >> "$INDEX"
fi

(
  cd "$PROJECT_PATH"
  "$PJM" note "Connected this project to the Obsidian AI memory vault at $VAULT." || true
)

echo "Done."
echo "Project note: $NOTE"

