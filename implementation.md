# Implementation Plan — Custom Python Tokenizer Package

## 1. Implementation Strategy

Build the project incrementally.

Do not start by implementing every feature.

The recommended order is:

```text
Project scaffolding
        ↓
Core Token model
        ↓
Basic scanner
        ↓
Words / numbers / punctuation
        ↓
Whitespace configuration
        ↓
Unicode support
        ↓
URLs / emails
        ↓
Contractions
        ↓
Emoji
        ↓
Custom rules
        ↓
Benchmarks
        ↓
Documentation
        ↓
Packaging
        ↓
CI
        ↓
PyPI release
```

---

# 2. Initial Repository Structure

Recommended:

```text
custom-tokenizer/
│
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── tokenizer.py
│       ├── tokens.py
│       ├── rules.py
│       ├── config.py
│       ├── normalizer.py
│       ├── exceptions.py
│       └── utils.py
│
├── tests/
│   ├── conftest.py
│   ├── test_basic.py
│   ├── test_punctuation.py
│   ├── test_numbers.py
│   ├── test_unicode.py
│   ├── test_urls.py
│   ├── test_emails.py
│   ├── test_contractions.py
│   ├── test_tokens.py
│   └── test_regression.py
│
├── benchmarks/
│   ├── benchmark_basic.py
│   └── benchmark_corpus.py
│
├── docs/
│   ├── getting_started.md
│   ├── api.md
│   └── tokenization_rules.md
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── pyproject.toml
└── .gitignore
```

---

# 3. Phase 1 — Package Scaffolding

Create the Python package and packaging configuration.

Example `pyproject.toml` responsibilities:

```text
build system
project metadata
package discovery
Python version
dependencies
optional development dependencies
```

Development dependencies can include:

```text
pytest
ruff
mypy
build
twine
```

The core package should ideally have zero runtime dependencies.

---

# 4. Phase 2 — Token Model

Implement:

```python
Token
TokenKind
```

Recommended:

```python
from dataclasses import dataclass
from enum import Enum


class TokenKind(str, Enum):
    WORD = "word"
    NUMBER = "number"
    PUNCTUATION = "punctuation"
    WHITESPACE = "whitespace"
    SYMBOL = "symbol"
    URL = "url"
    EMAIL = "email"
    EMOJI = "emoji"


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    kind: TokenKind
    start: int
    end: int
```

Verify:

```python
token.start <= token.end
token.end <= len(source)
```

---

# 5. Phase 3 — Basic Scanner

Implement a left-to-right scanner.

Concept:

```python
class Tokenizer:
    def tokenize(self, text: str) -> list[Token]:
        ...
```

Pseudo implementation:

```python
while position < len(text):

    if matches_url(text, position):
        consume_url()

    elif matches_email(text, position):
        consume_email()

    elif is_whitespace(text[position]):
        consume_whitespace()

    elif is_word_character(text[position]):
        consume_word()

    elif is_number(text, position):
        consume_number()

    elif is_emoji(text, position):
        consume_emoji()

    elif is_punctuation(text[position]):
        consume_punctuation()

    else:
        consume_symbol()
```

The actual priority should be validated with tests.

---

# 6. Phase 4 — Word Tokenization

Basic word recognition should support Unicode.

Example:

```python
char.isalpha()
```

A word may include combining marks or internal apostrophes depending on configuration.

Initial behavior:

```text
Hello world
```

→

```python
["Hello", "world"]
```

Test:

```text
hello
Hello
HELLO
café
नमस्ते
こんにちは
你好
```

---

# 7. Phase 5 — Number Tokenization

Implement a small numeric scanner rather than using an overly broad regex.

Minimum:

```text
42
3.14
0.5
```

Potential future support:

```text
-42
1,000
1e10
₹500
$10.50
```

Do not add every format in V1.

Each supported format must have tests.

---

# 8. Phase 6 — Punctuation

Maintain a clear punctuation classification.

Examples:

```text
.
,
!
?
:
;
(
)
[
]
{
}
"
'
```

Output:

```python
["Hello", ",", "world", "!"]
```

Test adjacent punctuation:

```text
Hello!!!
What?!
...
```

---

# 9. Phase 7 — Whitespace

Add:

```python
preserve_whitespace=False
```

When false:

```text
Hello   world
```

→

```python
["Hello", "world"]
```

When true:

```python
[
    Token("Hello", ...),
    Token("   ", TokenKind.WHITESPACE, ...),
    Token("world", ...)
]
```

Preserve original whitespace text.

---

# 10. Phase 8 — Public Convenience API

Expose:

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
    detailed: bool = False,
) -> list[str] | list[Token]:
    ...
```

Prefer returning strings by default because this is easiest for users.

Example:

```python
from package_name import tokenize

