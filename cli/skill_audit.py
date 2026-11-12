#!/usr/bin/env python3
"""Read-only, standard-library audit of recorded AI Skill invocations.

Reports observations, never claims that missing log events prove non-usage.
This program never executes SKILL.md, changes installed Skills, or sends data.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator


class InputError(Exception):
    """The user-provided source cannot be safely audited."""


def parse_time(value: str) -> datetime:
    cleaned = str(value).strip()
    try:
        return datetime.fromtimestamp(float(cleaned), tz=timezone.utc)
    except (ValueError, OverflowError, OSError):
        pass
    try:
        parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("无效时间戳") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def readable_file(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_file():
        raise InputError("无法读取指定日志：文件不存在或不是普通文件")
    try:
        with path.open("r", encoding="utf-8-sig"):
            pass
    except (OSError, UnicodeError) as error:
        raise InputError("无法读取指定日志：权限或编码错误") from error
    return path


def scan_skills(roots: list[str], as_of: datetime) -> tuple[dict[str, int | None], list[str]]:
    inventory: dict[str, int | None] = {}
    duplicates: list[str] = []
    for raw in roots:
        root = Path(raw).expanduser()
        if not root.is_dir():
            raise InputError("无法读取 Skills 目录：路径不存在或不是目录")
        try:
            children = sorted(root.iterdir(), key=lambda p: p.name)
        except OSError as error:
            raise InputError("无法读取 Skills 目录：权限错误") from error
        for child in children:
            # Shared Skill directories are often installed as symlinks.
            # We inspect metadata only, and never read/execute SKILL.md.
            if not child.is_dir():
                continue
            definition = child / "SKILL.md"
            if definition.is_symlink() or not definition.is_file():
                continue
            try:
                birth = getattr(definition.stat(), "st_birthtime", None)
            except OSError:
                birth = None
            age_days = None
            if birth is not None and birth > 0:
                days = int((as_of - datetime.fromtimestamp(birth, tz=timezone.utc)).total_seconds() // 86400)
                if days >= 0:
                    age_days = days
            if child.name in inventory:
                duplicates.append(child.name)
                # Duplicate names cannot reliably be mapped to separate log events.
                inventory[child.name] = None
            else:
                inventory[child.name] = age_days
    return inventory, sorted(set(duplicates))


def claude_events(path: Path, invalid: Counter[str]) -> Iterator[tuple[datetime, str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            for line in handle:
                if not line.strip():
                    continue
                fields = line.rstrip("\r\n").split("\t")
                if len(fields) < 3 or not fields[2].strip():
                    invalid["rows"] += 1
                    continue
                try:
                    timestamp = parse_time(fields[0])
                except ValueError:
                    invalid["rows"] += 1
                    continue
                yield timestamp, "Claude", fields[2].strip()
    except (OSError, UnicodeError) as error:
        raise InputError("无法读取 Claude 日志：权限或编码错误") from error


def csv_events(path: Path, invalid: Counter[str]) -> Iterator[tuple[datetime, str, str]]:
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not {"timestamp", "executor", "skill"}.issubset(reader.fieldnames):
                raise InputError("CSV 需要 timestamp,executor,skill 三列")
            for row in reader:
                try:
                    executor = (row["executor"] or "").strip()
                    skill = (row["skill"] or "").strip()
                    if not executor or not skill:
                        raise ValueError("缺少执行器或 Skill")
                    yield parse_time(row["timestamp"] or ""), executor, skill
                except (ValueError, TypeError):
                    invalid["rows"] += 1
    except (OSError, UnicodeError, csv.Error) as error:
        raise InputError("无法读取事件 CSV：权限、编码或格式错误") from error


def assess(count: int, age_days: int | None, has_unknown: bool) -> str:
    if has_unknown:
        return "先补齐跨执行器证据"
    if count >= 3:
        return "抽样对照实际效果"
    if count:
        return "低频：检查触发是否正确"
    if age_days is not None and age_days < 14:
        return "新安装：继续观察"
    return "零观测：核查漏记与必要性"


def audit(args: argparse.Namespace) -> dict:
    now = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
    start = now - timedelta(days=args.days)
    inventory, duplicates = scan_skills(args.skills_root, now)
    counts: Counter[tuple[str, str]] = Counter()
    executor_totals: Counter[str] = Counter()
    observed_executors: set[str] = set()
    invalid: Counter[str] = Counter()
    unmatched = 0

    logs: list[tuple[str, Path]] = []
    for value in args.claude_log:
        logs.append(("claude", readable_file(value)))
        observed_executors.add("Claude")
    for value in args.event_csv:
        logs.append(("csv", readable_file(value)))

    for kind, path in logs:
        source = claude_events(path, invalid) if kind == "claude" else csv_events(path, invalid)
        for timestamp, executor, skill in source:
            observed_executors.add(executor)
            if not start <= timestamp <= now:
                continue
            if skill not in inventory:
                unmatched += 1
                continue
            counts[(executor, skill)] += 1
            executor_totals[executor] += 1

    expected_executors = sorted(set(args.expect_executor) | observed_executors)
    unknown_executors = set(expected_executors) - observed_executors
    executors = {
        name: {
            "status": "log_supplied" if name in observed_executors else "unknown",
            "observed_calls": executor_totals[name] if name in observed_executors else None,
        }
        for name in expected_executors
    }
    rows = []
    for name in inventory:
        total = sum(counts[(executor, name)] for executor in observed_executors)
        rows.append({
            "name": name,
            "observed_calls": total,
            "by_executor": {
                executor: counts[(executor, name)] if executor in observed_executors else None
                for executor in expected_executors
            },
            "age_days": inventory[name],
            "next_step": assess(total, inventory[name], bool(unknown_executors)),
        })
    rows.sort(key=lambda entry: (-entry["observed_calls"], entry["name"].casefold()))
    return {
        "as_of_utc": now.isoformat().replace("+00:00", "Z"),
        "window_days": args.days,
        "skills_detected": len(rows),
        "observed_calls": sum(executor_totals.values()),
        "coverage_verified": False,
        "executors": executors,
        "skills": rows,
        "invalid_rows": invalid["rows"],
        "unmatched_events": unmatched,
        "duplicate_skill_names": duplicates,
        "limitations": [
            "日志调用次数仅为已记录事件，不等于真实调用次数；缺日志更不等于零调用。",
            "日志存在也无法证明 Hook 在整个窗口持续运行。",
            "Skill 的效果、漏触发及保留价值需要真实任务 A/B 对照，不能由调用量推断。",
            "低频安全防护 Skill 不能因为零观测就直接删除。",
        ],
    }


def escape_markdown(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")


def format_markdown(data: dict) -> str:
    executors = data["executors"]
    names = list(executors)
    table_columns = ["Skill", "已记录调用"] + names + ["下一步"]
    lines = [
        "# Skill Audit Lite · 本地调用观测报告",
        "",
        f"- 统计截止（UTC）：{data['as_of_utc']}；窗口：近 {data['window_days']} 天",
        f"- 找到 Skill：{data['skills_detected']}；**已记录调用**：{data['observed_calls']}",
        "- **口径：零观测不等于真实零调用；缺日志视为未知。**",
        "",
        "## 采集覆盖",
        "",
    ]
    if executors:
        for name, item in executors.items():
            state = "已提供日志（不保证全时段完整）" if item["status"] == "log_supplied" else "未知（未提供可用日志）"
            lines.append(f"- {escape_markdown(name)}：{state}")
    else:
        lines.append("- 未提供日志或预期执行器；所有调用统计均不可判定。")
    lines.extend(["", "## Skill 清单", "", "| " + " | ".join(escape_markdown(k) for k in table_columns) + " |",
                  "| " + " | ".join("---" for _ in table_columns) + " |"])
    for skill in data["skills"]:
        values = [skill["name"], str(skill["observed_calls"])]
        values.extend("未知" if skill["by_executor"][name] is None else str(skill["by_executor"][name]) for name in names)
        values.append(skill["next_step"])
        lines.append("| " + " | ".join(escape_markdown(value) for value in values) + " |")
    lines.extend([
        "", "## 数据质量与使用边界", "",
        f"- 无效日志行：{data['invalid_rows']}；未匹配安装 Skill 的窗口内事件：{data['unmatched_events']}",
        "- 同名 Skill 路径冲突：" + ("、".join(escape_markdown(name) for name in data["duplicate_skill_names"]) if data["duplicate_skill_names"] else "未发现"),
    ])
    lines.extend("- " + limitation for limitation in data["limitations"])
    lines.extend([
        "", "## 30 分钟人工复盘", "",
        "1. 逐一确认 Claude / Codex / 其他执行器的 Skill Hook 是否真实覆盖本期任务。",
        "2. 从真实工作里选 3 个本该触发 Skill 的任务，复盘漏触发及原因。",
        "3. 对其中 1–3 个任务做有无 Skill 的 A/B：质量、完成时间、成本、返工率。",
        "4. 标记保留 / 修复触发 / 继续观察；不要仅凭调用量自动删除。",
        "", "隐私提示：仅在本机读取；分享报告前自行检查 Skill 名称是否包含私有信息。", "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="只读审计 SKILL.md 与调用日志；零观测 ≠ 零使用。")
    parser.add_argument("--skills-root", action="append", required=True, metavar="DIR", help="包含子目录 SKILL.md 的根目录，可重复")
    parser.add_argument("--claude-log", action="append", default=[], metavar="PATH", help="Claude Hook TSV：timestamp<TAB>event<TAB>skill")
    parser.add_argument("--event-csv", action="append", default=[], metavar="PATH", help="跨执行器 CSV：timestamp,executor,skill")
    parser.add_argument("--expect-executor", action="append", default=[], metavar="NAME", help="本应覆盖的执行器，可重复；缺日志为未知")
    parser.add_argument("--days", type=int, default=30, metavar="N", help="观察窗口（默认 30 天）")
    parser.add_argument("--as-of", metavar="ISO8601", help="指定统计截止（测试或复盘用），默认 UTC 现在")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="输出格式")
    args = parser.parse_args(argv)
    if args.days <= 0:
        parser.error("--days 必须是正整数")
    try:
        data = audit(args)
    except (InputError, ValueError) as error:
        print(f"审计输入错误：{error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
