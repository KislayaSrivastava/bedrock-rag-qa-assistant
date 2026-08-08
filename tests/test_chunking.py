from src.chunking import chunk_text


def test_short_text_returns_single_chunk():
    text = "This is a short paragraph that fits in one chunk."
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0].text == text


def test_long_text_splits_into_multiple_chunks():
    paragraph = "Sentence one. Sentence two. Sentence three. Sentence four. " * 20
    chunks = chunk_text(paragraph, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c.text) <= 220 for c in chunks)  # allows for overlap prefix


def test_chunk_overlap_must_be_smaller_than_chunk_size():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, chunk_overlap=100)


def test_paragraph_boundaries_are_respected_when_possible():
    text = "Paragraph one is short.\n\nParagraph two is also short."
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=0)
    assert len(chunks) == 1
    assert "Paragraph one" in chunks[0].text
    assert "Paragraph two" in chunks[0].text
