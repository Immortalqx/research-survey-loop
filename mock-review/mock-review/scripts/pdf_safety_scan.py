#!/usr/bin/env python3
"""PDF artifact scan for mock-review workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    fitz = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


TERMS = re.compile(
    r"(?i)\b("
    r"ignore|instruction|prompt|chatgpt|assistant|system prompt|language model|"
    r"LLM|reviewer|review|accept|reject|score|confidence|confidential|do not|"
    r"disregard|override|you are|rate this|give.*accept|best paper"
    r")\b"
)

ACTIVE_TOKENS = {"/JavaScript", "/JS", "/Launch", "/EmbeddedFile", "/AA", "/OpenAction"}


def scan_pdf(path: Path) -> dict:
    if fitz is None:
        raise RuntimeError(f"PyMuPDF import failed: {IMPORT_ERROR}")

    doc = fitz.open(path)
    item: dict = {
        "file": path.name,
        "pages": doc.page_count,
        "metadata": doc.metadata,
        "needs_pass": bool(doc.needs_pass),
        "embedded_file_count": doc.embfile_count() if hasattr(doc, "embfile_count") else 0,
        "annotations_count": 0,
        "active_content_xrefs": [],
        "open_action_interpretation": [],
        "keyword_hits": [],
        "tiny_text_spans": [],
        "white_text_spans": [],
        "low_alpha_spans": [],
        "verdict": "",
    }

    for xref in range(1, doc.xref_length()):
        try:
            obj = doc.xref_object(xref, compressed=False)
        except Exception:
            continue
        tokens = sorted(set(t for t in re.findall(r"/[A-Za-z]+", obj) if t in ACTIVE_TOKENS))
        if tokens:
            item["active_content_xrefs"].append(
                {"xref": xref, "tokens": tokens, "object_preview": obj[:500]}
            )
            if tokens == ["/OpenAction"]:
                match = re.search(r"/OpenAction\s+(\d+)\s+0\s+R", obj)
                if match:
                    ref = int(match.group(1))
                    try:
                        refobj = doc.xref_object(ref, compressed=False)
                    except Exception as exc:
                        refobj = f"failed to read referenced object: {exc}"
                    item["open_action_interpretation"].append(
                        f"/OpenAction points to xref {ref}: {str(refobj).strip()[:240]}"
                    )

    for page_number, page in enumerate(doc, start=1):
        annot = page.first_annot
        while annot:
            item["annotations_count"] += 1
            annot = annot.next

        text = page.get_text("text")
        for match in TERMS.finditer(text):
            context = text[max(0, match.start() - 110) : match.end() + 150].replace("\n", " ")
            item["keyword_hits"].append(
                {"page": page_number, "term": match.group(0), "context": context}
            )

        raw = page.get_text("rawdict")
        for block in raw.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    chars = span.get("chars", [])
                    span_text = "".join(ch.get("c", "") for ch in chars).strip()
                    if not span_text:
                        continue
                    size = float(span.get("size") or 0)
                    color = span.get("color")
                    alpha = span.get("alpha")
                    bbox = [round(float(v), 2) for v in span.get("bbox", [])]
                    if size and size < 3:
                        item["tiny_text_spans"].append(
                            {
                                "page": page_number,
                                "size": round(size, 2),
                                "color": color,
                                "text": span_text[:160],
                                "bbox": bbox,
                            }
                        )
                    if color == 16777215:
                        item["white_text_spans"].append(
                            {
                                "page": page_number,
                                "size": round(size, 2),
                                "text": span_text[:160],
                                "bbox": bbox,
                            }
                        )
                    if alpha is not None and alpha < 0.5:
                        item["low_alpha_spans"].append(
                            {
                                "page": page_number,
                                "size": round(size, 2),
                                "alpha": alpha,
                                "text": span_text[:160],
                                "bbox": bbox,
                            }
                        )

    suspicious_keywords = []
    for hit in item["keyword_hits"]:
        context = hit["context"].lower()
        if any(
            marker in context
            for marker in [
                "ignore",
                "system prompt",
                "chatgpt",
                "language model",
                "disregard",
                "override",
                "rate this",
                "give accept",
            ]
        ):
            suspicious_keywords.append(hit)

    risky_active = [
        x
        for x in item["active_content_xrefs"]
        if any(t in x["tokens"] for t in ["/JavaScript", "/JS", "/Launch", "/EmbeddedFile", "/AA"])
    ]

    if suspicious_keywords or risky_active or item["embedded_file_count"]:
        item["verdict"] = "Needs human review: suspicious artifact indicators present."
    else:
        item["verdict"] = "No obvious prompt-injection or active-content risk found in automated scan."
    return item


def write_markdown(report: dict, output_path: Path) -> None:
    lines = [
        f"# PDF Artifact Hygiene Scan: {report['file']}",
        "",
        f"- Pages: {report['pages']}",
        f"- Encrypted / needs password: {report['needs_pass']}",
        f"- Embedded files: {report['embedded_file_count']}",
        f"- Annotations: {report['annotations_count']}",
        f"- Active-content token xrefs: {len(report['active_content_xrefs'])}",
        f"- Keyword hits: {len(report['keyword_hits'])}",
        f"- Tiny text spans <3pt: {len(report['tiny_text_spans'])}",
        f"- White text spans: {len(report['white_text_spans'])}",
        f"- Low-alpha spans: {len(report['low_alpha_spans'])}",
        f"- Verdict: {report['verdict']}",
        "",
        "## Active Content / OpenAction",
    ]
    if report["active_content_xrefs"]:
        for entry in report["active_content_xrefs"][:20]:
            preview = entry["object_preview"].replace("\n", " ")[:260]
            lines.append(f"- xref {entry['xref']}: tokens {entry['tokens']}; preview: `{preview}`")
    else:
        lines.append("- None found.")

    if report["open_action_interpretation"]:
        lines.extend(["", "## OpenAction Interpretation"])
        for detail in report["open_action_interpretation"]:
            lines.append(f"- {detail}")

    lines.extend(["", "## Keyword Hits"])
    if report["keyword_hits"]:
        for hit in report["keyword_hits"][:60]:
            lines.append(f"- p{hit['page']} `{hit['term']}`: {hit['context']}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Hidden / Low Visibility Text"])
    hidden = report["tiny_text_spans"] + report["white_text_spans"] + report["low_alpha_spans"]
    if hidden:
        for hit in hidden[:80]:
            lines.append(f"- p{hit['page']} bbox {hit.get('bbox')}: `{hit.get('text')}`")
    else:
        lines.append("- None.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan PDFs for manuscript artifact risks.")
    parser.add_argument("pdfs", nargs="+", help="PDF files to scan.")
    parser.add_argument("--output-dir", default="temp_codex/scans", help="Directory for reports.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    for pdf in args.pdfs:
        path = Path(pdf).expanduser().resolve()
        if not path.exists():
            print(f"PDF not found: {path}", file=sys.stderr)
            return 1
        report = scan_pdf(path)
        reports.append(report)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem)[:90]
        write_markdown(report, output_dir / f"{safe_name}_scan.md")

    (output_dir / "pdf_safety_scan_summary.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            print(f"{report['file']}: {report['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
