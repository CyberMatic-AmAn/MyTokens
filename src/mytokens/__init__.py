"""MyTokens — A lightweight, production-grade, rule-based NLP tokenizer library."""

from __future__ import annotations

from mytokens.config import TokenizerConfig
from mytokens.exceptions import ConfigurationError, InvalidInputError, RuleError, TokenizerError
from mytokens.normalizer import Normalizer
from mytokens.tokenizer import Tokenizer, tokenize
from mytokens.tokens import Token, TokenKind

__version__ = "0.1.0"

__all__ = [
    "ConfigurationError",
    "InvalidInputError",
    "Normalizer",
    "RuleError",
    "Token",
    "TokenKind",
    "Tokenizer",
    "TokenizerConfig",
    "TokenizerError",
    "tokenize",
]
