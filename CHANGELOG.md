# Changelog

All notable changes to `mytokens` (MyTokens) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-22

### Added
- Core `Token` model with `@dataclass(frozen=True, slots=True)` and token span offset indexing.
- `TokenKind` enumeration covering `WORD`, `NUMBER`, `PUNCTUATION`, `WHITESPACE`, `SYMBOL`, `URL`, `EMAIL`, and `EMOJI`.
- `Tokenizer` class with configurable lexical scanner:
  - Configurable whitespace preservation or filtering.
  - Configurable contraction splitting (e.g., `don't` -> `["do", "n't"]` or `["don't"]`).
  - Protected token detection: URLs (`http`, `https`, `ftp`) and RFC-like email addresses.
  - Unicode-aware word tokenization across Latin, Devanagari, Japanese, Chinese, Arabic, and accented scripts.
  - Robust number tokenization supporting integers, decimals, scientific notation, negative numbers, and thousands commas.
  - Emoji detection supporting single-point, multi-point, variation selectors, and zero-width joiner sequences.
  - Punctuation & symbol extraction handling compound/repeated punctuation (`...`, `---`).
- Simple public API: `tokenize(text, **options)`.
- Streaming tokenization support: `Tokenizer.tokenize_iter(text)`.
- Custom rule registration mechanism: `Tokenizer.add_rule(...)`.
- Decoupled `Normalizer` utility for text sanitization, unicode normalization (NFC/NFKD/NFD/NFKC), and case folding.
- Comprehensive test suite covering basic tokens, punctuation, numbers, unicode scripts, URLs, emails, contractions, and error handling.
- Benchmarking scripts comparing throughput and latency against standard methods.
- Full type annotations and `py.typed` marker.
