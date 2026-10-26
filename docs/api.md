# MyTokens API Reference

This document provides a comprehensive reference for the public API exposed by `mytokens`.

---

## Functions

### `tokenize(text, **options)`

Convenience function to tokenize input text using standard or customized options.

```python
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
```

#### Parameters:
- `text` (`str`): The raw text to tokenize. Must be a `str`.
- `preserve_whitespace` (`bool`, default: `False`): If `True`, whitespace sequences are emitted as tokens with `kind=TokenKind.WHITESPACE`. If `False`, whitespace is consumed and omitted from output.
- `lowercase` (`bool`, default: `False`): If `True`, emitted token strings are converted to lowercase.
- `split_contractions` (`bool`, default: `False`): If `True`, English contractions are partitioned into constituent components (e.g., `don't` -> `["do", "n't"]`). If `False`, contractions remain intact as single words.
- `recognize_urls` (`bool`, default: `True`): If `True`, HTTP/HTTPS/FTP URLs are matched as single `TokenKind.URL` tokens.
- `recognize_emails` (`bool`, default: `True`): If `True`, email addresses are matched as single `TokenKind.EMAIL` tokens.
- `recognize_emojis` (`bool`, default: `True`): If `True`, emojis and ZWJ sequences are matched as single `TokenKind.EMOJI` tokens.
- `unicode_normalization` (`str | None`, default: `None`): Standard Unicode normalization form (`"NFC"`, `"NFD"`, `"NFKC"`, `"NFKD"`).
- `max_input_length` (`int | None`, default: `None`): Maximum allowed character length for input strings.
- `detailed` (`bool`, default: `False`): If `False`, returns a list of strings (`list[str]`). If `True`, returns a list of `Token` dataclass instances (`list[Token]`).

---

## Classes

### `Tokenizer`

The stateful, configurable tokenizer class.

```python
class Tokenizer:
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
    ) -> None: ...
```

#### Methods:

- **`tokenize(text: str, *, detailed: bool = False) -> list[str] | list[Token]`**  
  Tokenizes string and returns a full list of tokens.

- **`tokenize_iter(text: str, *, detailed: bool = False) -> Iterator[str | Token]`**  
  Memory-efficient generator yielding tokens sequentially.

- **`add_rule(name: str, pattern: str | Pattern[str], kind: TokenKind = TokenKind.SYMBOL, priority: int = 50) -> None`**  
  Registers a custom regular expression rule.

- **`remove_rule(name: str) -> None`**  
  Removes a previously registered custom rule.

- **`config` (`TokenizerConfig`)**  
  Read-only property returning the active `TokenizerConfig` object.

---

### `Token`

Immutable token dataclass representing a discrete token span in source text.

```python
@dataclass(frozen=True, slots=True)
class Token:
    text: str
    kind: TokenKind
    start: int
    end: int
```

#### Properties:
- `span`: Returns `(start, end)` tuple.
- `length`: Returns character count of token text.
- `to_dict()`: Converts token to a JSON-serializable dictionary.

---

### `TokenKind`

Enumeration of supported token categories:

- `TokenKind.WORD` (`"word"`)
- `TokenKind.NUMBER` (`"number"`)
- `TokenKind.PUNCTUATION` (`"punctuation"`)
- `TokenKind.WHITESPACE` (`"whitespace"`)
- `TokenKind.SYMBOL` (`"symbol"`)
- `TokenKind.URL` (`"url"`)
- `TokenKind.EMAIL` (`"email"`)
- `TokenKind.EMOJI` (`"emoji"`)
- `TokenKind.CONTRACTION` (`"contraction"`)
- `TokenKind.UNKNOWN` (`"unknown"`)

---

### `Normalizer`

Utility class for decoupled text normalization:

- `Normalizer.normalize_unicode(text, form="NFC") -> str`
- `Normalizer.to_lower(text) -> str`
- `Normalizer.strip_whitespace(text) -> str`
- `Normalizer.normalize(text, unicode_form=None, lowercase=False, strip=False) -> str`

---

## Exceptions

- `TokenizerError`: Base class for all library exceptions.
  - `ConfigurationError`: Raised on invalid configuration options.
  - `InvalidInputError`: Raised when input is not a valid `str`.
  - `RuleError`: Raised on invalid custom rule definitions or duplicate names.
