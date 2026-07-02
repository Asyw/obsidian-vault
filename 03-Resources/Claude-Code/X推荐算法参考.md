---
tags:
  - reference
  - algorithm
created: 2026-07-03
source: Claude Code 记忆系统
---

# X（推特）"为你推荐"算法参考

**仓库**: https://github.com/xai-org/x-algorithm
**学习笔记**: `D:\Documents\X推荐算法学习笔记.md`

## 核心架构

两阶段推荐系统：
1. **召回（Retrieval）** — Thunder（内网，Rust）+ Phoenix（外网，JAX）并行拉取候选
2. **排序（Ranking）** — Grok Transformer 模型预测互动概率，加权排序

## 四大组件

| 组件 | 职责 | 技术栈 |
|------|------|--------|
| Home Mixer | 编排层：混合候选、过滤、广告插入 | Rust |
| Thunder | 内网内容（关注的人）| Rust |
| Phoenix | 召回+排序核心 AI 模型 | Python/JAX/Haiku |
| Grox | 内容理解：分类、安全、embedding | Python/gRPC |

## 关键要点

- 去掉所有手工特征，纯 Transformer learned
- 用哈希技巧（hashing trick）处理海量用户/推文 ID，省内存
- JAX + Haiku 框架
- 预训练小模型可用（256维，2层 Transformer，~3GB）
