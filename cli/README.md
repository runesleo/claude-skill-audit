# Skill Audit Lite（`claude-skill-audit` 的只读 CLI 组件）

一个零依赖、只读、可离线运行的小工具：**每 30 天盘点 AI Skills，分清「已记录调用」「没有日志」「实际是否有价值」**。

核心原则：**没有调用记录 ≠ 没有被使用，更 ≠ 应该删除。**

你可以先直接把 [PROMPT.md](PROMPT.md) 复制给自己的 AI 助手，让它按同样的标准做一次只读体检；需要可复核的数字，再运行脚本。原仓库的 [SKILL.md](../SKILL.md) 继续负责规则-执行缺口、触发冲突和过时模式检查，CLI **并未替代**这些能力。

## 60 秒开始

Python 3.9+，无需 `pip install`、API Key 或网络。下面代码块均在仓库根目录的 `cli/` 中执行：

```bash
cd cli
```

先用附带的虚构数据体验完整报告：

```bash
python3 skill_audit.py \
  --skills-root examples/skills \
  --claude-log examples/claude.log \
  --event-csv examples/events.csv \
  --expect-executor Claude \
  --expect-executor Codex \
  --expect-executor Gemini \
  --as-of 2026-11-12T00:00:00Z
```

在自己的 Mac 上审计已安装的 Claude Skills：

```bash
python3 skill_audit.py \
  --skills-root "$HOME/.claude"/skills \
  --expect-executor Claude \
  --expect-executor Codex
```

这条命令会立即枚举实际存在的 `SKILL.md`，但**没有调用日志时，统计会明确显示未知**。它不会假装能自动读取所有 AI 的内部对话历史。

如果你**此前自行配置过**把 Claude Skill 调用写到 `~/.claude/skill-usage.log` 的 Hook，且其 TSV 行结构为 `Unix秒级时间戳<TAB>事件<TAB>Skill目录名`，可额外传入日志：

```bash
python3 skill_audit.py \
  --skills-root "$HOME/.claude"/skills \
  --claude-log ~/.claude/skill-usage.log \
  --expect-executor Claude \
  --expect-executor Codex
```

> `~/.claude/skill-usage.log` 是一种**自定义 Hook 日志约定**，并非 Claude 默认自带文件。若文件不存在，不要强行指定；先检查自己使用了什么采集方式。这个工具不会安装 Hook、修改 Claude/Codex 配置或产生新后台任务。

也可以通过 JSON 获取结构化结果（供你自己的看板进一步加工）：

```bash
python3 skill_audit.py --skills-root examples/skills --event-csv examples/events.csv --format json
```

## 多 AI 执行器：统一事件格式

把各执行器**已有、合法可读**的调用记录整理成一个 UTF-8 CSV（不要求一定是 Claude）：

```csv
timestamp,executor,skill
2026-11-11T09:00:00Z,Codex,research
2026-11-11T10:00:00Z,Claude,research
```

- `timestamp`：ISO8601（推荐）或 Unix 秒级时间戳。
- `executor`：如 `Codex`、`Claude`、`Gemini`；名称大小写要一致。
- `skill`：安装目录名称（不是自由文本标题）。
- `--event-csv`、`--skills-root` 和 `--expect-executor` 都可以重复传入。
- 显式指定预期执行器但缺少有效日志时，该执行器的 Skill 调用数记为 `null` / `未知`，不是 `0`。

脚本只计数给定窗口内、能对应到所扫描 Skill 的事件；会统计未匹配事件、格式损坏行以及重复 Skill 目录名，帮助你识别采集缺口。**提供日志 ≠ 证明 Hook 连续运行**，因此报告里的 `coverage_verified` 始终是 `false`。

## 看报告时别踩这 4 个坑

1. **调用次数是观测值，不是全平台真实总数**。尤其不要把单个 Claude Hook 的计数当成 Codex 或其他 Agent 的总使用量。
2. **零观测的常见原因是没记录、没触发或者尚未遇到适用任务**。先查覆盖与触发，再谈 Skill 是否无用。
3. **低频救急型 Skill 不应自动淘汰**。事故排障、密钥泄露应对等 Skill，调用少可能反而是好事。
4. **效果要实测**。选 1–3 个真实任务做 Skill ON/OFF 对照，记录质量、耗时、Token/成本、返工；这份脚本不会编造效果数据。

直接用 [AB_TEMPLATE.md](AB_TEMPLATE.md) 记录真实效果，给自己留一个 `[保留 / 改进触发 / 继续观察]` 清单即可；不要按次数自动删除。

## 隐私与安全

- 仅读取用户明确指定的目录和日志；**不会读取 `SKILL.md` 的正文、执行其中的命令、修改/删除 Skill、联网或上传任何数据**。
- 默认将 Markdown 报告打印到终端，日志路径和原始日志行不会写入报告。
- **Skill 目录名称本身可能是敏感信息**。分享输出前请亲自审查或只分享自己的结论，别直接公开私人报告。
- 对不存在/不可读的显式日志报错并退出，不悄悄把不可读解释成零调用。
- `SKILL.md` 文件年龄如果操作系统可提供文件创建时间，会作为参考；否则返回未知。文件创建时间也不等于 Skill 实际安装日期。

## 本地验证

```bash
python3 -m unittest discover -s tests -v
```

本项目最初是从真实的「30 天审计、跨 Claude/Codex 覆盖缺口、3 项 A/B 对照」工作复盘抽象出来的，但**示例、测试及计划公开的代码没有任何个人日志或账号内容**。适合当作一个小而明确的方法起点，不自称完整的 Agent 可观测性平台。

License：MIT，见 [LICENSE](../LICENSE)。
