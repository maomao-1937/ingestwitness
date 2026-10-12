from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from ingestwitness.cli import markdown
from ingestwitness.core import audit, extract_pdf, source_units, validate_chunks


class FakeEmbedder:
    def matrix(self, source_units, chunk_texts):
        return [[1.0 if text in chunk else 0.1 for chunk in chunk_texts] for text in source_units]


def test_pdf_extracts_pages(tmp_path: Path):
    path = tmp_path / "sample.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(40, 700, "The refund window lasts for thirty days after purchase.")
    pdf.showPage()
    pdf.showPage()
    pdf.save()
    pages = extract_pdf(path)
    assert len(pages) == 2
    assert "refund" in pages[0]["text"]
    assert source_units(pages)[1] == [2]


def test_missing_and_exact_text():
    pages = [{"page": 1, "text": "The refund window lasts for thirty days after purchase. Signed deletion receipts must be requested by enterprise customers."}]
    chunks = validate_chunks([{"id": "a", "text": "The refund window lasts for thirty days after purchase."}])
    report = audit(pages, chunks, FakeEmbedder())
    assert [item["status"] for item in report["units"]] == ["exact_text_present", "possible_missing_text"]
    assert report["units"][1]["page"] == 1
    assert "Possible missing" in markdown(report)


def test_unreadable_page_is_not_called_covered():
    report = audit([{"page": 1, "text": ""}], [{"id": "a", "text": "anything"}], FakeEmbedder())
    assert report["unreadable_pages"] == [1]
    assert report["model"] == "not_run_no_extractable_source_units"


def test_short_source_text_is_not_silently_omitted():
    units, unreadable = source_units([{"page": 1, "text": "No refunds."}])
    assert units == [{"page": 1, "text": "No refunds."}]
    assert unreadable == []


def test_duplicate_chunk_id_rejected():
    with pytest.raises(ValueError, match="Duplicate chunk id"):
        validate_chunks([{"id": "a", "text": "x"}, {"id": "a", "text": "y"}])


def test_empty_chunk_export_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        validate_chunks([])


def test_matrix_shape_checked():
    class Broken:
        def matrix(self, source_units, chunk_texts):
            return []

    with pytest.raises(RuntimeError, match="shape"):
        audit([{"page": 1, "text": "This source sentence is long enough for the audit."}], [{"id": "x", "text": "chunk"}], Broken())
