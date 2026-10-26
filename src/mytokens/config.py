"""Configuration options and validation for MyTokens."""

from __future__ import annotations

from dataclasses import dataclass

from mytokens.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class TokenizerConfig:
    """Configuration class controlling tokenizer scanning and filtering behavior.

    Attributes:
        preserve_whitespace: Whether to emit whitespace tokens (kind=WHITESPACE).
        lowercase: Whether to convert emitted token texts to lower case.
        split_contractions: Whether to split English contractions (e.g., don't -> ["do", "n't"]).
        recognize_urls: Whether to match URLs as single atomic tokens.
        recognize_emails: Whether to match email addresses as single atomic tokens.
        recognize_emojis: Whether to match emojis and emoji sequences as atomic tokens.
        unicode_normalization: Optional Unicode normalization form ('NFC', 'NFD', 'NFKC', 'NFKD').
        max_input_length: Maximum allowed input text length in characters (None for unlimited).
    """

    preserve_whitespace: bool = False
    lowercase: bool = False
    split_contractions: bool = False
    recognize_urls: bool = True
    recognize_emails: bool = True
    recognize_emojis: bool = True
    unicode_normalization: str | None = None
    max_input_length: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.preserve_whitespace, bool):
            raise ConfigurationError("preserve_whitespace must be a boolean")
        if not isinstance(self.lowercase, bool):
            raise ConfigurationError("lowercase must be a boolean")
        if not isinstance(self.split_contractions, bool):
            raise ConfigurationError("split_contractions must be a boolean")
        if not isinstance(self.recognize_urls, bool):
            raise ConfigurationError("recognize_urls must be a boolean")
        if not isinstance(self.recognize_emails, bool):
            raise ConfigurationError("recognize_emails must be a boolean")
        if not isinstance(self.recognize_emojis, bool):
            raise ConfigurationError("recognize_emojis must be a boolean")

        if self.unicode_normalization is not None:
            valid_forms = {"NFC", "NFD", "NFKC", "NFKD"}
            if not isinstance(self.unicode_normalization, str) or self.unicode_normalization.upper() not in valid_forms:
                raise ConfigurationError(
                    f"unicode_normalization must be one of {valid_forms} or None, "
                    f"got {self.unicode_normalization!r}"
                )

        if self.max_input_length is not None:
            if not isinstance(self.max_input_length, int) or self.max_input_length <= 0:
                raise ConfigurationError(
                    f"max_input_length must be a positive integer, got {self.max_input_length!r}"
                )
