#!/bin/bash
# Obsidian 知识库一键同步脚本
# 用法: bash Scripts/git-sync.sh "提交信息"
#       不带参数则自动生成时间戳提交信息

set -e
VAULT_DIR="/Users/xiaosong/Documents/Obsidian"
ENV_FILE="/Users/xiaosong/.openclaw/.env"
REMOTE="origin"
BRANCH="main"

# 读取 token
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "❌ 未找到 $ENV_FILE"
    exit 1
fi

cd "$VAULT_DIR"

echo ">>> 拉取远程更新..."
git pull "$REMOTE" "$BRANCH" --rebase 2>&1 || echo "⚠️  拉取失败，继续推送..."

if ! git diff-index --quiet HEAD --; then
    COMMIT_MSG="${1:-📦 $(date '+%Y-%m-%d %H:%M') 自动同步}"
    echo ">>> 提交: $COMMIT_MSG"
    git add -A
    git commit -m "$COMMIT_MSG"
else
    echo ">>> 无变更，跳过提交"
fi

echo ">>> 推送到 GitHub..."
git push "$REMOTE" "$BRANCH"

echo ">>> ✅ 同步完成"
