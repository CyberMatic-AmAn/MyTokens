"""Core token representations and kind definitions for MyTokens."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenKind(str, Enum):
    """Enumeration of token categories identified by MyTokens."""

    WORD = "word"
    NUMBER = "number"
    PUNCTUATION = "punctuation"
    WHITESPACE = "whitespace"
    SYMBOL = "symbol"
    URL = "url"
    EMAIL = "email"
    EMOJI = "emoji"
    CONTRACTION = "contraction"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Token:
    """Represents a discrete token extracted from text with span offsets.

    Attributes:
        text: The string content of the token.
        kind: The TokenKind classification.
        start: Zero-indexed start character offset in the source text.
        end: Zero-indexed end character offset (exclusive) in the source text.
    """

    text: str
    kind: TokenKind
    start: int
    end: int

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError(f"Token text must be a str, got {type(self.text).__name__}")
        if not isinstance(self.kind, TokenKind):
            raise TypeError(f"Token kind must be an instance of TokenKind, got {type(self.kind).__name__}")
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise TypeError("Token start and end offsets must be integers")
        if self.start < 0:
            raise ValueError(f"Token start offset cannot be negative: {self.start}")
        if self.end < self.start:
            raise ValueError(f"Token end offset ({self.end}) cannot precede start offset ({self.start})")

    @property
    def span(self) -> tuple[int, int]:
        """Returns (start, end) offset tuple."""
        return self.start, self.end

    @property
    def length(self) -> int:
        """Returns character length of the token string."""
        return len(self.text)

    def to_dict(self) -> dict[str, Any]:
        """Convert token to a plain dictionary representation."""
        return {
            "text": self.text,
            "kind": self.kind.value,
            "start": self.start,
            "end": self.end,
        }
