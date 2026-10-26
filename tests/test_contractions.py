"""Tests for contraction splitting and preservation."""

from mytokens import tokenize
from mytokens.utils import verify_token_spans


def test_contractions_preserved_by_default() -> None:
    text = "I'm sure they don't know we're here and can't come."
    tokens = tokenize(text)
    assert "I'm" in tokens
    assert "don't" in tokens
    assert "we're" in tokens
    assert "can't" in tokens


def test_contractions_split_enabled() -> None:
    text = "I'm don't can't we're"
    tokens = tokenize(text, split_contractions=True)
    assert tokens == ["I", "'m", "do", "n't", "ca", "n't", "we", "'re"]


def test_various_negative_contractions() -> None:
    text = "won't isn't aren't wouldn't"
    tokens = tokenize(text, split_contractions=True)
    assert tokens == ["wo", "n't", "is", "n't", "are", "n't", "would", "n't"]


def test_contractions_curly_apostrophes() -> None:
    text = "I’m sure they don’t mind."
    tokens = tokenize(text, split_contractions=True)
    assert tokens == ["I", "’m", "sure", "they", "do", "n’t", "mind", "."]


def test_contractions_span_integrity() -> None:
    text = "I'm sure we don't think they'll lose."
    tokens = tokenize(text, split_contractions=True, detailed=True)
    assert verify_token_spans(text, tokens) is True
