# Contributing to MyTokens

Thank you for your interest in contributing to **MyTokens**! We welcome bug reports, feature suggestions, documentation enhancements, and code contributions.

## Development Setup

1. Clone the repository and navigate into the root directory:
   ```bash
   git clone https://github.com/CyberMatic-AmAn/MyTokens.git
   cd MyTokens
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in editable mode with development dependencies:
   ```bash
   pip install -e .[dev,benchmark]
   ```

## Running Tests

Run the test suite using `pytest`:
```bash
pytest
```

## Code Quality Standards

Before submitting a pull request, verify that:
1. All unit tests pass (`pytest`).
2. Type checking passes without errors (`mypy src`).
3. Code conforms to style guides (`ruff check .` and `ruff format --check .`).
4. Any new feature includes corresponding unit tests and documentation updates.
5. Invariants (e.g., token offsets matching slice `source[token.start:token.end]`) are maintained.

## Commit Guidelines

We use conventional commit messages:
- `feat: ...` for new features
- `fix: ...` for bug fixes
- `docs: ...` for documentation improvements
- `test: ...` for adding or improving tests
- `perf: ...` for performance optimizations
