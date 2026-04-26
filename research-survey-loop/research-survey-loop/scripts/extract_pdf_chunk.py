#!/usr/bin/env python3
"""Extract a bounded page chunk from a PDF as plain text."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_MAX_PAGES = 10


def run_command(args: list[str]) -> str:
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
    return proc.stdout


def get_total_pages(pdf_path: Path) -> int:
    output = run_command(["pdfinfo", str(pdf_path)])
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Could not determine PDF page count via pdfinfo")
    return int(match.group(1))


def extract_text(pdf_path: Path, start_page: int, end_page: int) -> str:
    return run_command(
        [
            "pdftotext",
            "-layout",
            "-nopgbrk",
            "-f",
            str(start_page),
            "-l",
            str(end_page),
            str(pdf_path),
            "-",
        ]
    ).strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract at most 10 pages from a PDF for chunked reading."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file.")
    parser.add_argument("--start-page", required=True, type=int, help="1-based start page.")
    parser.add_argument("--end-page", required=True, type=int, help="1-based end page.")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help="Maximum allowed pages per extraction. Default: 10.",
    )
    parser.add_argument(
        "--output",
        help="Optional output text file. If omitted, print to stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON containing metadata plus extracted text.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    if args.start_page < 1 or args.end_page < args.start_page:
        print("Invalid page range", file=sys.stderr)
        return 1

    requested_pages = args.end_page - args.start_page + 1
    if requested_pages > args.max_pages:
        print(
            f"Requested {requested_pages} pages, which exceeds the limit of {args.max_pages}",
            file=sys.stderr,
        )
        return 1

    try:
        total_pages = get_total_pages(pdf_path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.end_page > total_pages:
        print(
            f"Requested end page {args.end_page} exceeds total pages {total_pages}",
            file=sys.stderr,
        )
        return 1

    try:
        text = extract_text(pdf_path, args.start_page, args.end_page)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    next_start = args.end_page + 1 if args.end_page < total_pages else None
    next_end = None
    if next_start is not None:
        next_end = min(total_pages, next_start + args.max_pages - 1)

    payload = {
        "pdf_path": str(pdf_path),
        "start_page": args.start_page,
        "end_page": args.end_page,
        "pages_extracted": requested_pages,
        "total_pages": total_pages,
        "next_window": None
        if next_start is None
        else {"start_page": next_start, "end_page": next_end},
        "text": text,
    }

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
