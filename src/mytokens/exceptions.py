"""Custom exception hierarchy for MyTokens."""

from __future__ import annotations


class TokenizerError(Exception):
    """Base exception for all errors raised by MyTokens."""


class ConfigurationError(TokenizerError):
    """Raised when an invalid configuration is provided to the Tokenizer."""


class InvalidInputError(TokenizerError, TypeError):
    """Raised when the text input to be tokenized is not a valid string."""


class RuleError(TokenizerError):
    """Raised when custom rule registration fails or encounters an invalid pattern."""
