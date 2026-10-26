# Getting Started with MyTokens

**MyTokens** (`mytokens`) is a fast, lightweight, zero-dependency Python rule-based NLP tokenizer. It provides a simple API for converting raw text into clean tokens with first-class support for Unicode, URLs, emails, numbers, emojis, contractions, and exact span offsets.

---

## Installation

Install via pip:

```bash
pip install mytokens
```

Or install locally in editable mode for development:

```bash
git clone https://github.com/mytokens/mytokens.git
cd mytokens
pip install -e .[dev]
```

---

## Quick Start

### 1. Simple Tokenization (Strings)

By default, `tokenize` takes a string and returns a list of token strings:

```python
from mytokens import tokenize

text = "Hello, world! I'm learning NLP with MyTokens."
tokens = tokenize(text)
print(tokens)
# Output: ['Hello', ',', 'world', '!', "I'm", 'learning', 'NLP', 'with', 'MyTokens', '.']
```

### 2. Detailed Token Objects (with Offsets & Kinds)

Pass `detailed=True` to receive structured `Token` dataclass instances containing text, classification kind, and character offsets `(start, end)`:

```python
from mytokens import tokenize

tokens = tokenize("Hello, world!", detailed=True)
for tok in tokens:
    print(f"{tok.text:<10} | {tok.kind.value:<12} | span: {tok.start}:{tok.end}")
```

Output:
```text
Hello      | word         | span: 0:5
,          | punctuation  | span: 5:6
world      | word         | span: 7:12
!          | punctuation  | span: 12:13
```

---

## Working with the `Tokenizer` Class

For advanced workflows, instantiate the `Tokenizer` class:

```python
from mytokens import Tokenizer

tokenizer = Tokenizer(
    split_contractions=True,
    preserve_whitespace=False,
    recognize_urls=True,
    recognize_emails=True,
    recognize_emojis=True,
)

text = "Don't forget to visit https://example.com and email me at test@example.com! ❤️"
tokens = tokenizer.tokenize(text)
print(tokens)
```

Output:
```python
['do', "n't", 'forget', 'to', 'visit', 'https://example.com', 'and', 'email', 'me', 'at', 'test@example.com', '!', '❤️']
```

---

## Streaming / Iterative Tokenization

To process large texts or streams without loading all tokens into memory at once, use `tokenize_iter()`:

```python
from mytokens import Tokenizer

tokenizer = Tokenizer()
for tok in tokenizer.tokenize_iter("Stream of tokens arriving sequentially..."):
    print(tok)
```

---

## Custom Rules

You can register custom tokenization patterns (e.g., Twitter hashtags or mentions):

```python
from mytokens import Tokenizer, TokenKind

tokenizer = Tokenizer()
tokenizer.add_rule(
    name="hashtag",
    pattern=r"#[A-Za-z0-9_]+",
    kind=TokenKind.SYMBOL,
    priority=10,  # lower numbers execute with higher priority
)

tokens = tokenizer.tokenize("Exploring #python and #nlp!")
print(tokens)
# Output: ['Exploring', '#python', 'and', '#nlp', '!']
```
