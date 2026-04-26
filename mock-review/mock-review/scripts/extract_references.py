#!/usr/bin/env python3
"""Extract a first-pass references matrix from a manuscript PDF or text file."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


def run_pdftotext(pdf_path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", "-raw", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "pdftotext failed").strip()
        raise RuntimeError(message)
    return proc.stdout


def clean_text(value: str) -> str:
    value = value.replace("\u00ad", "")
    value = re.sub(r"(\w)-\s+(\w)", r"\1\2", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_entries(text: str) -> list[str]:
    match = re.search(r"(?im)^\s*(references|bibliography)\s*$", text)
    refs = text[match.end() :] if match else text
    refs = re.sub(r"\n\d{1,4}\n", "\n", refs)

    entries: list[str] = []
    current: list[str] = []
    numbered_pattern = re.compile(r"^\s*\[(\d+)\]\s*(.*)")

    for raw_line in refs.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^\d{1,4}$", line):
            continue
        if re.match(r"(?i)^(references|bibliography)$", line):
            continue
        numbered = numbered_pattern.match(line)
        if numbered:
            if current:
                entries.append(clean_text(" ".join(current)))
            current = [line]
        elif current:
            current.append(line)

    if current:
        entries.append(clean_text(" ".join(current)))
    return entries


def parse_entry(entry: str, index: int) -> dict:
    ref_match = re.match(r"^\[(\d+)\]\s*(.*)", entry)
    if ref_match:
        ref = int(ref_match.group(1))
        body = ref_match.group(2)
    else:
        ref = index
        body = entry

    match = re.match(r"(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+)", body)
    if match:
        authors, year, title, venue = [clean_text(group) for group in match.groups()]
    else:
        match = re.match(r"(.+?)\.\s+(\d{4})\.\s+(.+)", body)
        if match:
            authors, year, title = [clean_text(group) for group in match.groups()]
            venue = ""
        else:
            authors, year, title, venue = "", "", clean_text(body), ""

    return {
        "ref": ref,
        "authors": authors,
        "year": year,
        "title": title,
        "venue_text": venue,
        "category": "",
        "core_read": "",
        "topic_role": "",
        "raw_entry": entry,
    }


def write_outputs(rows: list[dict], output: Path | None, markdown: Path | None, json_path: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    if markdown:
        markdown.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# References Matrix",
            "",
            "| Ref | Year | Title | Venue | Category | Core Read |",
            "|---:|---:|---|---|---|---|",
        ]
        for row in rows:
            title = row["title"].replace("|", "%7C")
            venue = row["venue_text"].replace("|", "%7C")
            lines.append(
                f"| [{row['ref']}] | {row['year']} | {title} | {venue} | {row['category']} | {row['core_read']} |"
            )
        markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract a references matrix from a PDF or text file.")
    parser.add_argument("input", help="PDF or text file.")
    parser.add_argument("--output", help="CSV output path.")
    parser.add_argument("--markdown", help="Markdown output path.")
    parser.add_argument("--json", dest="json_path", help="JSON output path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    try:
        if input_path.suffix.lower() == ".pdf":
            text = run_pdftotext(input_path)
        else:
            text = input_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    entries = extract_entries(text)
    if not entries:
        print("No numbered references found.", file=sys.stderr)
        return 2

    rows = [parse_entry(entry, index + 1) for index, entry in enumerate(entries)]
    rows.sort(key=lambda row: row["ref"])

    write_outputs(
        rows,
        Path(args.output) if args.output else None,
        Path(args.markdown) if args.markdown else None,
        Path(args.json_path) if args.json_path else None,
    )

    print(f"Extracted {len(rows)} references.")
    if not (args.output or args.markdown or args.json_path):
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