tokens = tokenize("Hello, world!")
```

---

# 11. Phase 9 — Normalization

Create a separate normalizer.

Possible operations:

```python
normalize_unicode
lowercase
strip
```

Important:

Tokenization and normalization should not be tightly coupled.

A user must be able to tokenize without changing the original text.

---

# 12. Phase 10 — URL Detection

Implement a practical URL rule.

Examples:

```text
https://example.com
http://example.com
https://example.com/path?q=123
```

Expected:

```python
[
    "Visit",
    "https://example.com/path?q=123"
]
```

Do not attempt to implement a full RFC URL parser.

The objective is tokenization, not validation.

---

# 13. Phase 11 — Email Detection

Examples:

```text
hello@example.com
user.name+tag@example.co.uk
```

Expected as one token when enabled.

Malformed strings should fall back to normal lexical tokenization rather than crashing.

---

# 14. Phase 12 — Contraction Handling

Implement a controlled rule map.

Example:

```python
CONTRACTIONS = {
    "I'm": ["I", "'m"],
    "you're": ["you", "'re"],
    "don't": ["do", "n't"],
    "can't": ["can", "n't"],
}
```

Do not rely only on lowercasing because original token text may need to be preserved.

Future versions can make contraction rules language-specific.

---

# 15. Phase 13 — Emoji

Emoji support is difficult because some emoji are represented by multiple Unicode code points.

V1 should define a practical scope.

Possible V1 strategy:

- recognize common emoji ranges,
- preserve emoji sequences where practical,
- avoid claiming complete Unicode emoji compliance.

Document limitations.

A future implementation can use Unicode grapheme-cluster logic.

---

# 16. Phase 14 — Custom Rules

After the core tokenizer is stable, allow custom rules.

Conceptual API:

```python
tokenizer.add_rule(
    name="hashtag",
    pattern=...,
    kind=TokenKind.SYMBOL,
    priority=...
)
```

Example future extension:

```text
#python
```

→

```text
HASHTAG
```

Do not implement this before the base architecture is stable.

---

# 17. Phase 15 — Token Offsets

For every detailed token:

```python
token.text == source[token.start:token.end]
```

must hold whenever normalization is disabled.

This is an important invariant.

Test it heavily.

---

# 18. Phase 16 — Test Matrix

Build a test matrix.

### Basic

```text
hello
hello world
Hello World
```

### Punctuation

```text
hello!
hello, world.
What?!
```

### Numbers

```text
42
3.14
-10
```

### Unicode

```text
café
नमस्ते
你好
こんにちは
مرحبا
```

### URLs

```text
https://example.com
http://example.com/path
```

### Emails

```text
user@example.com
```

### Contractions

```text
I'm
don't
can't
we're
```

### Whitespace

```text
hello world
hello    world
hello\tworld
hello\nworld
```

### Empty input

```text
""
```

### Large input

Test several MB of text.

---

# 19. Phase 17 — Regression Tests

Whenever a bug is fixed, add a test.

Example:

```python
def test_url_query_parameter_not_split():
    ...
```

This prevents future refactors from reintroducing bugs.

---

# 20. Phase 18 — Benchmarking

Create benchmark scripts.

Measure:

```text
characters/second
tokens/second
time/input size
memory usage
```

Use realistic datasets.

Potential benchmark inputs:

```text
short sentence
paragraph
large text document
mixed Unicode document
social-media-like text
technical text
```

If comparing against NLTK, clearly document which NLTK tokenizer and version were used.

Do not compare incompatible tokenizer behaviors without explaining the difference.

---

# 21. Phase 19 — Dataset for Evaluation

For serious evaluation, use publicly available text datasets.

Possible sources include:

- Project Gutenberg
- Wikipedia dumps
- public news datasets
- Universal Dependencies treebanks
- public NLP benchmark corpora with compatible licenses

Always verify dataset licensing before redistributing data with the package.

Do not include large datasets inside the Python package.

---

# 22. Phase 20 — Quality Tooling

Run:

```bash
pytest
ruff check .
ruff format --check .
mypy src
python -m build
```

Fix all errors before release.

---

# 23. Phase 21 — CI

GitHub Actions should run on every push and pull request.

Example matrix:

```text
Python 3.10
Python 3.11
Python 3.12
Python 3.13
```

Adjust according to the actual supported range.

CI stages:

```text
checkout
↓
install dependencies
↓
lint
↓
type check
↓
tests
↓
build package
```

---

# 24. Phase 22 — Documentation

README should contain a minimal example:

```python
from package_name import tokenize

text = "Hello, world! I'm building an NLP library."

print(tokenize(text))
```

Then explain advanced use:

```python
from package_name import Tokenizer

tokenizer = Tokenizer(
    preserve_whitespace=False,
    split_contractions=True,
)

