# MyTokens

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](pyproject.toml)

A lightweight, production-grade, zero-dependency rule-based NLP tokenizer library for Python.

Inspired by the usability and extensibility of standard NLP libraries, **MyTokens** (`mytokens`) provides a clean, fast, and transparent tokenizer engine built entirely on Python's standard library. It features deterministic left-to-right lexical scanning, strict offset span integrity, comprehensive international Unicode support, and configurable tokenization modes.

---

## Features

- **Zero Runtime Dependencies**: Pure Python standard library implementation with zero external runtime requirements.
- **Span Integrity Guarantee**: Exact start and end character offsets guarantee that `source[token.start:token.end] == token.text`.
- **Comprehensive Unicode Support**: Handles non-Latin scripts (Devanagari/Hindi, Japanese Kanji/Kana, Chinese Hanzi, Arabic) and combining marks out of the box.
- **Protected Structured Tokens**: Intelligently preserves URLs (`http`, `https`, `ftp`) and email addresses without mangling sentence boundaries.
- **Numbers & Formats**: Accurately recognizes integers, floating-point decimals, scientific notation, negative numbers, and comma-formatted thousands (`1,000,000`).
- **Emoji Awareness**: Full support for standard emojis, skin-tone modifiers, variation selectors, and Zero-Width Joiner (ZWJ) sequences (e.g. 👨‍👩‍👧‍👦).
- **Contraction Splitting**: Configurable splitting of English contractions (`don't` -> `["do", "n't"]` or preserved as `["don't"]`).
- **Custom Rule Registry**: Easily register custom domain patterns (e.g., hashtags, mentions, product codes) with configurable priorities.
- **Streaming Ready**: Offers memory-efficient generator streaming via `Tokenizer.tokenize_iter()`.

---

## Installation

```bash
pip install mytokens
```

Or install locally for development:

```bash
git clone https://github.com/CyberMatic-AmAn/MyTokens.git
cd MyTokens
pip install -e .[dev]
```

---

## Quick Start

### Basic Usage

```python
from mytokens import tokenize

text = "Hello, world! I'm learning NLP with MyTokens."
tokens = tokenize(text)
print(tokens)
# ['Hello', ',', 'world', '!', "I'm", 'learning', 'NLP', 'with', 'MyTokens', '.']
```

### Detailed Mode (Span Offsets & Categories)

```python
from mytokens import tokenize

tokens = tokenize("Hello, world!", detailed=True)
for t in tokens:
    print(f"{t.text:<8} | {t.kind.value:<12} | offsets: ({t.start}, {t.end})")
```

Output:
```text
Hello    | word         | offsets: (0, 5)
,        | punctuation  | offsets: (5, 6)
world    | word         | offsets: (7, 12)
!        | punctuation  | offsets: (12, 13)
```

### Advanced Tokenizer Configuration

```python
from mytokens import Tokenizer

tokenizer = Tokenizer(
    split_contractions=True,
    preserve_whitespace=False,
    recognize_urls=True,
    recognize_emails=True,
    recognize_emojis=True,
)

text = "Don't forget to visit https://example.com or email me at user@domain.com! 🚀"
tokens = tokenizer.tokenize(text)
print(tokens)
# ['do', "n't", 'forget', 'to', 'visit', 'https://example.com', 'or', 'email', 'me', 'at', 'user@domain.com', '!', '🚀']
```

### Streaming for Large Text

```python
from mytokens import Tokenizer

tokenizer = Tokenizer()
for token in tokenizer.tokenize_iter("Streaming token generation for large corpora..."):
    process(token)
```

---

## Benchmark Results

Benchmarks conducted on Python 3.12.6, Windows 11 (AMD64):

### Throughput & Latency Comparison

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

*Note: MyTokens is ~2x faster than NLTK `word_tokenize` across standard NLP scenarios while adding structured URL/Email/Emoji detection and exact span offset tracking.*

### Corpus Scaling & Memory

| Corpus Target | Actual Size | Tokens Extracted | Elapsed Time | Throughput | Peak Traced Memory |
|:---|---:|---:|---:|---:|---:|
| **10 KB** | 8,806 chars | 1,360 | 71.43 ms | 0.13 MB/s (123,282 chars/s) | 65.94 KB |
| **100 KB** | 92,722 chars | 14,320 | 773.92 ms | 0.13 MB/s (119,809 chars/s) | 666.29 KB |
| **1 MB** | 930,328 chars | 143,680 | 13.64 s | 0.07 MB/s (68,201 chars/s) | 6.72 MB |

---

## Token Categories (`TokenKind`)

- `WORD`: Alphabetic tokens across all Unicode scripts and combining marks.
- `NUMBER`: Integers, floats, decimals, scientific notation, formatted thousands.
- `PUNCTUATION`: Delimiters, brackets, quotes, ellipses (`...`), dash sequences (`--`).
- `WHITESPACE`: Preserved contiguous spaces/tabs/newlines (when `preserve_whitespace=True`).
- `SYMBOL`: Currency (`$`, `€`, `₹`, `¥`), mathematical symbols (`+`, `=`, `÷`), and special characters.
- `URL`: Web and file links (`https://...`, `ftp://...`).
- `EMAIL`: Email addresses.
- `EMOJI`: Single emojis and compound ZWJ sequences.
- `UNKNOWN`: Fallback for unrecognized control characters.

---

## Running Tests

Run the test suite using pytest:

```bash
pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
