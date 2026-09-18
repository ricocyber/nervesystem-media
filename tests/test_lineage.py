import pytest

from analytics.lineage import SourceSpan, validate_spans


def test_lineage_accepts_ordered_nonoverlapping_spans():
    spans = [
        SourceSpan("src", 1000, 5000, 0, 4000),
        SourceSpan("src", 9000, 12000, 4000, 7000),
    ]
    validate_spans(spans, 7000)


def test_lineage_rejects_output_overlap():
    spans = [
        SourceSpan("src", 0, 1000, 0, 1000),
        SourceSpan("src", 2000, 3000, 900, 1900),
    ]
    with pytest.raises(ValueError):
        validate_spans(spans, 2000)
