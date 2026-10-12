# Selection notes — 2026-10-12

This is a demand hypothesis, not a claim about adoption or future stars. Sources were read on 2026-10-12 (Asia/Shanghai).

## Direct evidence across time and channels

1. [Stack Overflow PDF table extraction question](https://stackoverflow.com/questions/78383580/parse-tables-in-pdf-file-when-rag), 2024-04-25: a RAG developer says two libraries flattened technical-table rows and lost parameter associations. Supports upstream ingestion failure; does not prove this MVP can restore tables (it cannot).
2. [Reddit LocalLLaMA RAG user](https://www.reddit.com/r/LocalLLaMA/comments/1ps6txq/rag_that_actually_works/), 2025-12-21: a user says a fact present in a long PDF was not found by a local document chatbot and suspects only part of the source was considered. Supports invisible coverage concern; root cause is not confirmed.
3. [Reddit RAG developer on PDF ingestion](https://www.reddit.com/r/Rag/comments/1q1d00i/reaching_my_wits_end_with_pdf_ingestion/), about 2026-01: repeated attempts with multiple parsers failed on apparently ordinary PDFs. Supports recurring engineering friction; may also point to a need for better extraction rather than an audit.
4. [Reddit postmortem on silent page loss](https://www.reddit.com/r/Rag/comments/1wt97q2/what_broke_in_our_pdf_ingestion_for_rag_silent/), 2026-10: cites a 4,000-page scan with only a small portion indexed while the job reported success. Author works on a document-extraction product, so its numbers are unverified and commercial interest is a caveat.

Stack Overflow plus Reddit provide independent voices across 2024–2026. Community discussion and continued product activity are attention signals, not forecasts for IngestWitness.

## Alternatives and difference

- [PDFstract](https://github.com/aksarav/pdfstract) (Apache-2.0): broad extraction, chunking and embedding pipeline plus chunk inspection. Stronger than this MVP at parsing, but the documented main workflow creates chunks itself rather than auditing an arbitrary existing exported index against original pages.
- [pdf-mcp](https://github.com/jztan/pdf-mcp) and [pdf-rag-mcp](https://github.com/MBaranekTech/pdf-rag-mcp): strong PDF search/OCR/table pipelines; these are substitutes if switching to their entire workflow is acceptable.
- [RAGPrep](https://ragprep.com/): free no-signup chunk-quality checks before embedding; not an arbitrary post-index PDF-to-export comparison in its documented flow.
- [ragtune](https://github.com/metawake/ragtune): retrieval simulation, comparison and CI; valuable when known queries or its own ingestion setup are available.

The intended wedge is stack-agnostic **after-the-fact** comparison with page and actual exported-chunk IDs. It may be unnecessary for teams whose existing stack exposes this diagnostic. It cannot diagnose every reason a RAG answer misses a fact; extraction, chunking, indexing and retrieval are separate stages.

Selection frames only: [Knowledge Work Plugins](https://github.com/anthropics/knowledge-work-plugins) prompted a concrete input-to-review deliverable; [Agency Agents](https://github.com/msitarzewski/agency-agents) prompted competitor and reality checks. No source code, role prompt or data was copied.

## Next test

Ask two RAG maintainers for non-sensitive text-layer PDFs and actual exported chunks from a recent job. Before showing this tool's output, ask them to identify known missing source facts. Compare their labels to the page-level triage, log missed items and spurious flags, and ask whether they would put the report in their pre-release workflow. This validation has not happened.
