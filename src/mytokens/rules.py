"""Rule definitions, pre-compiled patterns, and custom rule registry for MyTokens."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Pattern

from mytokens.exceptions import RuleError
from mytokens.tokens import TokenKind

# URL pattern: matches http, https, ftp, file with path/query/fragment
# Excludes closing brackets/quotes/periods if they are trailing sentence punctuation.
URL_REGEX = re.compile(
    r"""(?xi)
    \b(?:https?|ftp|file)://
    [^\s<>'"{}|\\^`\[\]]+
    """
)

# Trailing punctuation to strip from URLs and Emails when attached to sentence endings
TRAILING_PUNCT = ".,;:!?)'\"}]>"

# Email pattern: RFC-practical email format
EMAIL_REGEX = re.compile(
    r"""(?xi)
    \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
    """
)

# Emoji pattern: supports standard emoji ranges, skin-tone modifiers, variation selectors, and ZWJ sequences
_EMOJI_BASE = (
    r"(?:"
    r"[\U0001F600-\U0001F64F]"  # Emoticons
    r"|[\U0001F300-\U0001F5FF]"  # Misc Symbols and Pictographs
    r"|[\U0001F680-\U0001F6FF]"  # Transport and Map
    r"|[\U0001F1E0-\U0001F1FF]"  # Regional indicator symbols (flags)
    r"|[\U0001F900-\U0001F9FF]"  # Supplemental Symbols and Pictographs
    r"|[\U0001FA00-\U0001FA6F]"  # Chess, symbols extended-A
    r"|[\U0001FA70-\U0001FAFF]"  # Symbols and Pictographs Extended-A
    r"|[\u2600-\u26FF]"          # Misc symbols (sun, umbrella, heart, etc.)
    r"|[\u2700-\u27BF]"          # Dingbats
    r"|[\u2300-\u23FF]"          # Misc Technical
    r"|[\u2B50\u2B55\u203C\u2049\u2122\u2139\u2934\u2935\u3030\u303D\u3297\u3299]"
    r")"
)
_MODIFIER = r"[\U0001F3FB-\U0001F3FF]"  # Skin tone modifiers
_VARIATION = r"\uFE0F"                  # Emoji variation selector
_ZWJ = r"\u200D"                        # Zero-width joiner

# Complete emoji sequence: (base + optional modifier/variation)(ZWJ + base + optional modifier/variation)*
EMOJI_REGEX = re.compile(
    rf"(?:{_EMOJI_BASE}(?:{_MODIFIER}|{_VARIATION})?)(?:{_ZWJ}{_EMOJI_BASE}(?:{_MODIFIER}|{_VARIATION})?)*"
)

# Number pattern:
# 1. Scientific: 1.23e-4, 1e10
# 2. Formatted thousands: 1,000,000 or 1,234.56
# 3. Floating point: 3.14159, .75, 0.5
# 4. Plain integer: 42
NUMBER_REGEX = re.compile(
    r"""(?x)
    (?:
        \b\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][+-]?\d+)?\b   # 1,000 or 1,000.50
        | \b\d+\.\d+(?:[eE][+-]?\d+)?\b                      # 3.14, 3.14e+5
        | \b\d+[eE][+-]?\d+\b                                # 1e10, 2E-3
        | \b\d+\b                                            # 42
        | \.\d+(?:[eE][+-]?\d+)?\b                           # .5, .75
    )
    """
)

# English Contractions lookup: maps full contraction string to tuple of sub-token strings
# Offsets into the original contraction string partition it cleanly:
CONTRACTIONS_MAP: dict[str, tuple[str, str]] = {
    "i'm": ("I", "'m"),
    "i’m": ("I", "’m"),
    "you're": ("you", "'re"),
    "you’re": ("you", "’re"),
    "we're": ("we", "'re"),
    "we’re": ("we", "’re"),
    "they're": ("they", "'re"),
    "they’re": ("they", "’re"),
    "it's": ("it", "'s"),
    "it’s": ("it", "’s"),
    "he's": ("he", "'s"),
    "he’s": ("he", "’s"),
    "she's": ("she", "'s"),
    "she’s": ("she", "’s"),
    "that's": ("that", "'s"),
    "that’s": ("that", "’s"),
    "what's": ("what", "'s"),
    "what’s": ("what", "’s"),
    "there's": ("there", "'s"),
    "there’s": ("there", "’s"),
    "here's": ("here", "'s"),
    "here’s": ("here", "’s"),
    "who's": ("who", "'s"),
    "who’s": ("who", "’s"),
    "how's": ("how", "'s"),
    "how’s": ("how", "’s"),
    "where's": ("where", "'s"),
    "where’s": ("where", "’s"),
    "when's": ("when", "'s"),
    "when’s": ("when", "’s"),
    "why's": ("why", "'s"),
    "why’s": ("why", "’s"),
    "can't": ("ca", "n't"),
    "can’t": ("ca", "n’t"),
    "won't": ("wo", "n't"),
    "won’t": ("wo", "n’t"),
    "shan't": ("sha", "n't"),
    "shan’t": ("sha", "n’t"),
    "ain't": ("ai", "n't"),
    "ain’t": ("ai", "n’t"),
    "don't": ("do", "n't"),
    "don’t": ("do", "n’t"),
    "doesn't": ("does", "n't"),
    "doesn’t": ("does", "n’t"),
    "didn't": ("did", "n't"),
    "didn’t": ("did", "n’t"),
    "haven't": ("have", "n't"),
    "haven’t": ("have", "n’t"),
    "hasn't": ("has", "n't"),
    "hasn’t": ("has", "n’t"),
    "hadn't": ("had", "n't"),
    "hadn’t": ("had", "n’t"),
    "aren't": ("are", "n't"),
    "aren’t": ("are", "n’t"),
    "isn't": ("is", "n't"),
    "isn’t": ("is", "n’t"),
    "wasn't": ("was", "n't"),
    "wasn’t": ("was", "n’t"),
    "weren't": ("were", "n't"),
    "weren’t": ("were", "n’t"),
    "wouldn't": ("would", "n't"),
    "wouldn’t": ("would", "n’t"),
    "shouldn't": ("should", "n't"),
    "shouldn’t": ("should", "n’t"),
    "couldn't": ("could", "n't"),
    "couldn’t": ("could", "n’t"),
    "mustn't": ("must", "n't"),
    "mustn’t": ("must", "n’t"),
    "i've": ("I", "'ve"),
    "i’ve": ("I", "’ve"),
    "you've": ("you", "'ve"),
    "you’ve": ("you", "’ve"),
    "we've": ("we", "'ve"),
    "we’ve": ("we", "’ve"),
    "they've": ("they", "'ve"),
    "they’ve": ("they", "’ve"),
    "i'll": ("I", "'ll"),
    "i’ll": ("I", "’ll"),
    "you'll": ("you", "'ll"),
    "you’ll": ("you", "’ll"),
    "he'll": ("he", "'ll"),
    "he’ll": ("he", "’ll"),
    "she'll": ("she", "'ll"),
    "she’ll": ("she", "’ll"),
    "we'll": ("we", "'ll"),
    "we’ll": ("we", "’ll"),
    "they'll": ("they", "'ll"),
    "they’ll": ("they", "’ll"),
    "i'd": ("I", "'d"),
    "i’d": ("I", "’d"),
    "you'd": ("you", "'d"),
    "you’d": ("you", "’d"),
    "he'd": ("he", "'d"),
    "he’d": ("he", "’d"),
    "she'd": ("she", "'d"),
    "she’d": ("she", "’d"),
    "we'd": ("we", "'d"),
    "we’d": ("we", "’d"),
    "they'd": ("they", "'d"),
    "they’d": ("they", "’d"),
}

# Regex to detect contractions in text
CONTRACTION_REGEX = re.compile(
    r"""(?xi)\b(?:
        [A-Za-z]+(?:['’](?:m|re|ve|ll|d|s))
        | [A-Za-z]+n['’]t
    )\b"""
)

# Whitespace pattern: matches contiguous unicode whitespace
WHITESPACE_REGEX = re.compile(r"\s+")

# Punctuation pattern: single punctuation marks or common repeated sequences (..., --, ---)
PUNCTUATION_REGEX = re.compile(
    r"""(?x)
    \.\.\.+               # Ellipsis ...
    | -{2,}               # Dash sequences -- or ---
    | [!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]  # Standard ASCII punctuation
    | [\u2010-\u2027\u2030-\u205E\u3001-\u3003\u3008-\u301F] # Unicode punctuation marks
    """
)


@dataclass(frozen=True, slots=True)
class CustomRule:
    """Represents a user-defined custom tokenization rule.

    Attributes:
        name: Unique identifier for the rule.
        pattern: Compiled regular expression to match.
        kind: TokenKind to assign to matched spans.
        priority: Lower numbers run earlier (0 is highest priority).
    """

    name: str
    pattern: Pattern[str]
    kind: TokenKind
    priority: int = 50

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise RuleError("Rule name must be a non-empty string")
        if not isinstance(self.pattern, re.Pattern):
            raise RuleError(f"Rule pattern must be a compiled re.Pattern, got {type(self.pattern)}")
        if not isinstance(self.kind, TokenKind):
            raise RuleError(f"Rule kind must be a TokenKind instance, got {type(self.kind)}")
        if not isinstance(self.priority, int):
            raise RuleError("Rule priority must be an integer")
