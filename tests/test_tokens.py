"""Tests for Token model, TokenKind, and span integrity."""

import pytest

from mytokens.tokens import Token, TokenKind
from mytokens.utils import reconstruct_text, verify_token_spans


def test_token_creation() -> None:
    tok = Token(text="hello", kind=TokenKind.WORD, start=0, end=5)
    assert tok.text == "hello"
    assert tok.kind == TokenKind.WORD
    assert tok.start == 0
    assert tok.end == 5
    assert tok.span == (0, 5)
    assert tok.length == 5
    assert tok.to_dict() == {
        "text": "hello",
        "kind": "word",
        "start": 0,
        "end": 5,
    }


def test_token_immutability() -> None:
    tok = Token(text="test", kind=TokenKind.WORD, start=0, end=4)
    with pytest.raises(AttributeError):
        tok.text = "other"  # type: ignore[misc]


def test_token_invalid_offsets() -> None:
    with pytest.raises(ValueError, match="negative"):
        Token(text="a", kind=TokenKind.WORD, start=-1, end=2)

    with pytest.raises(ValueError, match="cannot precede"):
        Token(text="a", kind=TokenKind.WORD, start=5, end=3)


def test_token_invalid_types() -> None:
    with pytest.raises(TypeError):
        Token(text=123, kind=TokenKind.WORD, start=0, end=3)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        Token(text="a", kind="word", start=0, end=1)  # type: ignore[arg-type]


def test_verify_token_spans_utility() -> None:
    source = "Hello world"
    tokens = [
        Token("Hello", TokenKind.WORD, 0, 5),
        Token("world", TokenKind.WORD, 6, 11),
    ]
    assert verify_token_spans(source, tokens) is True


def test_verify_token_spans_mismatch() -> None:
    source = "Hello world"
    tokens = [
        Token("Hello", TokenKind.WORD, 0, 5),
        Token("Earth", TokenKind.WORD, 6, 11),  # text mismatch with source[6:11]
    ]
    assert verify_token_spans(source, tokens) is False


def test_reconstruct_text() -> None:
    source = "Hello   world!"
    tokens = [
        Token("Hello", TokenKind.WORD, 0, 5),
        Token("   ", TokenKind.WHITESPACE, 5, 8),
        Token("world", TokenKind.WORD, 8, 13),
        Token("!", TokenKind.PUNCTUATION, 13, 14),
    ]
    assert reconstruct_text(tokens) == source
