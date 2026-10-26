# Development Instructions — Custom Python Tokenizer

## 1. Role

Act as a senior Python library engineer and NLP engineer.

Your task is to implement a production-quality tokenizer package from the project context.

Do not treat this as a simple coding exercise. Every implementation decision should consider:

- API stability,
- correctness,
- maintainability,
- performance,
- Unicode,
- testing,
- packaging,
- documentation,
- backwards compatibility.

---

## 2. General Rules

### Rule 1 — Keep the public API small

Prefer a small API such as:

```python
tokenize(text, **options)
Tokenizer(...)
Token(...)
```

Do not expose internal implementation details unnecessarily.

### Rule 2 — Separate public API from internals

Public:

```python
from package_name import tokenize, Tokenizer, Token
```

Internal modules may change without breaking users.

### Rule 3 — Avoid unnecessary dependencies

Use Python standard library whenever practical.

Dependencies must have a clear technical reason.

### Rule 4 — Type everything

Use Python type hints throughout the public and internal code.

Example:

```python
def tokenize(text: str) -> list[str]:
    ...
```

### Rule 5 — Validate inputs

Invalid arguments should produce clear exceptions.

Example:

```python
TypeError("text must be a string")
```

Do not silently accept invalid input.

---

## 3. Tokenization Rules

The tokenizer must follow an explicit rule priority.

Recommended order:

```text
1. Protected structured tokens
2. Whitespace
3. Words
4. Numbers
5. Emoji
6. Punctuation
7. Symbols
8. Unknown characters
```

Protected tokens such as URLs and emails must be detected before punctuation splitting.

For example:

```text
https://example.com/test?q=1
```

must not become dozens of tokens when URL recognition is enabled.

---

## 4. Scanner Design

Prefer a deterministic left-to-right scanner over repeatedly applying unrelated regex substitutions.

Conceptually:

```python
position = 0

while position < len(text):
    rule = find_matching_rule(text, position)

    if rule:
        token = rule.consume(text, position)
        emit(token)
        position = token.end
    else:
        consume_unknown_character()
```

Rules should have predictable priority.

Do not build a pipeline that repeatedly modifies the entire input string unless there is a strong reason.

---

## 5. Rule Abstraction

A future-friendly rule interface may look conceptually like:

```python
class TokenRule(Protocol):
    def match(self, text: str, position: int) -> Match | None:
        ...
```

Do not over-engineer V1.

A small internal abstraction is preferable to a complex plugin architecture.

---

## 6. Unicode Requirements

Never assume that:

```python
'a' <= char <= 'z'
```

is sufficient for identifying letters.

Use Unicode-aware mechanisms where possible.

Consider:

- `str.isalpha()`
- `str.isdigit()`
- `str.isalnum()`
- Unicode categories where necessary
- combining marks
- non-Latin scripts

Test at least:

```text
English
Hindi
Japanese
Chinese
Arabic
accented Latin
emoji
```

---

## 7. Whitespace

Whitespace behavior must be configurable.

Default:

```python
preserve_whitespace=False
```

Optional:

```python
preserve_whitespace=True
```

When preserved, whitespace should have its own token category.

Do not accidentally remove meaningful Unicode whitespace.

---

## 8. Punctuation

Punctuation should generally be emitted separately.

Example:

```text
Hello, world!
```

becomes:

```text
["Hello", ",", "world", "!"]
```

Handle repeated punctuation:

```text
What?!
```

Possible output:

```text
["What", "?", "!"]
```

Document the behavior clearly.

---

## 9. Numbers

Support at least:

- integers,
- decimals,
- negative numbers where practical,
- comma-separated numbers where explicitly supported.

Do not accidentally classify punctuation as part of every number.

Examples:

```text
42
3.14
-10
```

The exact supported grammar must be documented and tested.

---

## 10. URLs and Emails

These should be implemented as protected token rules.

Examples:

```text
https://example.com
http://example.com/path
user@example.com
```

Recognition should be configurable.

The tokenizer should not attempt to become a complete URL validator. It only needs a practical tokenization rule.

---

## 11. Contractions

Contraction handling must be configurable.

Do not silently force linguistic splitting.

Recommended:

```python
split_contractions=True
```

should use a documented rule set.

Support common forms first:

```text
I'm
you're
he's
we're
they're
don't
can't
won't
isn't
```

The rule set can grow later.

---

## 12. Token Object

