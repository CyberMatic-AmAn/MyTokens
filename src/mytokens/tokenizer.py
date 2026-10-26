"""Primary tokenizer implementation and public interface for MyTokens."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterator, Pattern

from mytokens.config import TokenizerConfig
from mytokens.exceptions import ConfigurationError, InvalidInputError, RuleError
from mytokens.rules import (
    CONTRACTION_REGEX,
    EMAIL_REGEX,
    EMOJI_REGEX,
    NUMBER_REGEX,
    PUNCTUATION_REGEX,
    TRAILING_PUNCT,
    URL_REGEX,
    WHITESPACE_REGEX,
    CustomRule,
)
from mytokens.tokens import Token, TokenKind


class Tokenizer:
    """Configurable, rule-based lexical tokenizer for natural language text.

    Supports custom rules, protected tokens (URLs, emails), unicode scripts,
    numbers, emojis, contractions, and span offsets.
    """

    def __init__(
        self,
        *,
        preserve_whitespace: bool = False,
        lowercase: bool = False,
        split_contractions: bool = False,
        recognize_urls: bool = True,
        recognize_emails: bool = True,
        recognize_emojis: bool = True,
        unicode_normalization: str | None = None,
        max_input_length: int | None = None,
        config: TokenizerConfig | None = None,
    ) -> None:
        if config is not None:
            if not isinstance(config, TokenizerConfig):
                raise ConfigurationError(f"config must be a TokenizerConfig instance, got {type(config)}")
            self._config = config
        else:
            self._config = TokenizerConfig(
                preserve_whitespace=preserve_whitespace,
                lowercase=lowercase,
                split_contractions=split_contractions,
                recognize_urls=recognize_urls,
                recognize_emails=recognize_emails,
                recognize_emojis=recognize_emojis,
                unicode_normalization=unicode_normalization,
                max_input_length=max_input_length,
            )

        self._custom_rules: list[CustomRule] = []

    @property
    def config(self) -> TokenizerConfig:
        """Returns the active tokenizer configuration."""
        return self._config

    def add_rule(
        self,
        name: str,
        pattern: str | Pattern[str],
        kind: TokenKind = TokenKind.SYMBOL,
        priority: int = 50,
    ) -> None:
        """Registers a user-defined custom tokenization rule.

        Args:
            name: Unique name for the rule.
            pattern: Regex string or compiled Pattern to match.
            kind: TokenKind classification to assign.
            priority: Evaluation priority (lower numbers execute earlier).
        """
        if any(r.name == name for r in self._custom_rules):
            raise RuleError(f"A rule with name {name!r} is already registered.")

        if isinstance(pattern, str):
            try:
                compiled = re.compile(pattern)
            except re.error as e:
                raise RuleError(f"Failed to compile pattern {pattern!r}: {e}") from e
        elif isinstance(pattern, re.Pattern):
            compiled = pattern
        else:
            raise RuleError(f"Pattern must be str or re.Pattern, got {type(pattern)}")

        rule = CustomRule(name=name, pattern=compiled, kind=kind, priority=priority)
        self._custom_rules.append(rule)
        self._custom_rules.sort(key=lambda r: r.priority)

    def remove_rule(self, name: str) -> None:
        """Removes a previously registered custom rule by name."""
        initial_len = len(self._custom_rules)
        self._custom_rules = [r for r in self._custom_rules if r.name != name]
        if len(self._custom_rules) == initial_len:
            raise RuleError(f"Rule {name!r} not found.")

    def tokenize_iter(
        self,
        text: str,
        *,
        detailed: bool = False,
    ) -> Iterator[Any]:
        """Generator yielding tokens sequentially from input text.

        Args:
            text: Input string to tokenize.
            detailed: If True, yields Token dataclass instances; if False, yields str.

        Yields:
            Token objects if detailed=True, else str tokens.
        """
        if not isinstance(text, str):
            raise InvalidInputError(f"Input text must be a string, got {type(text).__name__}")

        if self._config.max_input_length is not None and len(text) > self._config.max_input_length:
            raise ValueError(
                f"Input text length ({len(text)}) exceeds maximum allowed "
                f"length of {self._config.max_input_length} characters"
            )

        if not text:
            return

        pos = 0
        text_len = len(text)

        while pos < text_len:
            # 1. Custom Rules
            matched_custom = False
            for rule in self._custom_rules:
                m = rule.pattern.match(text, pos)
                if m and m.start() == pos and m.end() > pos:
                    tok_text = text[pos : m.end()]
                    yield self._create_token(tok_text, rule.kind, pos, m.end(), detailed)
                    pos = m.end()
                    matched_custom = True
                    break
            if matched_custom:
                continue

            # 2. Whitespace
            ws_match = WHITESPACE_REGEX.match(text, pos)
            if ws_match:
                end = ws_match.end()
                if self._config.preserve_whitespace:
                    yield self._create_token(
                        text[pos:end], TokenKind.WHITESPACE, pos, end, detailed
                    )
                pos = end
                continue

            # 3. Protected URLs
            if self._config.recognize_urls:
                url_match = URL_REGEX.match(text, pos)
                if url_match:
                    raw_url = url_match.group(0)
                    while raw_url and raw_url[-1] in TRAILING_PUNCT:
                        raw_url = raw_url[:-1]
                    if raw_url:
                        end = pos + len(raw_url)
                        yield self._create_token(
                            text[pos:end], TokenKind.URL, pos, end, detailed
                        )
                        pos = end
                        continue

            # 4. Protected Emails
            if self._config.recognize_emails:
                email_match = EMAIL_REGEX.match(text, pos)
                if email_match:
                    raw_email = email_match.group(0)
                    while raw_email and raw_email[-1] in TRAILING_PUNCT:
                        raw_email = raw_email[:-1]
                    if raw_email:
                        end = pos + len(raw_email)
                        yield self._create_token(
                            text[pos:end], TokenKind.EMAIL, pos, end, detailed
                        )
                        pos = end
                        continue

            # 5. English Contractions (when split_contractions is True)
            if self._config.split_contractions:
                cont_match = CONTRACTION_REGEX.match(text, pos)
                if cont_match:
                    raw_cont = cont_match.group(0)
                    cont_len = len(raw_cont)
                    apostrophe_idx = -1
                    for idx, ch in enumerate(raw_cont):
                        if ch in ("'", "’"):
                            apostrophe_idx = idx
                            break

                    if apostrophe_idx != -1:
                        if raw_cont.lower().endswith(("n't", "n’t")):
                            split_point = apostrophe_idx - 1
                        else:
                            split_point = apostrophe_idx

                        prefix = text[pos : pos + split_point]
                        suffix = text[pos + split_point : pos + cont_len]

                        if prefix:
                            yield self._create_token(
                                prefix, TokenKind.WORD, pos, pos + split_point, detailed
                            )
                        if suffix:
                            yield self._create_token(
                                suffix, TokenKind.WORD, pos + split_point, pos + cont_len, detailed
                            )
                        pos += cont_len
                        continue

            # 6. Emojis
            if self._config.recognize_emojis:
                emoji_match = EMOJI_REGEX.match(text, pos)
                if emoji_match:
                    end = emoji_match.end()
                    yield self._create_token(
                        text[pos:end], TokenKind.EMOJI, pos, end, detailed
                    )
                    pos = end
                    continue

            # 7. Numbers (integers, floats, exponents, thousands separators, negative numbers)
            is_neg = False
            if text[pos] == "-" and pos + 1 < text_len and (text[pos + 1].isdigit() or text[pos + 1] == "."):
                prev_char = text[pos - 1] if pos > 0 else " "
                if prev_char.isspace() or prev_char in "([{<=,+*":
                    is_neg = True

            if is_neg:
                num_sub = NUMBER_REGEX.match(text, pos + 1)
                if num_sub:
                    end = num_sub.end()
                    yield self._create_token(
                        text[pos:end], TokenKind.NUMBER, pos, end, detailed
                    )
                    pos = end
                    continue

            num_match = NUMBER_REGEX.match(text, pos)
            if num_match:
                end = num_match.end()
                yield self._create_token(
                    text[pos:end], TokenKind.NUMBER, pos, end, detailed
                )
                pos = end
                continue

            # 8. Unicode Words
            curr_char = text[pos]
            cat = unicodedata.category(curr_char)
            if cat[0] in ("L", "M"):
                word_end = pos + 1
                while word_end < text_len:
                    next_char = text[word_end]
                    next_cat = unicodedata.category(next_char)
                    if next_cat[0] in ("L", "M"):
                        word_end += 1
                    elif not self._config.split_contractions and next_char in ("'", "’") and word_end + 1 < text_len:
                        after_cat = unicodedata.category(text[word_end + 1])
                        if after_cat[0] == "L":
                            word_end += 2
                        else:
                            break
                    else:
                        break

                yield self._create_token(
                    text[pos:word_end], TokenKind.WORD, pos, word_end, detailed
                )
                pos = word_end
                continue

            # 9. Punctuation
            punct_match = PUNCTUATION_REGEX.match(text, pos)
            if punct_match:
                end = punct_match.end()
                yield self._create_token(
                    text[pos:end], TokenKind.PUNCTUATION, pos, end, detailed
                )
                pos = end
                continue

            # 10. Symbols (currency, math, other symbols)
            if cat[0] == "S" or curr_char in "$€£¥₹+<=>±×÷~^|#@%*":
                yield self._create_token(
                    curr_char, TokenKind.SYMBOL, pos, pos + 1, detailed
                )
                pos += 1
                continue

            # 11. Fallback Unknown
            yield self._create_token(
                curr_char, TokenKind.UNKNOWN, pos, pos + 1, detailed
            )
            pos += 1

    def tokenize(
        self,
        text: str,
        *,
        detailed: bool = False,
    ) -> list[Any]:
        """Tokenizes text and returns a list of tokens.

        Args:
            text: Input string to tokenize.
            detailed: If True, returns list of Token objects; if False, returns list of str.

        Returns:
            list[Token] if detailed=True, else list[str].
        """
        return list(self.tokenize_iter(text, detailed=detailed))

    def _create_token(
        self,
        raw_text: str,
        kind: TokenKind,
        start: int,
        end: int,
        detailed: bool,
    ) -> Token | str:
        tok_text = raw_text
        if self._config.unicode_normalization:
            tok_text = unicodedata.normalize(
                self._config.unicode_normalization.upper(), tok_text
            )
        if self._config.lowercase:
            tok_text = tok_text.casefold()

        if detailed:
            return Token(text=tok_text, kind=kind, start=start, end=end)
        return tok_text


def tokenize(
    text: str,
    *,
    preserve_whitespace: bool = False,
    lowercase: bool = False,
    split_contractions: bool = False,
    recognize_urls: bool = True,
    recognize_emails: bool = True,
    recognize_emojis: bool = True,
    unicode_normalization: str | None = None,
    max_input_length: int | None = None,
    detailed: bool = False,
) -> list[str] | list[Token]:
    """Convenience function to tokenize text with given configuration options.

    Args:
        text: Raw text string to tokenize.
        preserve_whitespace: Whether to emit whitespace tokens.
        lowercase: Whether to convert token texts to lowercase.
        split_contractions: Whether to split contractions (e.g. don't -> ["do", "n't"]).
        recognize_urls: Whether to match URLs as single tokens.
        recognize_emails: Whether to match email addresses as single tokens.
        recognize_emojis: Whether to match emojis and sequences as single tokens.
        unicode_normalization: Optional Unicode normalization form ('NFC', 'NFD', 'NFKC', 'NFKD').
        max_input_length: Maximum allowed input text length in characters.
        detailed: If True, returns list[Token]; if False (default), returns list[str].

    Returns:
        List of string tokens or Token dataclass instances.
    """
    tokenizer = Tokenizer(
        preserve_whitespace=preserve_whitespace,
        lowercase=lowercase,
        split_contractions=split_contractions,
        recognize_urls=recognize_urls,
        recognize_emails=recognize_emails,
        recognize_emojis=recognize_emojis,
        unicode_normalization=unicode_normalization,
        max_input_length=max_input_length,
    )
    return tokenizer.tokenize(text, detailed=detailed)
