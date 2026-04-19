# skill-audit — Claude Code 技能树体检

[English](README.md) · 中文

> 给自己的 Claude Code 配置做一次"用了什么 / 没用什么 / 互相打架什么"的扫描。
> 输出：热度排名 + 死 skill 候选 + 规则-执行 gap + 冲突诊断。

## 灵感与归属

这个 skill 是 [@HiTw93](https://x.com/HiTw93) 的 [Waza](https://github.com/tw93/Waza)（MIT）启发的产物。Waza 把工程能力拆成 8 维（think / design / hunt / check / read / write / learn / health）让 Claude 可执行；我用这 8 维对照自己的 62 个 skill 时发现 `/health` 是空的——没人在审"用了什么 / 没用什么 / 互相打架什么"，于是建了 skill-audit 来补这个维度。**没有 Waza 就没有这个 skill。**

横向扫描的具体实现（死 skill 候选 / 冲突检测 / 过期 pattern 识别 / 报告输出）是本地写的。

---

## What it does

跑一次扫描，输出一份当前 skill 树的体检报告，覆盖：

1. **家底清点** — 一共多少 skill / hook / 别名
2. **热度分析** — 真实调用次数排名（数据源 `~/.claude/skill-usage.log`，PreToolUse hook 自动埋点）
3. **死 skill 识别** — 连续 30 天 0 触发 + 无 hook 绑定 + 无 CLAUDE.md 引用 → 候选归档
4. **规则-执行 gap** — 有规则引用但 0 调用的 skill（写了不跑 = 没写）
5. **冲突检测** — 触发条件高度重叠的 skill 群组

不自动删，只识别 + 建议归档到 `_archived/`，30 天观察期再永久删。

---

## 我自己跑出来的样子（4/17 baseline）

| 指标 | 数值 |
|------|------|
| 总 skill 数 | 61 |
| 11 天总调用 | 1388 次（126/天） |
| 有调用记录 | 46 个（75%） |
| 从未调用 | 23 个（37.7% 冷藏率） |
| Top 5 集中度 | 92% 调用 |

最值钱的发现不是死 skill 数量，而是 **6 个有 P0 规则引用但 0 调用的 skill**——其中 `systematic-debugging` 是写在铁律里的"连续 3 次失败必走四阶段"，11 天 1388 次调用里**一次都没触发**。规则与执行的 gap 客观存在，写了不跑等于没写。

---

## 使用方法

### 安装

```bash
git clone https://github.com/runesleo/claude-skill-audit ~/.claude/skills/skill-audit
```

### 前提
- Claude Code 已安装并配置了若干 skill
- 启用 PreToolUse hook 写入 `~/.claude/skill-usage.log`（自动埋点是 audit 的数据基座）
- 主仓 skill 目录：`~/.claude/skills/`

### 触发
- 手动：`/skill-audit`
- 自动建议时机：周日运营日 / 新增 ≥5 skill 后 / 半年基线对比 / 怀疑 skill 冗余时

### 输出
报告写入 `~/.claude/memory/skill-tree-audit-YYYY-MM-DD.md`，下次跑增量对比。

---

## 设计哲学

- **不自动删**：skill 是肌肉记忆，死 skill 也可能是季节性触发（如周复盘 skill 一周才一次）
- **归档 > 删除**：候选死 skill 移到 `_archived/`，30 天观察期内可复活
- **人工 review**：自动识别 + 人工判断，不做全自动清理
- **数据基座先于审计**：没有 PreToolUse hook 的 `skill-usage.log`，audit 就是猜

---

## Roadmap

**检测能力**
- [ ] 识别"hook 引用但 skill 目录里没有"的孤儿引用
- [ ] 跨机器审计（本地 Mac + VPS skill 状态对齐）
- [ ] 与上次 baseline 做 diff，高亮变化

**报告输出**
- [ ] 趋势可视化 dashboard（HTML）
- [ ] 导出 Obsidian Daily Note
- [ ] Slack / Discord webhook 推送

---

## 关于作者

Leo ([@runes_leo](https://x.com/runes_leo))，AI × Crypto 独立构建者。

用 Claude Code 做两件事：
- **预测市场量化** — 在 [Polymarket](https://polymarket.com/?via=runes-leo&r=runesleo&utm_source=github&utm_content=claude-skill-audit) 跑做市和量化策略
- **内容自动化** — 包括这个 repo 在内的工具链，让一个人也能跑出团队的产能

更多实战：[leolabs.me](https://leolabs.me)

---

## License

MIT — 自由 fork、改、发。改的时候保留对 [@HiTw93 Waza](https://github.com/tw93/Waza) 的致谢，让链条不断。
