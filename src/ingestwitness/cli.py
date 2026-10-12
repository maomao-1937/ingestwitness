"""Compare a PDF's readable source text with actual exported RAG chunks."""

import argparse
import json
import sys
from pathlib import Path

from .core import audit, extract_pdf, validate_chunks
from .model import LocalEmbedder


def markdown(report: dict) -> str:
    lines = ["# IngestWitness report", "", report["warning"], "", f"Model: `{report['model']}`", ""]
    if report["unreadable_pages"]:
        lines += ["## Unverified pages", "", "No extractable text on PDF pages: " + ", ".join(map(str, report["unreadable_pages"])), ""]
    for status, heading in [("possible_missing_text", "Possible missing source text"), ("semantic_match_review", "Semantic matches needing review"), ("exact_text_present", "Exact source text found")]:
        lines += [f"## {heading}", ""]
        matches = [item for item in report["units"] if item["status"] == status]
        if not matches:
            lines.append("- None")
        for item in matches:
            lines.append(f"- PDF page {item['page']} → nearest exported chunk `{item['nearest_chunk_id']}` (cosine similarity hint {item['nearest_similarity']:.3f})")
            lines.append(f"  - Source: {item['source_text'][:260]}")
            if item["exact_chunk_id"]:
                lines.append(f"  - Exact text in chunk `{item['exact_chunk_id']}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit text-layer PDF source coverage in exported RAG chunks with local semantic AI")
    parser.add_argument("source", type=Path, help="Original text-layer PDF")
    parser.add_argument("chunks", type=Path, help="JSON array of {id,text} exported from your own index")
    parser.add_argument("--out", type=Path, default=Path("report.md"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--fail-on-gaps", action="store_true", help="Exit 3 if any possible missing text or unreadable page")
    args = parser.parse_args(argv)
    try:
        pages = extract_pdf(args.source)
        chunks = validate_chunks(json.loads(args.chunks.read_text(encoding="utf-8")))
        report = audit(pages, chunks, LocalEmbedder())
        args.out.write_text(markdown(report), encoding="utf-8")
        if args.json_out:
            args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        print(f"IngestWitness error: {exc}", file=sys.stderr)
        return 2
    missing = sum(unit["status"] == "possible_missing_text" for unit in report["units"])
    print(f"Wrote {args.out}: {len(report['units'])} source units; {missing} possible gaps; {len(report['unreadable_pages'])} unverified pages")
    return 3 if args.fail_on_gaps and (missing or report["unreadable_pages"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
