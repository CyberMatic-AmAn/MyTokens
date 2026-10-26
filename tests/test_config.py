"""Tests for configuration validation, custom rules, and normalizer."""

import re

import pytest

from mytokens import Normalizer, TokenKind, Tokenizer, TokenizerConfig
from mytokens.exceptions import ConfigurationError, RuleError


def test_config_defaults() -> None:
    cfg = TokenizerConfig()
    assert cfg.preserve_whitespace is False
    assert cfg.lowercase is False
    assert cfg.split_contractions is False
    assert cfg.recognize_urls is True
    assert cfg.recognize_emails is True
    assert cfg.recognize_emojis is True
    assert cfg.unicode_normalization is None
    assert cfg.max_input_length is None


def test_config_invalid_types() -> None:
    with pytest.raises(ConfigurationError):
        TokenizerConfig(preserve_whitespace="yes")  # type: ignore[arg-type]

    with pytest.raises(ConfigurationError):
        TokenizerConfig(unicode_normalization="INVALID")

    with pytest.raises(ConfigurationError):
        TokenizerConfig(max_input_length=-10)


def test_max_input_length_enforcement() -> None:
    tok = Tokenizer(max_input_length=5)
    with pytest.raises(ValueError, match="exceeds maximum"):
        tok.tokenize("123456")


def test_custom_rule_registration() -> None:
    tokenizer = Tokenizer()
    tokenizer.add_rule(
        name="hashtag",
        pattern=r"#[A-Za-z0-9_]+",
        kind=TokenKind.SYMBOL,
        priority=10,
    )

    tokens = tokenizer.tokenize("Check out #python and #ai today!", detailed=True)
    hashtags = [t for t in tokens if t.kind == TokenKind.SYMBOL and t.text.startswith("#")]
    assert len(hashtags) == 2
    assert hashtags[0].text == "#python"
    assert hashtags[1].text == "#ai"


def test_custom_rule_errors() -> None:
    tokenizer = Tokenizer()
    tokenizer.add_rule("rule1", r"@\w+", TokenKind.SYMBOL)

    # Duplicate name
    with pytest.raises(RuleError, match="already registered"):
        tokenizer.add_rule("rule1", r"#\w+", TokenKind.SYMBOL)

    # Remove non-existent rule
    with pytest.raises(RuleError, match="not found"):
        tokenizer.remove_rule("non_existent")

    # Successfully remove rule
    tokenizer.remove_rule("rule1")
    assert len(tokenizer._custom_rules) == 0


def test_normalizer_utility() -> None:
    assert Normalizer.to_lower("HeLLo WorLD") == "hello world"
    assert Normalizer.strip_whitespace("   padded   ") == "padded"

    # Unicode normalization
    nfd = Normalizer.normalize_unicode("café", form="NFD")
    nfc = Normalizer.normalize_unicode(nfd, form="NFC")
    assert nfc == "café"

    # Combined normalize
    norm = Normalizer.normalize("  CAFÉ  ", unicode_form="NFC", lowercase=True, strip=True)
    assert norm == "café"
