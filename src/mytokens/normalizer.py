"""Decoupled text normalization utilities for MyTokens."""

from __future__ import annotations

import unicodedata

from mytokens.exceptions import ConfigurationError


class Normalizer:
    """Provides independent, non-destructive normalization transformations."""

    @staticmethod
    def normalize_unicode(text: str, form: str = "NFC") -> str:
        """Apply standard Unicode normalization form to the given text."""
        norm_form = form.upper()
        if norm_form not in {"NFC", "NFD", "NFKC", "NFKD"}:
            raise ConfigurationError(f"Invalid Unicode normalization form: {form!r}")
        return unicodedata.normalize(norm_form, text)

    @staticmethod
    def to_lower(text: str) -> str:
        """Lowercases text using Unicode-aware case folding."""
        return text.casefold()

    @staticmethod
    def strip_whitespace(text: str) -> str:
        """Strips leading and trailing whitespace."""
        return text.strip()

    @classmethod
    def normalize(
        cls,
        text: str,
        *,
        unicode_form: str | None = None,
        lowercase: bool = False,
        strip: bool = False,
    ) -> str:
        """Applies configured sequence of normalizations."""
        result = text
        if unicode_form:
            result = cls.normalize_unicode(result, unicode_form)
        if lowercase:
            result = cls.to_lower(result)
        if strip:
            result = cls.strip_whitespace(result)
        return result
