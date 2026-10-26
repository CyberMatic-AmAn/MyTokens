"""Helper and verification utilities for MyTokens."""

from __future__ import annotations

from typing import Iterable

from mytokens.tokens import Token


def verify_token_spans(source: str, tokens: Iterable[Token]) -> bool:
    """Verifies that all token spans match the underlying source text slices.

    Args:
        source: The original un-normalized input text.
        tokens: Iterable of extracted Token instances.

    Returns:
        True if all token texts match source[start:end] exactly.
    """
    last_end = 0
    for tok in tokens:
        if tok.start < last_end:
            return False
        if tok.end > len(source):
            return False
        if source[tok.start : tok.end] != tok.text:
            return False
        last_end = tok.end
    return True


def reconstruct_text(tokens: Iterable[Token]) -> str:
    """Reconstructs text by concatenating token strings.

    If tokens include whitespace tokens, this will exactly equal the original text.
    """
    return "".join(tok.text for tok in tokens)
