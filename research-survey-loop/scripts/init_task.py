#!/usr/bin/env python3
"""Initialize or refresh a long-running survey task directory."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    cleaned: list[str] = []
    last_dash = False
    for char in value.strip():
        is_cjk = "\u4e00" <= char <= "\u9fff"
        if char.isalnum() or is_cjk:
            cleaned.append(char.lower())
            last_dash = False
        else:
            if not last_dash and cleaned:
                cleaned.append("-")
                last_dash = True
    slug = "".join(cleaned).strip("-")
    if slug:
        return re.sub(r"-{2,}", "-", slug)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"task-{timestamp}"


def render_template(template_path: Path, replacements: dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def write_file(path: Path, content: str, *, overwrite: bool) -> str:
    if path.exists() and not overwrite:
        return "kept"
    path.write_text(content, encoding="utf-8")
    return "written"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize a survey task directory from bundled templates."
    )
    parser.add_argument("topic", help="Human-readable survey topic.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root where survey_tasks/ will live. Default: current directory.",
    )
    parser.add_argument(
        "--tasks-dir-name",
        default="survey_tasks",
        help="Name of the tasks directory under the workspace root. Default: survey_tasks",
    )
    parser.add_argument(
        "--topic-slug",
        help="Optional explicit slug. Default: derived from topic.",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Overwrite all managed markdown files.",
    )
    parser.add_argument(
        "--force-current-task",
        action="store_true",
        help="Overwrite current_task.md even if it already exists.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    topic_slug = args.topic_slug or slugify(args.topic)
    tasks_root = workspace_root / args.tasks_dir_name
    task_root = tasks_root / topic_slug
    sources_dir = task_root / "sources"
    papers_dir = sources_dir / "papers"
    supplementary_dir = sources_dir / "supplementary"

    for directory in (tasks_root, task_root, sources_dir, papers_dir, supplementary_dir):
        directory.mkdir(parents=True, exist_ok=True)

    created_at = now_iso()
    replacements = {
        "TOPIC": args.topic,
        "TOPIC_SLUG": topic_slug,
        "CREATED_AT": created_at,
        "WORKSPACE_ROOT": str(workspace_root),
        "TASK_DIR": str(task_root),
        "TASK_DIR_REL": str(task_root.relative_to(workspace_root)),
    }

    write_modes = {
        "task.md": args.force_all,
        "round_log.md": args.force_all,
        "survey.md": args.force_all,
        "current_task.md": args.force_all or args.force_current_task,
    }

    templates = {
        "task.md": ASSETS_DIR / "task-template.md",
        "round_log.md": ASSETS_DIR / "round-log-template.md",
        "current_task.md": ASSETS_DIR / "current-task-template.md",
        "survey.md": ASSETS_DIR / "survey-template.md",
    }

    actions: dict[str, str] = {}
    for filename, template_path in templates.items():
        destination = task_root / filename
        content = render_template(template_path, replacements)
        actions[filename] = write_file(destination, content, overwrite=write_modes[filename])

    payload = {
        "topic": args.topic,
        "topic_slug": topic_slug,
        "workspace_root": str(workspace_root),
        "task_root": str(task_root),
        "sources": {
            "papers": str(papers_dir),
            "supplementary": str(supplementary_dir),
        },
        "actions": actions,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
