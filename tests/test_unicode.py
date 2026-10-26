"""Tests for international scripts, Unicode characters, and emojis."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_devanagari_hindi() -> None:
    text = "नमस्ते दुनिया"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == ["नमस्ते", "दुनिया"]
    assert all(t.kind == TokenKind.WORD for t in tokens)
    assert verify_token_spans(text, tokens) is True


def test_japanese_and_chinese() -> None:
    text_ja = "こんにちは世界"
    assert tokenize(text_ja) == ["こんにちは世界"]

    text_zh = "你好世界"
    assert tokenize(text_zh) == ["你好世界"]


def test_arabic() -> None:
    text = "مرحبا بالعالم"
    assert tokenize(text) == ["مرحبا", "بالعالم"]


def test_accented_latin() -> None:
    text = "café résumé naïve"
    assert tokenize(text) == ["café", "résumé", "naïve"]


def test_emojis_simple() -> None:
    text = "I love Python ❤️🔥"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == ["I", "love", "Python", "❤️", "🔥"]
    emoji_tokens = [t for t in tokens if t.kind == TokenKind.EMOJI]
    assert len(emoji_tokens) == 2
    assert emoji_tokens[0].text == "❤️"
    assert emoji_tokens[1].text == "🔥"
    assert verify_token_spans(text, tokens) is True


def test_emojis_disabled() -> None:
    text = "Python 🔥"
    tokens = tokenize(text, recognize_emojis=False, detailed=True)
    assert len(tokens) == 2
    assert tokens[0].kind == TokenKind.WORD
    assert tokens[1].kind in (TokenKind.SYMBOL, TokenKind.UNKNOWN)


def test_complex_emoji_zwj() -> None:
    family_emoji = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"
    text = f"Family {family_emoji} together"
    tokens = tokenize(text, detailed=True)
    assert [t.text for t in tokens] == ["Family", family_emoji, "together"]
    assert tokens[1].kind == TokenKind.EMOJI
    assert verify_token_spans(text, tokens) is True
