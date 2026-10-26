"""Tests for punctuation handling and edge cases."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_standard_punctuation() -> None:
    text = "Hello, world!"
    assert tokenize(text) == ["Hello", ",", "world", "!"]


def test_adjacent_repeated_punctuation() -> None:
    text = "What?!"
    assert tokenize(text) == ["What", "?", "!"]

    text_excl = "Hello!!!"
    assert tokenize(text_excl) == ["Hello", "!", "!", "!"]


def test_ellipsis() -> None:
    text = "Wait... really?"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == ["Wait", "...", "really", "?"]
    assert tokens[1].kind == TokenKind.PUNCTUATION
    assert tokens[1].text == "..."
    assert verify_token_spans(text, tokens) is True


def test_brackets_quotes_delimiters() -> None:
    text = "([Hello]: \"world\"; {goodbye}.)"
    expected = [
        "(",
        "[",
        "Hello",
        "]",
        ":",
        '"',
        "world",
        '"',
        ";",
        "{",
        "goodbye",
        "}",
        ".",
        ")",
    ]
    assert tokenize(text) == expected


def test_dash_sequences() -> None:
    text = "one--two---three"
    assert tokenize(text) == ["one", "--", "two", "---", "three"]
