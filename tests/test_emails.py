"""Tests for email detection and boundary handling."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_basic_email() -> None:
    text = "Send mail to user@example.com please."
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == [
        "Send",
        "mail",
        "to",
        "user@example.com",
        "please",
        ".",
    ]
    assert tokens[3].kind == TokenKind.EMAIL
    assert verify_token_spans(text, tokens) is True


def test_complex_email_with_plus_and_subdomain() -> None:
    text = "Contact support+urgent@sub.domain.org for help"
    tokens = tokenize(text, detailed=True)
    assert tokens[1].text == "support+urgent@sub.domain.org"
    assert tokens[1].kind == TokenKind.EMAIL
    assert verify_token_spans(text, tokens) is True


def test_email_with_trailing_punctuation() -> None:
    text = "Email me at test@example.com."
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == [
        "Email",
        "me",
        "at",
        "test@example.com",
        ".",
    ]
    assert tokens[3].kind == TokenKind.EMAIL
    assert tokens[4].kind == TokenKind.PUNCTUATION
    assert verify_token_spans(text, tokens) is True


def test_email_recognition_disabled() -> None:
    text = "Contact test@example.com"
    tokens = tokenize(text, recognize_emails=False)
    assert "test" in tokens
    assert "@" in tokens
    assert "example" in tokens
