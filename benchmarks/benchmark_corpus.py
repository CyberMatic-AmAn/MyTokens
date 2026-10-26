"""Large-scale corpus benchmark measuring throughput and memory scaling."""

from __future__ import annotations

import gc
import os
import platform
import sys
import time
import tracemalloc

from mytokens import tokenize

BASE_TEXT = (
    "In 2026, natural language processing reached new frontiers across multilingual systems. "
    "Researchers published findings at https://nlp-proceedings.org/2026/paper?id=492. "
    "Datasets contained 1,250,000 sentences with 3.14159 ratio of annotated tokens. "
    "Users reported: 'We don't need complex heavy libraries when lightweight solutions exist!' "
    "Supported scripts include Hindi (नमस्ते दुनिया), Japanese (こんにちは世界), and Chinese (你好世界). "
    "Emails like author@university.edu and modern emojis like 🚀 and 📊 were correctly segmented.\n"
)


def generate_corpus(target_size_kb: int) -> str:
    """Generates synthetic corpus of approximate size in KB."""
    repeats = max(1, (target_size_kb * 1024) // len(BASE_TEXT.encode("utf-8")))
    return BASE_TEXT * repeats


def run_corpus_benchmark() -> None:
    print("=" * 80)
    print("MYTOKENS CORPUS SCALING & MEMORY BENCHMARK")
    print("=" * 80)
    print(f"Python Version: {platform.python_version()} on {platform.system()}")
    print("-" * 80)

    sizes_kb = [10, 100, 1000]

    for size_kb in sizes_kb:
        corpus = generate_corpus(size_kb)
        actual_bytes = len(corpus.encode("utf-8"))
        actual_chars = len(corpus)
        size_label = f"{actual_bytes / 1024:.1f} KB" if actual_bytes < 1024 * 1024 else f"{actual_bytes / (1024 * 1024):.2f} MB"

        print(f"\nCorpus Size: {size_label} ({actual_chars:,} characters)")

        tokenize(corpus[:1000])
        gc.collect()

        tracemalloc.start()
        t0 = time.perf_counter()
        tokens = tokenize(corpus)
        elapsed = time.perf_counter() - t0
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        throughput_mb = (actual_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        tokens_per_sec = len(tokens) / elapsed if elapsed > 0 else 0

        print(f"  Token count:     {len(tokens):,}")
        print(f"  Elapsed time:    {elapsed * 1000:.2f} ms")
        print(f"  Throughput:      {throughput_mb:.2f} MB/s ({actual_chars / elapsed:,.0f} chars/s)")
        print(f"  Tokens/second:   {tokens_per_sec:,.0f}")
        print(f"  Peak memory:     {peak / 1024:.2f} KB")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_corpus_benchmark()
