"""Tests for URL detection and boundary handling."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_basic_url() -> None:
    text = "Visit https://example.com today"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == ["Visit", "https://example.com", "today"]
    assert tokens[1].kind == TokenKind.URL
    assert verify_token_spans(text, tokens) is True


def test_url_with_query_and_params() -> None:
    text = "API endpoint: https://api.example.com/v1/search?q=nlp&limit=10#results"
    tokens = tokenize(text, detailed=True)
    assert tokens[2].text == ":"
    url_tok = tokens[3]
    assert url_tok.text == "https://api.example.com/v1/search?q=nlp&limit=10#results"
    assert url_tok.kind == TokenKind.URL
    assert verify_token_spans(text, tokens) is True


def test_url_with_trailing_punctuation() -> None:
    text = "Check out https://example.com/test?q=1. Is it good?"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == [
        "Check",
        "out",
        "https://example.com/test?q=1",
        ".",
        "Is",
        "it",
        "good",
        "?",
    ]
    assert tokens[2].kind == TokenKind.URL
    assert tokens[3].kind == TokenKind.PUNCTUATION
    assert verify_token_spans(text, tokens) is True


def test_url_recognition_disabled() -> None:
    text = "Visit https://example.com now"
    tokens = tokenize(text, recognize_urls=False)
    assert "https" in tokens
    assert ":" in tokens
