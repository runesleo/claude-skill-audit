---
name: skill-audit 技能树体检
description: 扫描 ~/.claude/skills/ 输出热度/死 skill/冲突/过期 pattern 报告。周日运营日跑。触发：/skill-audit、"技能树体检"、"skill 健康度"、"哪些 skill 没用"。
effort: xhigh
---

# Skill Audit — 技能树体检

> 对照 Tw93 Waza 的 /health 维度。56+ skill 没人管就是 tech debt。

## 触发场景

- 周日 /today 自动建议
- 手动 /skill-audit
- 新增 >5 个 skill 后复盘
- 半年一次基线对比

## 执行流程

### Step 1 — 清点家底
```bash
ls ~/.claude/skills/ | grep -v '^_\|\.md$\|\.jsonl$' | wc -l
ls ~/.claude/skills/ | grep -v '^_\|\.md$\|\.jsonl$' > /tmp/skill-list.txt
```

### Step 2 — 热度分析（execution-log.jsonl）
```bash
cat ~/.claude/skills/execution-log.jsonl | jq -r '.skill' | sort | uniq -c | sort -rn
```

注意：log 可能严重欠记录（当前 516B）。同步查 patterns.md / today.md 最近 30 天触发痕迹：
```bash
grep -roh '[a-z-]*-skill\|/[a-z-]*' ~/.claude/memory/today.md ~/.claude/memory/yesterday.md 2>/dev/null | sort -u
```

### Step 3 — 死 skill 识别
连续 30 天 0 触发 + 无 hook 绑定 + 无 CLAUDE.md 引用 → 候选死 skill。
```bash
for skill in $(cat /tmp/skill-list.txt); do
  cnt=$(grep -c "\"skill\":\"$skill\"" ~/.claude/skills/execution-log.jsonl 2>/dev/null || echo 0)
  ref=$(grep -r "$skill" ~/.claude/rules/ ~/.claude/CLAUDE.md 2>/dev/null | wc -l)
  echo "$skill | log:$cnt | ref:$ref"
done | sort -t'|' -k2n
```

### Step 4 — 冲突检测
两个 skill 触发条件高度重叠 = 冲突。扫 description 字段关键词：
- review / codex review
- debug / systematic-debugging
- xhs-publish / xhs-style / xhs-review
- content-pipeline / article-pipeline

输出："⚠️ [A] 和 [B] 可能重叠：共同触发词 = [...]"

### Step 5 — 过期 pattern 清理
```bash
# patterns.md 连续 5 session 未触发的条目
grep -n "pattern_" ~/.claude/skills/leo-evolution/learned/patterns.md 2>/dev/null | head -20
```
建议用户手动 review，不自动删。

### Step 6 — 输出报告

格式：
```
📊 Skill Tree Audit — YYYY-MM-DD

📈 家底：56 skill / 4 hook / 12 别名
🔥 Top 5 热度：leo-style(12) / today(8) / recall(6) / codex(4) / x-research(3)
💀 死 skill 候选：[列表]（建议移到 _archived/）
⚠️ 冲突疑似：[列表]
🧹 过期 pattern：[数量]，见 patterns.md 第 N 行

🎯 行动项：
- [ ] 归档死 skill
- [ ] 合并冲突 skill
- [ ] 清理过期 pattern
```

**保存基线**：报告写入 `~/.claude/memory/skill-tree-audit-YYYY-MM-DD.md`，下次对比增量。

## 设计哲学

- **不自动删**：skill 是肌肉记忆，死 skill 也可能是季节性触发（/tweet-review 两周一次）
- **归档 > 删除**：候选死 skill 移到 `_archived/`，保留 30 天再永久删
- **人工 review**：自动识别 + 人工判断，不做全自动清理
