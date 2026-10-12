# IngestWitness

IngestWitness is a small, independent **post-ingestion** check for RAG developers. Give it the original text-layer PDF and the JSON chunks your existing pipeline actually exported. It reads the PDF page by page, runs a real local sentence-embedding model, and points to source sentences that may have disappeared before indexing. You keep your own parser, vector store and chat system.

## First run

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/). The model [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) is Apache-2.0 licensed and downloads on first use; inference afterward is local. No paid API or API key is required. For the reproducible synthetic example:

```bash
uv sync --python 3.11 --extra test
uv run python examples/make_sample.py
uv run ingestwitness examples/sample.pdf examples/chunks.json --out report.md --json-out report.json --fail-on-gaps
uv run pytest -q
uv build
```

The example intentionally omits a page-2 deletion-receipt sentence from `chunks.json`, so the `--fail-on-gaps` command **should exit 3** after writing the report. Omit that flag to inspect without a nonzero exit. `report.md` shows page, sentence, nearest actual chunk ID and similarity hint; `report.json` is machine-readable. The fixture is synthetic, not evidence of accuracy on customer PDFs.

For your own pipeline, export a JSON array like `[{"id":"chunk-1","text":"..."}]` from the index or persisted chunk store, then run `ingestwitness original.pdf exported-chunks.json`. Do not supply only prospective chunks if you intend to audit what was truly indexed. This MVP accepts 1–40 pages, 20 MB max, 200 source sentences and 500 chunks so it cannot silently sample a large file.

## What the statuses mean

- `exact_text_present`: normalized source sentence appears literally in at least one exported chunk.
- `semantic_match_review`: no exact text, but a nearby exported chunk scores at least 0.72 cosine similarity. Review whether numbers, negation and table associations survived.
- `possible_missing_text`: no exact text and no high-similarity chunk. It could still be represented by a paraphrase the model missed.
- `unreadable_pages`: PDF text extraction returned no text. This may be blank, scanned or image-only; **coverage is unverified**, not a pass.

The model score and 0.72 threshold are heuristics, not calibrated probabilities or verified recall. It cannot reconstruct tables, OCR images, guarantee that every fact is in the index, or evaluate retrieval and answer quality. Long sentences may be truncated by the embedding model. Use an OCR/layout parser for scanned or complex PDFs and manually inspect flagged source pages.

## Why this narrow product

[PDFstract](https://github.com/aksarav/pdfstract) extracts/chunks/embeds and inspects chunk quality; [RAGPrep](https://ragprep.com/) scores material before chunking; [ragtune](https://github.com/metawake/ragtune) benchmarks retrieval. IngestWitness instead takes **an existing PDF plus the output of any already-run chunking pipeline** and reports source-to-exported-chunk gaps without asking the developer to change the pipeline. This is a testable workflow difference, not a claim that those tools are inferior. See [RESEARCH.md](RESEARCH.md) for demand evidence, counterevidence, and a real-user validation plan.

The code and synthetic fixture are original MIT-licensed work. No competitor code or data was copied. The model is Apache-2.0; `pypdf` and `reportlab` retain their own licenses. User adoption, practical time savings and false-positive/negative rates are not yet validated.
