"""Driver demonstration script for MyTokens NLP Tokenizer.

Designed for presenting to an academic evaluation panel:
1. Demonstrates standard and edge-case tokenization capabilities.
2. Compares simple string mode vs. detailed token mode (spans & kinds).
3. Verifies strict character offset span invariants.
4. Highlights URLs, emails, numbers, contractions, multilingual Unicode, emojis, and custom rules.
5. Displays a real-time performance summary and provides an interactive test prompt.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Ensure 'src' is in Python path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from mytokens import Token, TokenKind, Tokenizer, tokenize
    from mytokens.utils import verify_token_spans
except ImportError as err:
    print(f"Error importing mytokens: {err}")
    print(f"Searched in: {SRC_DIR}")
    sys.exit(1)

# Terminal styling utilities
USE_COLOR = os.name != "nt" or "WT_SESSION" in os.environ or "TERM" in os.environ


def color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(text: str) -> str:
    return color(text, "1")


def cyan(text: str) -> str:
    return color(text, "36")


def green(text: str) -> str:
    return color(text, "32")


def yellow(text: str) -> str:
    return color(text, "33")


def magenta(text: str) -> str:
    return color(text, "35")


def header(title: str, section_num: int) -> None:
    print("\n" + "=" * 80)
    print(bold(cyan(f" [DEMO {section_num}] {title}")))
    print("=" * 80)


def print_table(tokens: list[Token], source_text: str) -> None:
    print("-" * 74)
    print(f" {'#':<3} | {'Token Text':<22} | {'Kind':<14} | {'Span':<10} | {'Invariant':<8}")
    print("-" * 74)
    for idx, t in enumerate(tokens, start=1):
        span_str = f"({t.start}, {t.end})"
        slice_match = source_text[t.start : t.end] == t.text
        match_str = green("VALID") if slice_match else yellow("FAIL")
        print(f" {idx:<3} | {t.text:<22} | {t.kind.value:<14} | {span_str:<10} | {match_str:<8}")
    print("-" * 74)


# ==============================================================================
# DEMO SECTIONS
# ==============================================================================


def demo_1_split_vs_mytokens() -> None:
    header("Why str.split() Fails vs. MyTokens in NLP", 1)
    sample = "Hello, world! We're learning NLP with MyTokens."
    print(f"{bold('Input Text:')} {sample}\n")

    # str.split()
    naive_split = sample.split()
    print(yellow(bold("[Python str.split() Output]")))
    print(f"  Result: {naive_split}")
    print(
        "  Issue:  Punctuation remains attached ('Hello,', 'world!', 'MyTokens.') and contractions are glued ('We're').\n"
    )

    # MyTokens
    tokens = tokenize(sample)
    print(green(bold("[MyTokens tokenize() Output]")))
    print(f"  Result: {tokens}")
    print("  Advantage: Punctuation and word boundaries are cleanly and accurately segmented.")


def demo_2_detailed_tokens_and_offsets() -> None:
    header("Detailed Token Mode & Span Offset Invariants", 2)
    sample = "Lexitok evolved into MyTokens: fast, typed, and zero-dependency."
    print(f"{bold('Input Text:')} {sample}")
    print(f"{bold('Invariant:')}  source[start:end] == token.text\n")

    tokens: list[Token] = tokenize(sample, detailed=True)  # type: ignore[assignment]
    print_table(tokens, sample)
    all_valid = verify_token_spans(sample, tokens)
    print(f"Strict Span Integrity Check: {green('PASSED (100% matched)') if all_valid else yellow('FAILED')}")


def demo_3_protected_urls_and_emails() -> None:
    header("Protected Entities: URLs & Emails with Sentence Boundaries", 3)
    sample = (
        "Check our paper at https://nlp-hub.org/2026/mytokens?v=1&ref=seminar#results. "
        "Contact project.lead+panel@university.edu for inquiries!"
    )
    print(f"{bold('Input Text:')} {sample}\n")

    tokens: list[Token] = tokenize(sample, detailed=True)  # type: ignore[assignment]
    for t in tokens:
        if t.kind in (TokenKind.URL, TokenKind.EMAIL):
            print(f"  Found {bold(magenta(t.kind.value.upper()))}: {cyan(t.text)} (offsets: {t.start} to {t.end})")

    print("\nNotice: Trailing sentence punctuation ('.' and '!') is cleanly separated from the URL/email.")


def demo_4_numbers_and_negative_values() -> None:
    header("Robust Numeric Recognition & Operator Disambiguation", 4)
    samples = [
        ("Financial & Scientific", "Total revenue was $1,250,000.50, and error rate is 3.14e-5."),
        ("Disambiguation (Minus vs Neg)", "Expression: 5-2 = 3, but the temperature is -15.5 degrees."),
    ]
    for label, text in samples:
        print(f"\n{bold(label)}:")
        print(f"  Input:  {text}")
        tokens = tokenize(text)
        print(f"  Tokens: {tokens}")


def demo_5_contractions() -> None:
    header("Configurable Contraction Splitting", 5)
    sample = "I'm certain they don't believe we're ready, but we won't quit."
    print(f"{bold('Input Text:')} {sample}\n")

    # Preserved (Default)
    tok_default = tokenize(sample, split_contractions=False)
    print(bold("[Default (Preserve Contractions)]:"))
    print(f"  {tok_default}\n")

    # Split (PTB-Style)
    tok_split = tokenize(sample, split_contractions=True)
    print(bold("[Configured (split_contractions=True)]:"))
    print(f"  {tok_split}")
    print("  Notice: 'don't' -> ['do', \"n't\"], 'won't' -> ['wo', \"n't\"], 'I'm' -> ['I', \"'m\"].")


def demo_6_multilingual_unicode() -> None:
    header("Multilingual Unicode & Combining Scripts", 6)
    scripts = [
        ("Hindi (Devanagari)", "नमस्ते दुनिया! हम प्राकृतिक भाषा प्रसंस्करण पढ़ रहे हैं।"),
        ("Japanese (Kanji & Kana)", "こんにちは世界。最新のトークナイザー技術です。"),
        ("Chinese (Simplified)", "你好世界！欢迎体验轻量级自然语言处理分词器。"),
        ("Arabic (Right-to-Left)", "مرحبا بالعالم! معالجة اللغات الطبيعية."),
        ("Accented Latin", "The naïve café résumé was examined by the señor."),
    ]
    for script_name, text in scripts:
        tokens = tokenize(text)
        print(f"{bold(script_name)}:")
        print(f"  Input:  {text}")
        print(f"  Tokens: {tokens}\n")


def demo_7_emojis_and_zwj() -> None:
    header("Emoji Recognition & Zero-Width Joiner (ZWJ) Sequences", 7)
    # Family ZWJ sequence
    family = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"
    sample = f"Teamwork makes the dream work! 🚀 {family} ❤️🔥"
    print(f"{bold('Input Text:')} {sample}\n")

    tokens: list[Token] = tokenize(sample, detailed=True)  # type: ignore[assignment]
    for t in tokens:
        if t.kind == TokenKind.EMOJI:
            print(f"  Emoji token detected: '{t.text}' (Length: {len(t.text)} code points, kind: {t.kind.value})")


def demo_8_custom_rules() -> None:
    header("Extensibility: Registering Custom Domain Rules", 8)
    sample = "Discussion on #NLP and #MachineLearning with @prof_smith in room $302."
    print(f"{bold('Input Text:')} {sample}\n")

    tokenizer = Tokenizer()
    # Register custom hashtag and mention rules
    tokenizer.add_rule(
        name="hashtag",
        pattern=r"#[A-Za-z0-9_]+",
        kind=TokenKind.SYMBOL,
        priority=10,
    )
    tokenizer.add_rule(
        name="mention",
        pattern=r"@[A-Za-z0-9_]+",
        kind=TokenKind.SYMBOL,
        priority=11,
    )

    tokens: list[Token] = tokenizer.tokenize(sample, detailed=True)  # type: ignore[assignment]
    print(f"{bold('Custom Token Extraction:')}")
    for t in tokens:
        if t.text.startswith(("#", "@")):
            print(f"  Custom entity matched: {bold(cyan(t.text))} (Kind: {t.kind.value})")


def demo_9_speed_benchmark() -> None:
    header("Live Performance & Throughput Benchmark", 9)
    sample = (
        "In 2026, natural language processing reached new frontiers across multilingual systems. "
        "Researchers published findings at https://nlp-proceedings.org/2026/paper?id=492. "
        "Datasets contained 1,250,000 sentences with 3.14159 ratio of annotated tokens. "
        "Users reported: 'We don't need heavy frameworks when lightweight solutions exist!' "
        "Supported scripts include Hindi (नमस्ते दुनिया) and emojis 🚀🔥. "
    )
    repeats = 2000
    total_text = sample * repeats
    size_mb = len(total_text.encode("utf-8")) / (1024 * 1024)

    print(f"Benchmarking on {repeats:,} repetitions ({size_mb:.2f} MB of mixed multilingual text)...")

    t0 = time.perf_counter()
    tokens = tokenize(total_text)
    elapsed = time.perf_counter() - t0

    throughput = size_mb / elapsed
    tokens_per_sec = len(tokens) / elapsed

    print(f"  {bold('Extracted Tokens:')}  {len(tokens):,}")
    print(f"  {bold('Execution Time:')}  {elapsed * 1000:.2f} ms")
    print(f"  {bold('Throughput:')}      {green(f'{throughput:.2f} MB/s')} ({len(total_text)/elapsed:,.0f} chars/sec)")
    print(f"  {bold('Token Rate:')}      {green(f'{tokens_per_sec:,.0f} tokens/sec')}")


def interactive_mode() -> None:
    header("Interactive Tokenizer Console (Panel Testing)", 10)
    print("You can now enter any custom sentence to test MyTokens live.")
    print("Type 'exit', 'quit', or press Ctrl+C to return.\n")

    tokenizer = Tokenizer(split_contractions=True, recognize_urls=True, recognize_emails=True)

    while True:
        try:
            user_input = input(bold(cyan("MyTokens > "))).strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting interactive demo. Thank you!")
                break

            tokens: list[Token] = tokenizer.tokenize(user_input, detailed=True)  # type: ignore[assignment]
            print(f"\nSimple:   {[t.text for t in tokens]}")
            print_table(tokens, user_input)
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting interactive demo. Thank you!")
            break


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================


def main() -> None:
    print(bold(cyan("\n" + "#" * 80)))

    # demo_1_split_vs_mytokens()
    # demo_2_detailed_tokens_and_offsets()
    # demo_3_protected_urls_and_emails()
    # demo_4_numbers_and_negative_values()
    # demo_5_contractions()
    # demo_6_multilingual_unicode()
    # demo_7_emojis_and_zwj()
    # demo_8_custom_rules()
    # demo_9_speed_benchmark()

    # Prompt user/panel if run in an interactive terminal
    if sys.stdin.isatty():
        interactive_mode()
    else:
        print("\n[Notice] Non-interactive environment detected. Skipping live input prompt.")


if __name__ == "__main__":
    main()
