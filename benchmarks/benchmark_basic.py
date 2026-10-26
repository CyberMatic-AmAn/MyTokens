"""Benchmark suite measuring throughput and latency across standard NLP scenarios."""

from __future__ import annotations

import platform
import sys
import time
from typing import Any

from mytokens import tokenize

SAMPLE_SHORT = "Hello, world! I'm learning NLP with MyTokens."

SAMPLE_PARAGRAPH = """
Natural Language Processing (NLP) enables computers to understand human languages.
Visit https://example.com/nlp-guide?v=2 for updates! Contact us at support@nlp-hub.org.
Pi is ~3.14159, and 1,000,000 tokens are processed in 0.05s.
Emojis like ❤️ and 🚀 make text modern and vibrant.
"""

SAMPLE_UNICODE = """
नमस्ते दुनिया! Welcome to natural language processing.
こんにちは世界。你好世界。
The café résumé contains naïve assertions.
"""

CORPORA = {
    "Short Sentence": SAMPLE_SHORT,
    "Mixed Paragraph (URLs, Emails, Numbers)": SAMPLE_PARAGRAPH,
    "Multilingual Unicode": SAMPLE_UNICODE,
}


def run_benchmark(iterations: int = 1000) -> None:
    print("=" * 80)
    print("MYTOKENS PERFORMANCE BENCHMARK")
    print("=" * 80)
    print(f"Python Version: {platform.python_version()} ({platform.python_implementation()})")
    print(f"OS:             {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Iterations:     {iterations:,}")
    print("-" * 80)

    nltk_available = False
    nltk_version = "N/A"
    try:
        import nltk  # type: ignore[import-not-found]
        from nltk.tokenize import word_tokenize  # type: ignore[import-not-found]

        word_tokenize("test sentence")
        nltk_available = True
        nltk_version = nltk.__version__
    except Exception:
        nltk_available = False

    print(f"NLTK Available: {nltk_available} (Version: {nltk_version})")
    print("-" * 80)

    for name, text in CORPORA.items():
        total_chars = len(text) * iterations
        print(f"\nScenario: {name} (Text size: {len(text)} chars)")

        # 1. Python str.split() baseline
        t0 = time.perf_counter()
        split_tokens = 0
        for _ in range(iterations):
            tokens = text.split()
            split_tokens += len(tokens)
        t_split = time.perf_counter() - t0
        tp_split = total_chars / t_split if t_split > 0 else 0
        print(f"  [str.split() baseline]")
        print(f"    Latency:    {t_split / iterations * 1000:.4f} ms/run")
        print(f"    Throughput: {tp_split / 1_000_000:.2f} MB/s ({tp_split:,.0f} chars/s)")
        print(f"    Tokens/s:   {split_tokens / t_split:,.0f}")

        # 2. MyTokens default mode
        t0 = time.perf_counter()
        mytokens_tokens = 0
        for _ in range(iterations):
            tokens = tokenize(text)
            mytokens_tokens += len(tokens)
        t_mytokens = time.perf_counter() - t0
        tp_mytokens = total_chars / t_mytokens if t_mytokens > 0 else 0
        print(f"  [MyTokens (Default Tokenizer)]")
        print(f"    Latency:    {t_mytokens / iterations * 1000:.4f} ms/run")
        print(f"    Throughput: {tp_mytokens / 1_000_000:.2f} MB/s ({tp_mytokens:,.0f} chars/s)")
        print(f"    Tokens/s:   {mytokens_tokens / t_mytokens:,.0f}")

        # 3. MyTokens detailed mode
        t0 = time.perf_counter()
        detailed_tokens = 0
        for _ in range(iterations):
            tokens = tokenize(text, detailed=True)
            detailed_tokens += len(tokens)
        t_detailed = time.perf_counter() - t0
        tp_detailed = total_chars / t_detailed if t_detailed > 0 else 0
        print(f"  [MyTokens (Detailed Mode with Offsets)]")
        print(f"    Latency:    {t_detailed / iterations * 1000:.4f} ms/run")
        print(f"    Throughput: {tp_detailed / 1_000_000:.2f} MB/s ({tp_detailed:,.0f} chars/s)")
        print(f"    Tokens/s:   {detailed_tokens / t_detailed:,.0f}")

        # 4. NLTK word_tokenize (if installed)
        if nltk_available:
            try:
                t0 = time.perf_counter()
                nltk_tokens = 0
                for _ in range(iterations):
                    tokens = word_tokenize(text)
                    nltk_tokens += len(tokens)
                t_nltk = time.perf_counter() - t0
                tp_nltk = total_chars / t_nltk if t_nltk > 0 else 0
                print(f"  [NLTK word_tokenize]")
                print(f"    Latency:    {t_nltk / iterations * 1000:.4f} ms/run")
                print(f"    Throughput: {tp_nltk / 1_000_000:.2f} MB/s ({tp_nltk:,.0f} chars/s)")
                print(f"    Tokens/s:   {nltk_tokens / t_nltk:,.0f}")
            except Exception as e:
                print(f"  [NLTK word_tokenize]: Skipped ({e})")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_benchmark(iterations=1000)
