"""Read-only, provenance-preserving comparison of original pages and exported chunks."""

import re
from pathlib import Path
from typing import Any, Protocol


class Embedder(Protocol):
    def matrix(self, source_units: list[str], chunk_texts: list[str]) -> list[list[float]]: ...


def extract_pdf(path: Path) -> list[dict[str, Any]]:
    from pypdf import PdfReader

    if path.suffix.lower() != ".pdf":
        raise ValueError("Source must be a PDF file")
    if not path.is_file():
        raise ValueError(f"PDF does not exist: {path}")
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("MVP limit: PDF must be 20 MB or smaller")
    reader = PdfReader(str(path))
    if len(reader.pages) == 0 or len(reader.pages) > 40:
        raise ValueError("MVP limit: PDF must have 1-40 pages")
    return [{"page": index + 1, "text": page.extract_text() or ""} for index, page in enumerate(reader.pages)]


def validate_chunks(data: Any) -> list[dict[str, str]]:
    if not isinstance(data, list) or not data or len(data) > 500:
        raise ValueError("Chunk export must be a non-empty JSON array of at most 500 objects")
    chunks = []
    seen = set()
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Chunk {index} must be an object")
        cid = item.get("id")
        content = item.get("text")
        if not isinstance(cid, str) or not cid.strip() or not isinstance(content, str) or not content.strip():
            raise ValueError(f"Chunk {index} requires non-empty string id and text")
        if cid in seen:
            raise ValueError(f"Duplicate chunk id: {cid}")
        seen.add(cid)
        chunks.append({"id": cid, "text": content.strip()})
    return chunks


def source_units(pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[int]]:
    units = []
    unreadable_pages = []
    for page in pages:
        text = " ".join(page["text"].split())
        if not text:
            unreadable_pages.append(page["page"])
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip()
            if sentence:
                units.append({"page": page["page"], "text": sentence})
    if len(units) > 200:
        raise ValueError("MVP limit: PDF has more than 200 text units; split the file")
    return units, unreadable_pages


def _flat(text: str) -> str:
    return " ".join(text.lower().split())


def audit(pages: list[dict[str, Any]], chunks: list[dict[str, str]], model: Embedder) -> dict[str, Any]:
    units, unreadable_pages = source_units(pages)
    if not units:
        return {"model": "not_run_no_extractable_source_units", "units": [], "unreadable_pages": unreadable_pages, "warning": "No source text was extractable. Coverage is unverified; try OCR or another parser."}
    matrix = model.matrix([unit["text"] for unit in units], [chunk["text"] for chunk in chunks])
    if len(matrix) != len(units) or any(len(row) != len(chunks) for row in matrix):
        raise RuntimeError("Embedding model returned an unexpected similarity matrix shape")
    findings = []
    for unit, scores in zip(units, matrix, strict=True):
        closest_index = max(range(len(chunks)), key=lambda index: scores[index])
        closest = chunks[closest_index]
        exact_id = next((chunk["id"] for chunk in chunks if _flat(unit["text"]) in _flat(chunk["text"])), None)
        semantic = float(scores[closest_index])
        if exact_id is not None:
            status = "exact_text_present"
        elif semantic >= 0.72:
            status = "semantic_match_review"
        else:
            status = "possible_missing_text"
        findings.append({"page": unit["page"], "source_text": unit["text"], "status": status, "exact_chunk_id": exact_id, "nearest_chunk_id": closest["id"], "nearest_similarity": round(semantic, 4)})
    return {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "units": findings,
        "unreadable_pages": unreadable_pages,
        "warning": "This is a text-layer, source-to-exported-chunks triage. Similarity is not a calibrated coverage probability; a semantic match does not prove exact facts or table relationships survived. Blank/scanned pages are unverified, not covered.",
    }
