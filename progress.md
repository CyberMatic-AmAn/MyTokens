# Project Progress & Workflow Tracker — MyTokens

This document tracks the workflow, architecture, milestones, and implementation progress for **MyTokens** (`mytokens`) — a production-quality, lightweight, zero-dependency Python NLP rule-based tokenizer library.

---

## 1. Project Workflow & Milestones

```
Phase 1: Architecture & Scaffolding  [x] Complete
    ├── Package layout (src/ layout: src/mytokens)
    ├── pyproject.toml build configuration (setuptools, PEP 621)
    ├── .gitignore, LICENSE (MIT), CONTRIBUTING.md, CHANGELOG.md
    └── Git repository initialization

Phase 2: Core Models & Exceptions   [x] Complete
    ├── TokenKind Enum (WORD, NUMBER, PUNCTUATION, WHITESPACE, SYMBOL, URL, EMAIL, EMOJI, CONTRACTION, UNKNOWN)
    ├── Token dataclass (frozen=True, slots=True, start, end, text, kind, span, length, to_dict)
    ├── Exception hierarchy (TokenizerError, ConfigurationError, InvalidInputError, RuleError)
    └── Unit tests for Token models & span invariants (tests/test_tokens.py)

Phase 3: Configuration & Normalizer [x] Complete
    ├── TokenizerConfig dataclass with validation and safety guards
    ├── Standalone Normalizer (Unicode NFC/NFKD/NFD/NFKC, case folding, stripping)
    └── Unit tests for config & normalization (tests/test_config.py)

Phase 4: Rule Engine & Scanner      [x] Complete
    ├── Protected token rules (URLs, Emails with sentence-ending delimiter handling)
    ├── Contractions handler (lossless partitioning preserving start:end character spans)
    ├── Unicode Word detector (Devanagari/Hindi, CJK, Arabic, Latin + combining marks)
    ├── Number detector (integers, decimals, exponents, formatted thousands, negative numbers)
    ├── Emoji detector (ranges, ZWJ sequences, skin tones, variation selectors)
    ├── Punctuation & Symbol scanner (ellipses '...', dash sequences '--', individual delimiters)
    └── Deterministic left-to-right scanner maintaining span invariants

Phase 5: Public API & Streaming     [x] Complete
    ├── Tokenizer class with .tokenize() and .tokenize_iter() generator
    ├── Public tokenize() convenience function (simple string mode and detailed Token mode)
    └── Full test matrix: 57 tests passing in 0.23s (100% pass rate)

Phase 6: Benchmarks & Documentation [x] Complete
    ├── Benchmark suite (throughput chars/s, tokens/s, latency, and memory scaling)
    ├── Documentation (docs/getting_started.md, docs/api.md, docs/rules.md)
    └── Professional README.md with empirical benchmark tables and usage guides

Phase 7: Packaging, CI & Quality    [x] Complete
    ├── GitHub Actions workflow (.github/workflows/tests.yml)
    ├── Package build verification (sdist & wheel generated via python -m build)
    ├── Twine distribution metadata validation (PASSED)
    └── Clean-room wheel installation and import verified in isolated virtual environment

Phase 8: Panel Demonstration Driver [x] Complete
    ├── driver/main.py demonstration suite
    ├── 10 structured presentation modules
    ├── Real-time span integrity and offset validation
    ├── Operator disambiguation & multilingual demos
    └── Live interactive testing console for panel prompts
```

---

## 2. Acceptance Criteria Checklist

