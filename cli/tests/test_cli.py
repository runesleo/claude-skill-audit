"""End-to-end behavior tests for the read-only skill audit CLI."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-12T00:00:00Z"


def epoch(day: int) -> int:
    return int(datetime(2026, 11, day, tzinfo=timezone.utc).timestamp())


class SkillAuditCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.skills_root = self.workspace / "skills"
        self.skills_root.mkdir()

    def add_skill(self, name: str) -> None:
        folder = self.skills_root / name
        folder.mkdir()
        (folder / "SKILL.md").write_text("# Example skill\n", encoding="utf-8")

    def invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "skill_audit.py"),
             "--skills-root", str(self.skills_root),
             "--as-of", AS_OF, *args],
            capture_output=True, text=True, check=False,
        )

    def test_mixed_executor_logs_count_observations_without_claiming_complete_coverage(self) -> None:
        """A valid event in each adapter must be counted, never presented as full usage."""
        self.add_skill("research")
        self.add_skill("writer")
        claude = self.workspace / "claude.log"
        claude.write_text(
            f"{epoch(10)}\tSkill\tresearch\n"
            f"{epoch(11)}\tSkill\tresearch\n", encoding="utf-8",
        )
        other = self.workspace / "other.csv"
        with other.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["timestamp", "executor", "skill"])
            writer.writerow(["2026-11-11T12:00:00Z", "Codex", "writer"])

        result = self.invoke(
            "--claude-log", str(claude), "--event-csv", str(other),
            "--expect-executor", "Claude", "--expect-executor", "Codex",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        skills = {item["name"]: item for item in data["skills"]}
        self.assertEqual(data["observed_calls"], 3)
        self.assertEqual(skills["research"]["by_executor"], {"Claude": 2, "Codex": 0})
        self.assertEqual(skills["writer"]["by_executor"], {"Claude": 0, "Codex": 1})
        self.assertEqual(data["executors"]["Codex"]["status"], "log_supplied")
        self.assertFalse(data["coverage_verified"])

    def test_missing_executor_stays_unknown_not_zero(self) -> None:
        """A missing source cannot turn a skill into a verified zero-use skill."""
        self.add_skill("rare-protection")
        claude = self.workspace / "claude.log"
        claude.write_text("", encoding="utf-8")

        result = self.invoke(
            "--claude-log", str(claude),
            "--expect-executor", "Claude", "--expect-executor", "Codex",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        skill = data["skills"][0]
        self.assertEqual(skill["by_executor"]["Claude"], 0)
        self.assertIsNone(skill["by_executor"]["Codex"])
        self.assertEqual(data["executors"]["Codex"]["status"], "unknown")
        self.assertEqual(data["executors"]["Claude"]["status"], "log_supplied")
        self.assertNotIn("safe_to_delete", json.dumps(data))

    def test_dates_malformed_rows_and_unmatched_events_are_counted_honestly(self) -> None:
        """Only in-window valid events for inventoried skills add to the total."""
        self.add_skill("audit")
        claude = self.workspace / "claude.log"
        claude.write_text(
            f"{epoch(10)}\tSkill\taudit\n"
            f"{epoch(10)}\tSkill\tnot-installed\n"
            f"{epoch(1)}\tSkill\taudit\n"  # in range (30 days)
            f"{epoch(10)}\tbroken\n"
            "garbage\tSkill\taudit\n"
            f"{epoch(12) + 60}\tSkill\taudit\n",  # future
            encoding="utf-8",
        )
        result = self.invoke("--claude-log", str(claude), "--days", "5", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["observed_calls"], 1)
        self.assertEqual(data["unmatched_events"], 1)
        self.assertEqual(data["invalid_rows"], 2)

    def test_markdown_does_not_expose_input_paths_or_confuse_missing_logs_with_zero(self) -> None:
        """Published excerpts must not leak local paths or present missing data as zero."""
        self.add_skill("task|helper")
        claude = self.workspace / "private-name.log"
        claude.write_text(f"{epoch(10)}\tSkill\ttask|helper\n", encoding="utf-8")
        result = self.invoke(
            "--claude-log", str(claude), "--expect-executor", "Codex",
            "--format", "markdown",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("task\\|helper", result.stdout)
        self.assertIn("未知", result.stdout)
        self.assertNotIn(str(self.workspace), result.stdout)
        self.assertNotIn("private-name.log", result.stdout)
        self.assertIn("不等于真实零调用", result.stdout)

    def test_unreadable_requested_log_fails_instead_of_silently_reporting_zero(self) -> None:
        """An invalid log path must fail closed, not produce an empty clean audit."""
        self.add_skill("test")
        result = self.invoke("--claude-log", str(self.workspace / "missing.log"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("无法读取", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_skills_installed_as_directory_symlinks_are_inventoried(self) -> None:
        """Linked installations must not disappear from a user's Skill inventory."""
        original = self.workspace / "shared" / "linked-tool"
        original.mkdir(parents=True)
        (original / "SKILL.md").write_text("# Linked skill\n", encoding="utf-8")
        (self.skills_root / "linked-tool").symlink_to(original, target_is_directory=True)
        result = self.invoke("--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["skills_detected"], 1)
        self.assertEqual(data["skills"][0]["name"], "linked-tool")


if __name__ == "__main__":
    unittest.main()
