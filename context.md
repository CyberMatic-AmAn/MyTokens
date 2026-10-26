# Project Context — Custom Python Tokenizer Library

## 1. Project Overview

Build a production-quality Python NLP tokenizer library inspired by the usability and extensibility of NLTK, but focused initially on tokenization.

The project should provide a clean Python API for converting raw text into meaningful tokens while supporting multiple tokenization strategies. It should be designed from the beginning as an installable and publishable Python package, with proper testing, documentation, versioning, benchmarking, type hints, and PyPI packaging.

Working project name:

`[CHOOSE_PACKAGE_NAME]`

Example API:

```python
from package_name import tokenize

tokens = tokenize("Hello, world! This is a tokenizer.")
print(tokens)
```

The implementation must not simply wrap NLTK. The tokenizer engine should be independently implemented using Python's standard library unless a dependency is explicitly justified.

---

## 2. Main Problem

Generic string splitting is insufficient for NLP.

For example:

```text
"Hello, world! I'm learning NLP."
```

A useful tokenizer needs to distinguish words, punctuation, contractions, numbers, whitespace, URLs, emails, emojis, and other text structures according to clearly defined rules.

Existing libraries such as NLTK, spaCy, and Hugging Face tokenizers are powerful, but this project aims to create a lightweight, understandable, extensible tokenizer package that can be used independently.

---

## 3. Project Goals

### Primary goals

1. Implement a reliable rule-based tokenizer.
2. Provide a simple public API.
3. Support configurable tokenization modes.
4. Handle Unicode text correctly.
5. Preserve or discard whitespace according to configuration.
6. Correctly handle punctuation and common contractions.
7. Support numbers and common structured tokens.
8. Provide optional URL and email recognition.
9. Provide optional emoji-aware tokenization.
10. Provide token metadata when requested.
11. Make the package fast enough for normal NLP preprocessing.
12. Make the package easy to install with pip.
13. Publish it to PyPI.
14. Provide clear documentation and examples.
15. Provide automated tests and benchmarks.

### Secondary goals

- Streaming/iterative tokenization for large text.
- Custom rule registration.
- Language-aware configurations.
- Serialization of tokenizer configuration.
- Optional integration with downstream NLP pipelines.

---

## 4. Non-Goals for Version 1

Do not initially attempt to reproduce all functionality of NLTK.

Avoid making V1 responsible for:

- Full linguistic parsing.
- POS tagging.
- Stemming.
- Lemmatization.
- Named entity recognition.
- Dependency parsing.
- Machine translation.
- Sentence semantics.
- Large language model tokenization.
- Training a neural tokenizer.

These can become future extensions.

---

## 5. Target Users

### Students

Users learning NLP who want a transparent tokenizer implementation.

### Python developers

Developers who need lightweight text preprocessing without a large NLP framework.

### Researchers

Users who need deterministic and configurable tokenization rules.

### NLP projects

Projects that need a small preprocessing dependency.

---

## 6. Design Philosophy

The library should prioritize:

- simplicity,
- correctness,
- predictability,
- extensibility,
- performance,
- Unicode support,
- clear APIs,
- backwards compatibility.

A user should be able to understand what the tokenizer is doing.

Avoid hidden magic.

---

## 7. Proposed Architecture

```text
Raw Text
   |
   v
Normalizer
   |
   v
Protected Token Detector
(URL / Email / special structured tokens)
   |
   v
Lexical Scanner
   |
   +---- Word Detector
   +---- Number Detector
   +---- Punctuation Detector
   +---- Emoji Detector
   +---- Whitespace Detector
   +---- Symbol Detector
   |
   v
Post Processor
   |
   v
Token Objects / Strings
   |
   v
Public API
```

Suggested package structure:

```text
package_name/
├── __init__.py
├── tokenizer.py
├── tokens.py
├── rules.py
├── normalizer.py
├── exceptions.py
├── config.py
└── utils.py

tests/
├── test_basic.py
├── test_punctuation.py
├── test_numbers.py
├── test_unicode.py
├── test_urls.py
├── test_emails.py
├── test_contractions.py
├── test_config.py
└── test_regression.py

benchmarks/
├── benchmark_basic.py
└── benchmark_corpus.py

docs/
├── getting_started.md
├── api.md
└── rules.md

pyproject.toml
README.md
LICENSE
CHANGELOG.md
CONTRIBUTING.md
```

---

## 8. Core Token Categories