A `Token` should preferably be immutable.

Example:

```python
@dataclass(frozen=True, slots=True)
class Token:
    text: str
    kind: TokenKind
    start: int
    end: int
```

Offsets must refer to the original input.

Never calculate offsets from normalized text unless the API explicitly documents that behavior.

---

## 13. Normalization

Normalization should be separate from tokenization.

Do not silently lowercase user input.

Bad:

```python
tokenize("Python") -> ["python"]
```

unless explicitly configured.

Good:

```python
tokenize("Python", lowercase=True)
```

This preserves user expectations.

---

## 14. Error Handling

Create a small exception hierarchy only if needed.

Example:

```python
TokenizerError(Exception):
    ...
```

Avoid excessive custom exceptions.

---

## 15. Testing Instructions

Every tokenizer rule must have:

1. normal case,
2. boundary case,
3. malformed case,
4. Unicode case where applicable,
5. regression test after bug fixes.

Example:

```python
def test_url_is_single_token():
    ...
```

Use pytest.

Test both:

```python
tokenize(...)
```

and:

```python
Tokenizer(...).tokenize(...)
```

if both APIs exist.

---

## 16. Property/Invariant Testing

Where practical, verify invariants such as:

- tokenizer does not crash on arbitrary Unicode strings,
- token offsets remain ordered,
- token offsets are within input bounds,
- concatenating token spans reconstructs the source when whitespace/tokens are preserved,
- no token has an invalid range.

Property-based testing may be added later with Hypothesis, but it should not be mandatory for V1.

---

## 17. Documentation Instructions

README must include:

1. Project description
2. Installation
3. Quick start
4. Examples
5. Tokenizer configuration
6. Token categories
7. Detailed tokens
8. Unicode support
9. Performance/benchmark section
10. Development setup
11. Testing
12. Contributing
13. License
14. Roadmap

Avoid unsupported claims such as:

- "fastest tokenizer"
- "best tokenizer"
- "production ready"

unless backed by evidence.

---

## 18. Packaging Instructions

Use `pyproject.toml`.

The package must support:

```bash
python -m build
```

and:

```bash
python -m pip install dist/*.whl
```

Use a `src/` layout if practical:

```text
src/
└── package_name/
```

Recommended metadata:

- name
- version
- description
- readme
- requires-python
- license
- authors
- classifiers
- project URLs

---

## 19. Versioning

Use Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
0.1.0
0.1.1
0.2.0
1.0.0
```

Do not introduce breaking API changes in patch releases.

---

## 20. CI

Set up CI for:

- supported Python versions,
- tests,
- linting,
- optional type checking,
- package build.

GitHub Actions is recommended.

---

## 21. Benchmarking

Benchmarks must be reproducible.

Record:

```text
Python version
OS
CPU
RAM
input corpus
input size
configuration
iterations
throughput
```

Avoid misleading microbenchmarks.

Include realistic text.

---

## 22. Git Workflow

Recommended commits:

```text
feat: add basic tokenizer
feat: add token metadata
feat: add unicode handling
feat: add url detection
test: add punctuation cases
docs: add getting started guide
perf: optimize scanner
fix: correct decimal parsing
build: configure pyproject
```

Keep commits focused.

---

## 23. Security

The tokenizer processes user-provided text.

Avoid:

- unsafe `eval`,
- dynamic code execution,
- shell execution,
- arbitrary file access,
- unbounded recursive parsing.

Regex patterns must be designed carefully to avoid catastrophic backtracking.

For large input, consider configurable maximum input size or streaming APIs in future versions.

---

## 24. Compatibility

Define supported Python versions in `pyproject.toml`.

Do not use language features newer than the declared minimum version.

If Python 3.10+ is selected, use modern typing consistently.

---

## 25. Release Checklist

Before release:

```text
[ ] Tests pass
[ ] Lint passes
[ ] Type checks pass
[ ] README complete
[ ] API documented
[ ] CHANGELOG updated
[ ] Version updated
[ ] Wheel builds
[ ] Source distribution builds
[ ] Local wheel installation tested
[ ] Benchmark recorded
[ ] License included
[ ] Git tag created
[ ] PyPI/TestPyPI upload tested
```

---

## 26. Important Implementation Principle

Do not copy NLTK internals.

The project can be inspired by the behavior and API ergonomics of existing NLP libraries, but the implementation should be independently designed and written.

The goal is to create an original open-source tokenizer package.
