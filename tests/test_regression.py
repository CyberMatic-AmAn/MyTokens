"""Regression and stress tests for complex and boundary inputs."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_url_query_parameters_not_corrupted() -> None:
    text = "Visit https://example.com/search?q=nlp+python&sort=desc#results today."
    tokens = tokenize(text, detailed=True)
    assert tokens[1].text == "https://example.com/search?q=nlp+python&sort=desc#results"
    assert tokens[1].kind == TokenKind.URL
    assert verify_token_spans(text, tokens) is True


def test_email_in_parentheses() -> None:
    text = "Please reach out to (support@example.com) directly."
    tokens = tokenize(text, detailed=True)
    assert tokens[4].text == "("
    assert tokens[5].text == "support@example.com"
    assert tokens[5].kind == TokenKind.EMAIL
    assert tokens[6].text == ")"
    assert verify_token_spans(text, tokens) is True


def test_numbers_followed_by_punctuation() -> None:
    text = "Room 101, floor 2. Total: $500.00."
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == [
        "Room",
        "101",
        ",",
        "floor",
        "2",
        ".",
        "Total",
        ":",
        "$",
        "500.00",
        ".",
    ]
    assert verify_token_spans(text, tokens) is True


def test_mixed_emojis_and_symbols() -> None:
    text = "Celebrate! 🚀✨ #win @ 10:00am."
    tokens = tokenize(text, detailed=True)
    emojis = [t.text for t in tokens if t.kind == TokenKind.EMOJI]
    assert emojis == ["🚀", "✨"]
    assert verify_token_spans(text, tokens) is True


def test_large_input_stability() -> None:
    # 2,000 repetitions of sentence (~100 KB text)
    sentence = "The quick brown fox jumps over the lazy dog at https://example.com. Contact info@example.com for 42 items! "
    large_text = sentence * 1000

    tokens = tokenize(large_text, detailed=True)
    assert len(tokens) > 10000
    assert verify_token_spans(large_text, tokens) is True
