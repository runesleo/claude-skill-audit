# claude-skill-audit — AI Skill 技能树体检

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue) ![MIT](https://img.shields.io/badge/License-MIT-green)

[English](README.md) · 简体中文

不需要再装一个审计系统：把已有 Skill 的**清单、触发证据、规则要求和实际效果**定期对一遍。先找漏采与漏触发，再判断是否应该调整。

## 两种使用方式

### 1. AI 引导的 Skill 体检（Claude Code）

```bash
git clone https://github.com/runesleo/claude-skill-audit "$HOME/.claude"/skills/skill-audit
```

在 Claude Code 中触发 `/skill-audit`。仓库根目录的 [SKILL.md](SKILL.md) 依次检查：

1. 清点 Skills、Hooks、别名和规则引用。
2. 核对**已记录调用热度**、采集机制及时间覆盖，明确“未知”。
3. 查找**规则-执行缺口**：规则要求调用，但日志或任务证据未能证明发生过；这是待核验线索，不是断言。
4. 找可能重复的触发条件、过时的模式；人工给出保留、改进触发、继续观察的判断。

整个过程以只读分析为主，不自动删除、归档或改配置。

### 2. 跨 Claude / Codex / 其他执行器的只读 CLI

Python 3.9+，标准库即可运行，无需安装包、Token、联网或后台服务。先用**纯合成样例**在仓库根目录体验：

```bash
python3 cli/skill_audit.py \
  --skills-root cli/examples/skills \
  --claude-log cli/examples/claude.log \
  --event-csv cli/examples/events.csv \
  --expect-executor Claude \
  --expect-executor Codex \
  --expect-executor Gemini \
  --as-of 2026-11-12T00:00:00Z
```

自己的 Skill 清单示例（没有日志也会列出清单，使用情况记为未知）：

```bash
python3 cli/skill_audit.py \
  --skills-root "$HOME/.claude"/skills \
  --expect-executor Claude \
  --expect-executor Codex
```

如果你**已自行配置过** Claude Hook 把调用记入 `~/.claude/skill-usage.log`，且格式是 `timestamp<TAB>event<TAB>skill`，才能添加 `--claude-log ~/.claude/skill-usage.log`。这个文件不是 Claude 默认日志；脚本不会安装 Hook，也不会悄悄读取其他执行器的聊天记录。其他执行器可导入已有 `timestamp,executor,skill` CSV。

详见 [CLI 详细说明](cli/README.md)、[直接复制给 AI 的审计提示词](cli/PROMPT.md)、[Skill ON/OFF 实际效果对照模板](cli/AB_TEMPLATE.md)。CLI 仅对已提供数据做数量/覆盖审计；根目录的 Skill 负责**规则、冲突、过期模式**等定性检查，不会把一个数字等同于 Skill 的价值。

## 避免 4 个误判

- **没有记录 ≠ 没有使用**：单一 Claude Hook 的 0 不能代表 Codex/Gemini 的真实情况。
- **有日志 ≠ 全程覆盖**：采集可能中断，`coverage_verified=false` 是刻意的保守判断。
- **零观测 ≠ 无价值**：故障应急、安全类 Skill 低频往往合理。
- **次数 ≠ 效果**：选真实任务做 Skill ON/OFF 对照，量化质量、时间、成本与返工，再决定是否调整。

若在网上分享输出，先确认 Skill 名称、报告、规则和日志中没有私人数据。本仓库公开示例均为虚构数据。

## 致谢与设计

原思路来自 [@HiTw93 的 Waza](https://github.com/tw93/Waza)（MIT）的 `/health` 维度，并参考了 [darwin-skill](https://github.com/alchaincyf/darwin-skill) 周边关于 Skill 维护的讨论。保留原有的清单盘点、热度、规则执行缺口、触发冲突和过时模式检查，再加跨执行器观测层；不是只有安全审查。

坚持**只读、证据分级、人工决定**：不会自动删除 Skill，也不改个人环境。

运行测试：`python3 -m unittest discover -s cli/tests -v`。

## 已验证（本地候选，不等于跨平台验收）

- 2026-11-12：在 Python **3.12.14** 环境中，6/6 端到端测试通过，源码编译通过，仓库原版开源隐私预检返回 `exit 0`。
- 用**合成**的 2 个 Skill、3 条已记录调用演示，Claude/Codex 有样例日志，未提供 Gemini 日志时正确显示「未知」。
- 还**没有**实测 Python 3.9 运行时、真实用户全部日志覆盖率或实际效率提升；公开的模拟计数不能代表任何个人机器。

## 前提、隐私与已知限制（v0.0.1）

- Claude Code 原始 Skill 使用方式需要本地 Claude Code；单独 CLI 仅需 Python 3.9+ 与一个包含 Skill 子目录的目录，日志可选。
- CLI 只检查每个根目录下一层的 Skill 文件元数据，不读取或执行 `SKILL.md` 正文；不会下载数据、装 Hook 或更改配置。
- 多个根目录的**同名 Skill** 无法可靠归因；目录创建时间不等于安装时间；日志存在也不能证明连续采集。
- 报告可能包含 Skill 目录名称，公开前需自行脱敏；本仓库内的日志、示例和测试均为虚构数据。
- 规则-执行缺口、触发冲突和过时模式是原始 Skill 的人工核验流程，CLI **不宣称**可以自动完成，更不会按次数删除任何 Skill。

## 后续方向

- 识别 Hook 引用却不存在的 Skill、基础清单差异、跨机器一致性。
- 在不放宽隐私边界的前提下改善已有日志的时间覆盖与来源验证。
- 根据真实用户反馈决定是否值得做趋势看板；不为追求功能数量扩张复杂度。

作者：Leo（[@runes_leo](https://x.com/runes_leo)） · [leolabs.me](https://leolabs.me)。许可证：[MIT](LICENSE)。
