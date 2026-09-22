# AGENTS.md — blue_wonderland

博客「Blue Wonderland」（iamalex.blue），基于 astro-theme-typography。

## 工作契约

本仓库遵循 **[agent-workshop 统一契约](https://github.com/iamalexblue/agent-workshop/blob/main/AGENTS.md)**，要点：

- **身份声明**：每条 issue/PR comment 开头署名 `> 🤖 <名称> · <环境>`（如
  `dsh/qwen3.8-flash · DSH on openSUSE Tumbleweed_MSI`）；commit message 结尾加
  `Agent:` / `Env:` trailer。本仓库是公开仓，署名只用模型名与系统名，不含私人邮箱。
- **Issue 驱动**：开工前 `gh issue create`（内容变更也算），一个 issue 一个分支
  （`feat/<N>-<slug>` 等），PR body 含改动摘要/验证方式/`Closes #N`，squash merge。
- 写作类任务的风格规范见下，动笔前先读。

## 项目事实

```bash
pnpm dev      # 本地预览（astro check + dev）
pnpm build    # = astro check && astro build，交付前必须通过
pnpm lint     # eslint（antfu 配置 + unocss）
```

- 文章在 `src/content/posts/`，frontmatter 字段：`title / pubDate / categories /
description / lastmod`。新文章可用 `pnpm theme:create` 生成骨架。
- 中文排版：全文使用尖括号 `<>` 作书名号；正文标点用全角。
- `dist/` 是构建产物，改代码后由 `pnpm build` 重新生成再提交，不要手改。
- `.frontmatter/database/*.json` 会被编辑器插件自动改动：只提交与本次任务相关的变化。
- 部署走仓库既有 workflow；主题上游是 moeyua/astro-theme-typography，同步上游时
  单独开 issue/PR，不与内容改动混在一个 PR。

## 博客写作风格

细节以 agent-workshop 侧的 `blog-style-alex` skill（或人类提供的风格说明）为准；
核心要求：技术折腾记按「背景 → 踩坑 → 方案对比 → 结论」展开，散文随笔不设结构要求。
