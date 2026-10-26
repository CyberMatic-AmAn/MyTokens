# MyTokens Tokenization Rules & Architecture

MyTokens implements a deterministic, left-to-right lexical scanner designed specifically to avoid catastrophic backtracking and maintain strict character span integrity.

---

## 1. Evaluation Priority Order

The lexical scanner evaluates candidate tokens at position `pos` strictly according to the following priority:

```text
1. Custom Registered Rules (sorted by priority attribute)
2. Whitespace Sequences (\s+)
3. Protected URLs (https?://, ftp://, file://)
4. Protected Email Addresses (RFC-practical regex)
5. English Contractions (when split_contractions=True)
6. Emojis & Sequences (ZWJ, skin tone modifiers, variation selectors)
7. Numbers (scientific, decimal, integers, formatted thousands, negative numbers)
8. Unicode Words (combining marks, letters across non-Latin scripts)
9. Punctuation (repeated delimiters like '...', dashes '--', single punctuation)
10. Symbols (currency, mathematical symbols, special characters)
11. Unknown / Fallback Character
```

---

## 2. Invariant Guarantee

Whenever tokenization is executed without modifying text transformations (`lowercase=False` and `unicode_normalization=None`), the following invariant holds strictly:

$$\text{source}[\text{token.start} : \text{token.end}] == \text{token.text}$$

This ensures downstream NLP models, character span highlight tools, and NER annotators can reliably map tokens back to original documents.

---

## 3. Contraction Splitting Strategy

When `split_contractions=True`, English contractions are partitioned without mutating or dropping characters:

| Input Text | Partition 1 (`start:mid`) | Partition 2 (`mid:end`) |
|:---|:---|:---|
| `I'm` | `I` | `'m` |
| `you're` | `you` | `'re` |
| `we've` | `we` | `'ve` |
| `they'll` | `they` | `'ll` |
| `he'd` | `he` | `'d` |
| `don't` | `do` | `n't` |
| `can't` | `ca` | `n't` |
| `won't` | `wo` | `n't` |
| `user's` | `user` | `'s` |

Both ASCII straight apostrophes (`'`) and Unicode typographic apostrophes (`’`) are supported.

---

## 4. Protected Tokens (URLs & Emails)

URLs and emails appearing at sentence ends (e.g., `Visit https://example.com.`) have trailing punctuation (`.`, `,`, `!`, `?`, etc.) cleanly detached so that subsequent tokens capture the punctuation correctly without mangling the structured entity.