tokens = tokenizer.tokenize(text)
```

Document every public parameter.

---

# 25. Phase 23 — API Stability

Keep V1 API minimal.

Recommended public exports:

```python
__all__ = [
    "Token",
    "TokenKind",
    "Tokenizer",
    "tokenize",
]
```

Do not expose internal regexes or scanner classes as public API unless necessary.

---

# 26. Phase 24 — Packaging

Build:

```bash
python -m build
```

Expected:

```text
dist/
├── package_name-X.Y.Z.tar.gz
└── package_name-X.Y.Z-py3-none-any.whl
```

Test installation:

```bash
python -m venv .venv-test
```

Then:

```bash
python -m pip install dist/*.whl
```

Run:

```python
import package_name
print(package_name.tokenize("Hello, world!"))
```

---

# 27. Phase 25 — TestPyPI

Before the production PyPI release, publish to TestPyPI.

Conceptual process:

```text
build
↓
upload to TestPyPI
↓
install from TestPyPI
↓
test clean environment
↓
fix issues
↓
production PyPI
```

Never upload API keys to Git.

Use environment variables or trusted publishing.

---

# 28. Phase 26 — Production PyPI

Final release:

```text
update version
update changelog
run tests
build
verify metadata
upload
create Git tag
publish GitHub release
```

Recommended release tag:

```text
v0.1.0
```

---

# 29. Expected Final User Experience

After publication, a user should be able to do:

```bash
pip install package-name
```

Then:

```python
from package_name import tokenize

text = "Hello, world! Welcome to NLP."

tokens = tokenize(text)

print(tokens)
```

Expected:

```python
["Hello", ",", "world", "!", "Welcome", "to", "NLP", "."]
```

---

# 30. Advanced Expected Usage

```python
from package_name import Tokenizer

tokenizer = Tokenizer(
    preserve_whitespace=False,
    lowercase=False,
    split_contractions=True,
    recognize_urls=True,
    recognize_emails=True,
)

tokens = tokenizer.tokenize(
    "Email me at test@example.com or visit https://example.com."
)
```

Possible result:

```text
Email
me
at
test@example.com
or
visit
https://example.com
.
```

---

# 31. Performance Result Requirements

The final project should report benchmark results in a table:

| Implementation | Input | Time | Throughput |
|---|---|---:|---:|
| Custom tokenizer | 1 MB | measured | measured |
| NLTK baseline | 1 MB | measured | measured |
| Custom tokenizer | 10 MB | measured | measured |

Do not fill these numbers manually.

They must come from actual benchmark execution.

---

# 32. Required Graphs

For a serious project report, generate:

### Graph 1 — Throughput

X-axis:

```text
Input Size
```

Y-axis:

```text
Characters/Second
```

Compare implementations.

### Graph 2 — Latency

X-axis:

```text
Text Size
```

Y-axis:

```text
Execution Time
```

### Graph 3 — Tokenization Accuracy

If a manually/externally annotated evaluation corpus is available:

```text
Tokenizer
vs
Precision / Recall / F1
```

### Graph 4 — Memory Usage

Compare memory consumption across input sizes.

Do not create accuracy graphs without a reliable gold-standard dataset.

---

# 33. Acceptance Criteria

The project is accepted when all of the following are true:

```text
[ ] Package installs with pip
[ ] Public API works
[ ] Basic words work
[ ] Punctuation works
[ ] Numbers work
[ ] Unicode works
[ ] URLs work
[ ] Emails work
[ ] Configurable whitespace works
[ ] Contractions work
[ ] Token offsets are correct
[ ] Detailed Token objects work
[ ] Invalid input is handled
[ ] Tests pass
[ ] CI passes
[ ] Lint passes
[ ] Type checking passes
[ ] Benchmark exists
[ ] README exists
[ ] API documentation exists
[ ] CHANGELOG exists
[ ] LICENSE exists
[ ] Wheel builds
[ ] Source distribution builds
[ ] TestPyPI installation succeeds
[ ] Production PyPI package is ready
```

---

# 34. Suggested Milestones

## Milestone 1 — MVP

```text
Scaffolding
Token model
Basic scanner
Words
Numbers
Punctuation
Tests
```

## Milestone 2 — Practical tokenizer

```text
Unicode
Whitespace configuration
URLs
Emails
Contractions
Detailed tokens
```

## Milestone 3 — Engineering quality

```text
Benchmarks
Documentation
Type checking
Linting
CI
Packaging
```

## Milestone 4 — Public release

```text
TestPyPI
PyPI
GitHub release
Changelog
Examples
```

## Milestone 5 — Advanced tokenizer

```text
Custom rules
Emoji
Streaming
Language profiles
Domain-specific tokenizers
```

---

# 35. Final Architecture

```text
                    ┌─────────────────────┐
                    │      User API       │
                    │ tokenize / Tokenizer│
                    └──────────┬──────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │   Configuration     │
                    └──────────┬──────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │     Normalizer      │
                    └──────────┬──────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │  Rule-Based Scanner │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            v                  v                  v
       Structured          Lexical             Unicode
         Tokens             Tokens              Rules
       URL/Email        Word/Number/Punct       Emoji
            │                  │                  │
            └──────────────────┼──────────────────┘
                               v
                    ┌─────────────────────┐
                    │    Token Objects    │
                    │ text/kind/offsets   │
                    └──────────┬──────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │  Strings / Tokens   │
                    └─────────────────────┘
```

The architecture should remain modular enough that future NLP functionality can be built on top of the tokenizer without rewriting its core.