- [x] Package installs with pip (`pip install mytokens` or `pip install dist/*.whl`)
- [x] Public API works (`from mytokens import tokenize, Tokenizer, Token, TokenKind`)
- [x] Basic words work
- [x] Punctuation works (ellipses, repeated marks, brackets, quotes)
- [x] Numbers work (integers, decimals, scientific notation, formatted thousands, negatives)
- [x] Unicode works (Devanagari, CJK, Arabic, accented Latin, combining marks)
- [x] URLs work (http/https/ftp with path/query/fragment without mangling sentence punctuation)
- [x] Emails work (RFC-practical format)
- [x] Configurable whitespace works (`preserve_whitespace=False` vs `True`)
- [x] Contractions work (`split_contractions=False` vs `True` with ASCII `'` and curly `’`)
- [x] Token offsets are correct (`source[token.start:token.end] == token.text`)
- [x] Detailed `Token` objects work
- [x] Invalid input is handled (`InvalidInputError`, `ConfigurationError`, `RuleError`)
- [x] All automated tests pass (57/57 tests passing)
- [x] CI configuration created (`.github/workflows/tests.yml`)
- [x] Benchmark suite created (`benchmarks/benchmark_basic.py` and `benchmarks/benchmark_corpus.py`)
- [x] Empirical benchmark results recorded
- [x] Documentation complete (`README.md`, `docs/getting_started.md`, `docs/api.md`, `docs/rules.md`)
- [x] CHANGELOG exists (`CHANGELOG.md`)
- [x] LICENSE exists (`LICENSE` MIT)
- [x] Wheel builds (`dist/mytokens-0.1.0-py3-none-any.whl`)
- [x] Source distribution builds (`dist/mytokens-0.1.0.tar.gz`)
- [x] Twine check passes (`twine check dist/*` PASSED)
- [x] Local wheel installation verified in isolated clean environment

---

## 3. Empirical Performance Measurements

### Throughput & Latency (Python 3.12.6, Windows 11 AMD64)

| Scenario | Input Size | Implementation | Latency (ms/run) | Throughput (MB/s) | Tokens/sec |
|:---|---:|:---|---:|---:|---:|
| **Short Sentence** | 44 chars | `str.split()` baseline | 0.0003 ms | 143.65 MB/s | 22,853,412 |
| | | **MyTokens (Default)** | **0.0480 ms** | **0.92 MB/s** | **208,522** |
| | | MyTokens (Detailed) | 0.0621 ms | 0.71 MB/s | 160,935 |
| | | NLTK `word_tokenize` | 0.1018 ms | 0.43 MB/s | 108,007 |
| **Mixed Paragraph** | 284 chars | `str.split()` baseline | 0.0029 ms | 96.34 MB/s | 12,890,532 |
| *(URLs, Emails, Numbers)* | | **MyTokens (Default)** | **0.2056 ms** | **1.38 MB/s** | **248,009** |
| | | MyTokens (Detailed) | 0.2933 ms | 0.97 MB/s | 173,865 |
| | | NLTK `word_tokenize` | 0.4042 ms | 0.70 MB/s | 128,659 |
| **Multilingual Unicode** | 113 chars | `str.split()` baseline | 0.0065 ms | 17.43 MB/s | 2,159,727 |
| *(Devanagari, CJK, Accents)* | | **MyTokens (Default)** | **0.0933 ms** | **1.21 MB/s** | **214,326** |
| | | MyTokens (Detailed) | 0.1259 ms | 0.90 MB/s | 158,864 |
| | | NLTK `word_tokenize` | 0.1969 ms | 0.57 MB/s | 86,317 |

### Corpus Scaling & Memory

| Corpus Target | Actual Size | Tokens Extracted | Elapsed Time | Throughput | Peak Traced Memory |
|:---|---:|---:|---:|---:|---:|
| **10 KB** | 8,806 chars | 1,360 | 71.43 ms | 0.13 MB/s (123,282 chars/s) | 65.94 KB |
| **100 KB** | 92,722 chars | 14,320 | 773.92 ms | 0.13 MB/s (119,809 chars/s) | 666.29 KB |
| **1 MB** | 930,328 chars | 143,680 | 13.64 s | 0.07 MB/s (68,201 chars/s) | 6.72 MB |

---

## 4. Key Architectural Invariants
1. **Zero Runtime Dependencies**: Uses solely standard library (`dataclasses`, `enum`, `re`, `unicodedata`).
2. **Span Invariant**: `source[token.start:token.end] == token.text` holds without exception unless lossy lowercase or Unicode normalization is explicitly requested.
3. **Decoupled Architecture**: Normalization is purely opt-in and does not mutate tokens or break span tracking unless configured.
