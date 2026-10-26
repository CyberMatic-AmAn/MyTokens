"""Pytest test configuration and shared fixtures for MyTokens."""

import pytest

from mytokens import Tokenizer


@pytest.fixture
def default_tokenizer() -> Tokenizer:
    """Fixture providing a default Tokenizer instance."""
    return Tokenizer()


@pytest.fixture
def detailed_tokenizer() -> Tokenizer:
    """Fixture providing a Tokenizer configured for detailed Token objects."""
    return Tokenizer(split_contractions=True, preserve_whitespace=True)
