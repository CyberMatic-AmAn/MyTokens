"""Tests for basic tokenization functionality and invariants."""

import pytest

from mytokens import Token, TokenKind, Tokenizer, tokenize
from mytokens.exceptions import InvalidInputError
from mytokens.utils import verify_token_spans


def test_basic_hello_world() -> None:
    text = "Hello world"
    assert tokenize(text) == ["Hello", "world"]


def test_empty_string() -> None:
    assert tokenize("") == []


def test_only_whitespace() -> None:
    assert tokenize("   \t\n  ") == []
    assert len(tokenize("   \t\n  ", preserve_whitespace=True)) == 1


def test_whitespace_preservation() -> None:
    text = "Hello   world"
    tokens = tokenize(text, preserve_whitespace=True, detailed=True)
    assert len(tokens) == 3
    assert tokens[0] == Token("Hello", TokenKind.WORD, 0, 5)
    assert tokens[1] == Token("   ", TokenKind.WHITESPACE, 5, 8)
    assert tokens[2] == Token("world", TokenKind.WORD, 8, 13)
    assert verify_token_spans(text, tokens) is True


def test_lowercase_option() -> None:
    text = "Hello World"
    assert tokenize(text, lowercase=True) == ["hello", "world"]


def test_detailed_mode_returns_tokens() -> None:
    text = "Hello world"
    tokens = tokenize(text, detailed=True)
    assert all(isinstance(t, Token) for t in tokens)
    assert len(tokens) == 2
    assert tokens[0].text == "Hello"
    assert tokens[1].text == "world"
    assert verify_token_spans(text, tokens) is True


def test_streaming_tokenize_iter() -> None:
    tokenizer = Tokenizer()
    text = "Quick brown fox jumps"
    gen = tokenizer.tokenize_iter(text)
    assert next(gen) == "Quick"
    assert next(gen) == "brown"
    assert next(gen) == "fox"
    assert next(gen) == "jumps"
    with pytest.raises(StopIteration):
        next(gen)


def test_invalid_input_type() -> None:
    with pytest.raises(InvalidInputError):
        tokenize(12345)  # type: ignore[arg-type]

    with pytest.raises(InvalidInputError):
        tokenize(None)  # type: ignore[arg-type]

    with pytest.raises(InvalidInputError):
        tokenize(["a", "b"])  # type: ignore[arg-type]