At minimum, support:

```text
WORD
NUMBER
PUNCTUATION
WHITESPACE
SYMBOL
URL
EMAIL
EMOJI
```

Potential future categories:

```text
DATE
TIME
MENTION
HASHTAG
CURRENCY
CODE
HTML_TAG
PHONE_NUMBER
```

---

## 9. Token Representation

The library should support two output styles.

### Simple mode

```python
tokenize("Hello, world!")
```

returns:

```python
["Hello", ",", "world", "!"]
```

### Detailed mode

```python
tokenize("Hello, world!", detailed=True)
```

returns token objects conceptually like:

```python
Token(
    text="Hello",
    kind="WORD",
    start=0,
    end=5
)
```

This enables downstream NLP applications.

---

## 10. Configuration

The tokenizer should expose configuration instead of forcing one behavior.

Example:

```python
Tokenizer(
    lowercase=False,
    preserve_whitespace=False,
    split_contractions=True,
    recognize_urls=True,
    recognize_emails=True,
    recognize_emojis=True
)
```

The defaults should be conservative and unsurprising.

---

## 11. Important Tokenization Cases

### Basic text

```text
Hello world
```

Expected:

```text
Hello
world
```

### Punctuation

```text
Hello, world!
```

Expected:

```text
Hello
,
world
!
```

### Numbers

```text
I have 42 apples.
```

Expected:

```text
I
have
42
apples
.
```

### Decimal numbers

```text
3.14159
```

The implementation should define whether the decimal is one token.

Recommended:

```text
3.14159
```

as one NUMBER token.

### URLs

```text
Visit https://example.com/test?q=1
```

The URL should remain one token when URL recognition is enabled.

### Email

```text
Contact test@example.com
```

The email should remain one token.

### Contractions

```text
I'm don't can't we're
```

Configurable behavior should allow:

```text
I'm
don't
can't
we're
```

or:

```text
I
'
m
do
n't
can
'
t
we
'
re
```

### Unicode

Examples should include:

```text
नमस्ते दुनिया
こんにちは世界
你好世界
café
résumé
```

The tokenizer must not assume ASCII-only input.

### Emojis

Example:

```text
I love Python ❤️🔥
```

Emoji handling should be configurable.

---

## 12. Quality Requirements

The package should have:

- deterministic output,
- strong unit-test coverage,
- type hints,
- useful exceptions,
- documentation,
- semantic versioning,
- CI,
- linting,
- formatting,
- reproducible builds,
- package metadata,
- PyPI-ready distribution files.

Recommended quality tools:

- pytest
- ruff
- mypy
- build
- twine

Avoid unnecessary dependencies.

---

## 13. Performance Objective

The tokenizer should be benchmarked against:

1. Python `str.split()`
2. NLTK tokenizer where applicable
3. Other lightweight tokenizers if practical

The goal is not necessarily to beat NLTK in every case.

The project should clearly report:

- throughput,
- average latency,
- memory usage,
- corpus size,
- Python version,
- hardware,
- tokenizer configuration.

Never make performance claims without benchmark data.

---

## 14. Research/Engineering Value

The project demonstrates:

- lexical analysis,
- regular expressions,
- Unicode processing,
- finite-state/rule-based thinking,
- API design,
- package engineering,
- automated testing,
- benchmarking,
- open-source software development,
- Python distribution.

The tokenizer can also become the lexical foundation for a larger NLP toolkit.

---

## 15. Future Roadmap

### V0.1

- Basic tokenizer
- Words
- Numbers
- Punctuation
- Symbols
- Whitespace handling
- Tests
- PyPI packaging

### V0.2

- URLs
- Emails
- Contractions
- Unicode improvements
- Detailed Token objects

### V0.3

- Emoji support
- Custom rules
- Streaming tokenizer
- Benchmarks

### V0.4+

- Language profiles
- Hashtags
- Mentions
- Dates
- Currency
- Code-aware tokenization

---

## 16. Definition of Done

Version 1 is complete when:

- `pip install [PACKAGE_NAME]` works.
- The package imports successfully.
- Public API is documented.
- Core tokenization works.
- Edge cases have tests.
- Unicode cases are tested.
- Configuration works.
- Token metadata works.
- CI passes.
- Package can be built locally.
- Package can be installed from the built wheel.
- README contains examples.
- License is included.
- CHANGELOG exists.
- Benchmark results are documented.
- Package is ready for PyPI publication.
