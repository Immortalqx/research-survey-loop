#!/usr/bin/env python3
"""Search, download, and move survey sources into a task-local directory."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
CODEX_HOME = Path(os.getenv("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
SKILLS_HOME = CODEX_HOME / "skills"
ARXIV_SCRIPT = SKILLS_HOME / "arxiv" / "arxiv_fetch.py"
SEMANTIC_SCRIPT = SKILLS_HOME / "semantic-scholar" / "semantic_scholar_fetch.py"
EXA_SCRIPT = SKILLS_HOME / "exa-search" / "exa_search.py"

DOMAIN_GROUPS: dict[str, list[str]] = {
    "nature-science": ["nature.com", "science.org"],
    "cv": ["openaccess.thecvf.com", "ieeexplore.ieee.org", "springer.com"],
    "robotics": ["science.org", "journals.sagepub.com", "roboticsconference.org", "proceedings.mlr.press"],
}

USER_AGENT = "research-survey-loop/1.0"


def run_json_command(args: list[str]) -> Any:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "command failed").strip()
        raise RuntimeError(message)
    return json.loads(proc.stdout)


def now_stamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def ensure_task_dirs(task_dir: Path) -> tuple[Path, Path]:
    papers_dir = task_dir / "sources" / "papers"
    supplementary_dir = task_dir / "sources" / "supplementary"
    papers_dir.mkdir(parents=True, exist_ok=True)
    supplementary_dir.mkdir(parents=True, exist_ok=True)
    return papers_dir, supplementary_dir


def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    lowered = value.casefold()
    lowered = re.sub(r"\s+", " ", lowered)
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", lowered)


def safe_filename(value: str, suffix: str = "") -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "-", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned[:180].strip(" .")
    if not cleaned:
        cleaned = f"source-{now_stamp()}"
    return cleaned + suffix


def unique_destination(dest_dir: Path, filename: str) -> Path:
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        next_candidate = dest_dir / f"{stem}-{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1


def normalize_arxiv_results(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in payload:
        rows.append(
            {
                "priority_bucket": "arxiv",
                "source": "arxiv",
                "title": item.get("title"),
                "year": (item.get("published") or "")[:4] or None,
                "venue": "arXiv",
                "authors": item.get("authors") or [],
                "url": item.get("abs_url"),
                "pdf_url": item.get("pdf_url"),
                "arxiv_id": item.get("id"),
                "doi": None,
            }
        )
    return rows


def normalize_semantic_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in payload.get("data", []):
        external_ids = item.get("externalIds") or {}
        open_access_pdf = item.get("openAccessPdf") or {}
        publication_venue = item.get("publicationVenue") or {}
        rows.append(
            {
                "priority_bucket": "semantic-scholar",
                "source": "semantic-scholar",
                "title": item.get("title"),
                "year": item.get("year"),
                "venue": publication_venue.get("name") or item.get("venue"),
                "authors": [author.get("name") for author in item.get("authors", []) if author.get("name")],
                "url": item.get("url"),
                "pdf_url": open_access_pdf.get("url"),
                "arxiv_id": external_ids.get("ArXiv"),
                "doi": external_ids.get("DOI"),
                "semantic_paper_id": item.get("paperId"),
                "citation_count": item.get("citationCount"),
            }
        )
    return rows


def normalize_exa_results(group: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in payload.get("data", []):
        rows.append(
            {
                "priority_bucket": group,
                "source": "exa",
                "title": item.get("title"),
                "year": (item.get("published_date") or "")[:4] or None,
                "venue": None,
                "authors": [item.get("author")] if item.get("author") else [],
                "url": item.get("url"),
                "pdf_url": item.get("url") if str(item.get("url", "")).lower().endswith(".pdf") else None,
                "arxiv_id": None,
                "doi": None,
            }
        )
    return rows


def dedupe_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for row in rows:
        key_candidates = [
            f"doi:{row.get('doi')}" if row.get("doi") else "",
            f"arxiv:{row.get('arxiv_id')}" if row.get("arxiv_id") else "",
            f"url:{row.get('url')}" if row.get("url") else "",
            f"title:{normalize_title(row.get('title'))}" if row.get("title") else "",
        ]
        key = next((candidate for candidate in key_candidates if candidate), "")
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        kept.append(row)
    return kept


def search_exa(query: str, max_per_source: int, groups: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    if not EXA_SCRIPT.exists():
        warnings.append("Exa helper script not found; skipped publisher-priority search.")
        return [], warnings
    if not os.getenv("EXA_API_KEY", "").strip():
        warnings.append("EXA_API_KEY not set; skipped publisher-priority Exa search.")
        return [], warnings

    results: list[dict[str, Any]] = []
    for group in groups:
        domains = DOMAIN_GROUPS.get(group)
        if not domains:
            warnings.append(f"Unknown Exa domain group '{group}'; skipped.")
            continue
        try:
            payload = run_json_command(
                [
                    sys.executable,
                    str(EXA_SCRIPT),
                    "search",
                    query,
                    "--max",
                    str(max_per_source),
                    "--category",
                    "research paper",
                    "--content",
                    "none",
                    "--include-domains",
                    ",".join(domains),
                ]
            )
        except RuntimeError as exc:
            warnings.append(f"Exa search failed for {group}: {exc}")
            continue
        results.extend(normalize_exa_results(group, payload))
    return results, warnings


def search_semantic(query: str, max_per_source: int) -> tuple[list[dict[str, Any]], list[str]]:
    if not SEMANTIC_SCRIPT.exists():
        return [], ["Semantic Scholar helper script not found; skipped published-venue search."]
    try:
        payload = run_json_command(
            [
                sys.executable,
                str(SEMANTIC_SCRIPT),
                "search",
                query,
                "--max",
                str(max_per_source),
                "--fields-of-study",
                "Computer Science,Engineering",
                "--publication-types",
                "JournalArticle,Conference",
            ]
        )
    except RuntimeError as exc:
        return [], [f"Semantic Scholar search failed: {exc}"]
    return normalize_semantic_results(payload), []


def search_arxiv(query: str, max_per_source: int) -> tuple[list[dict[str, Any]], list[str]]:
    if not ARXIV_SCRIPT.exists():
        return [], ["arXiv helper script not found; skipped arXiv search."]
    try:
        payload = run_json_command(
            [
                sys.executable,
                str(ARXIV_SCRIPT),
                "search",
                query,
                "--max",
                str(max_per_source),
            ]
        )
    except RuntimeError as exc:
        return [], [f"arXiv search failed: {exc}"]
    return normalize_arxiv_results(payload), []


def download_arxiv(arxiv_id: str, dest_dir: Path) -> dict[str, Any]:
    payload = run_json_command(
        [
            sys.executable,
            str(ARXIV_SCRIPT),
            "download",
            arxiv_id,
            "--dir",
            str(dest_dir),
        ]
    )
    return {
        "action": "downloaded" if not payload.get("skipped") else "skipped-existing",
        "source": "arxiv",
        "path": payload.get("path"),
        "id": payload.get("id"),
    }


def direct_download(url: str, dest_dir: Path, title: str | None = None, *, allow_html: bool = False) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        headers = response.headers
        content_type = headers.get_content_type()
        final_url = response.geturl()

    parsed = urllib.parse.urlparse(final_url)
    raw_name = Path(parsed.path).name
    suffix = Path(raw_name).suffix.lower()
    is_pdf = content_type == "application/pdf" or suffix == ".pdf"
    is_html = content_type in {"text/html", "application/xhtml+xml"}

    if is_html and not allow_html:
        return {
            "action": "kept-url-only",
            "source": "url",
            "url": final_url,
            "reason": f"Refused to save HTML without --allow-html ({content_type})",
        }

    if not suffix:
        suffix = ".pdf" if is_pdf else ".html" if is_html else ".bin"

    filename_seed = title or Path(raw_name).stem or "downloaded-source"
    destination = unique_destination(dest_dir, safe_filename(filename_seed, suffix))
    destination.write_bytes(data)

    return {
        "action": "downloaded",
        "source": "url",
        "url": final_url,
        "path": str(destination),
        "content_type": content_type,
    }


def import_local(paths: list[str], task_dir: Path, *, mode: str) -> list[dict[str, Any]]:
    papers_dir, _ = ensure_task_dirs(task_dir)
    actions = []
    for raw_path in paths:
        source = Path(raw_path).expanduser().resolve()
        if not source.exists():
            actions.append({"action": "missing", "source": str(source)})
            continue
        destination = unique_destination(papers_dir, safe_filename(source.stem, source.suffix))
        if mode == "move":
            shutil.move(str(source), str(destination))
        else:
            shutil.copy2(source, destination)
        actions.append(
            {
                "action": mode,
                "source": str(source),
                "destination": str(destination),
                "relative_destination": str(destination.relative_to(task_dir)),
            }
        )
    return actions


def reuse_task_paper(paths: list[str], from_task: Path, task_dir: Path) -> list[dict[str, Any]]:
    papers_dir, _ = ensure_task_dirs(task_dir)
    actions = []
    for raw_path in paths:
        source = Path(raw_path)
        source = source if source.is_absolute() else (from_task / source)
        source = source.expanduser().resolve()
        if not source.exists():
            actions.append({"action": "missing", "source": str(source)})
            continue
        destination = unique_destination(papers_dir, safe_filename(source.stem, source.suffix))
        shutil.copy2(source, destination)
        actions.append(
            {
                "action": "copied",
                "source": str(source),
                "destination": str(destination),
                "relative_destination": str(destination.relative_to(task_dir)),
            }
        )
    return actions


def save_json_if_requested(payload: dict[str, Any], save_json: str | None) -> None:
    if not save_json:
        return
    destination = Path(save_json).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search, download, and organize survey sources for a research survey task."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search web-first sources and print normalized JSON.")
    search.add_argument("query")
    search.add_argument("--task-dir", required=True)
    search.add_argument("--max-per-source", type=int, default=5)
    search.add_argument(
        "--domain-groups",
        default="nature-science,cv,robotics",
        help="Comma-separated Exa domain groups. Default: nature-science,cv,robotics",
    )
    search.add_argument("--skip-exa", action="store_true")
    search.add_argument("--skip-semantic", action="store_true")
    search.add_argument("--skip-arxiv", action="store_true")
    search.add_argument(
        "--download-top",
        type=int,
        default=0,
        help="Download the first N results that expose a direct PDF or arXiv ID.",
    )
    search.add_argument("--save-json", help="Optional path to persist the normalized search payload.")

    download = subparsers.add_parser("download", help="Download one source into the task directory.")
    download.add_argument("--task-dir", required=True)
    target = download.add_mutually_exclusive_group(required=True)
    target.add_argument("--arxiv-id")
    target.add_argument("--url")
    target.add_argument("--semantic-id")
    download.add_argument("--title", help="Optional title used to build a local filename.")
    download.add_argument("--allow-html", action="store_true")

    import_local_cmd = subparsers.add_parser("import-local", help="Move or copy local PDFs into task-local sources/papers.")
    import_local_cmd.add_argument("--task-dir", required=True)
    import_local_cmd.add_argument("paths", nargs="+")
    import_local_cmd.add_argument("--mode", choices=("move", "copy"), default="move")

    reuse_cmd = subparsers.add_parser("reuse-task-paper", help="Copy one or more papers from another task into this task.")
    reuse_cmd.add_argument("--task-dir", required=True)
    reuse_cmd.add_argument("--from-task", required=True)
    reuse_cmd.add_argument("paths", nargs="+")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "search":
        task_dir = Path(args.task_dir).expanduser().resolve()
        papers_dir, supplementary_dir = ensure_task_dirs(task_dir)
        domain_groups = [item.strip() for item in args.domain_groups.split(",") if item.strip()]

        rows: list[dict[str, Any]] = []
        warnings: list[str] = []

        if not args.skip_exa:
            exa_rows, exa_warnings = search_exa(args.query, args.max_per_source, domain_groups)
            rows.extend(exa_rows)
            warnings.extend(exa_warnings)
        if not args.skip_semantic:
            semantic_rows, semantic_warnings = search_semantic(args.query, args.max_per_source)
            rows.extend(semantic_rows)
            warnings.extend(semantic_warnings)
        if not args.skip_arxiv:
            arxiv_rows, arxiv_warnings = search_arxiv(args.query, args.max_per_source)
            rows.extend(arxiv_rows)
            warnings.extend(arxiv_warnings)

        deduped = dedupe_results(rows)
        downloads: list[dict[str, Any]] = []
        if args.download_top > 0:
            remaining = args.download_top
            for row in deduped:
                if remaining <= 0:
                    break
                try:
                    if row.get("arxiv_id"):
                        downloads.append(download_arxiv(row["arxiv_id"], papers_dir))
                        remaining -= 1
                    elif row.get("pdf_url"):
                        downloads.append(
                            direct_download(
                                row["pdf_url"],
                                papers_dir,
                                title=row.get("title"),
                            )
                        )
                        remaining -= 1
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"Download failed for {row.get('title')}: {exc}")

        payload = {
            "query": args.query,
            "task_dir": str(task_dir),
            "search_time": now_stamp(),
            "papers_dir": str(papers_dir),
            "supplementary_dir": str(supplementary_dir),
            "warnings": warnings,
            "downloads": downloads,
            "results": deduped,
        }
        save_json_if_requested(payload, args.save_json)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "download":
        task_dir = Path(args.task_dir).expanduser().resolve()
        papers_dir, supplementary_dir = ensure_task_dirs(task_dir)

        try:
            if args.arxiv_id:
                payload = download_arxiv(args.arxiv_id, papers_dir)
            elif args.semantic_id:
                paper = run_json_command(
                    [
                        sys.executable,
                        str(SEMANTIC_SCRIPT),
                        "paper",
                        args.semantic_id,
                    ]
                )
                pdf_info = paper.get("openAccessPdf") or {}
                if pdf_info.get("url"):
                    payload = direct_download(pdf_info["url"], papers_dir, title=paper.get("title"))
                    payload["semantic_id"] = args.semantic_id
                else:
                    payload = {
                        "action": "kept-url-only",
                        "source": "semantic-scholar",
                        "semantic_id": args.semantic_id,
                        "url": paper.get("url"),
                        "reason": "No open-access PDF URL available",
                    }
            else:
                destination_dir = papers_dir if str(args.url).lower().endswith(".pdf") else supplementary_dir
                payload = direct_download(
                    args.url,
                    destination_dir,
                    title=args.title,
                    allow_html=args.allow_html,
                )
        except Exception as exc:  # noqa: BLE001
            print(str(exc), file=sys.stderr)
            return 1

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "import-local":
        task_dir = Path(args.task_dir).expanduser().resolve()
        payload = {
            "task_dir": str(task_dir),
            "actions": import_local(args.paths, task_dir, mode=args.mode),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "reuse-task-paper":
        task_dir = Path(args.task_dir).expanduser().resolve()
        from_task = Path(args.from_task).expanduser().resolve()
        payload = {
            "task_dir": str(task_dir),
            "from_task": str(from_task),
            "actions": reuse_task_paper(args.paths, from_task, task_dir),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"Unsupported command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
