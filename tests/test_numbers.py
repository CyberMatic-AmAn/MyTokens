"""Tests for number recognition, decimal formats, and edge cases."""

from mytokens import TokenKind, tokenize
from mytokens.utils import verify_token_spans


def test_integer_in_sentence() -> None:
    text = "I have 42 apples."
    assert tokenize(text) == ["I", "have", "42", "apples", "."]


def test_decimal_numbers() -> None:
    text = "Pi is approximately 3.14159 or 0.5 or .75"
    assert tokenize(text) == [
        "Pi",
        "is",
        "approximately",
        "3.14159",
        "or",
        "0.5",
        "or",
        ".75",
    ]


def test_scientific_notation() -> None:
    text = "The values are 1e10, 3.14e-5, and 2E+8."
    assert tokenize(text) == [
        "The",
        "values",
        "are",
        "1e10",
        ",",
        "3.14e-5",
        ",",
        "and",
        "2E+8",
        ".",
    ]


def test_formatted_thousands() -> None:
    text = "Revenue reached 1,000,000 and expenses were 12,345.67."
    tokens = tokenize(text, detailed=True)
    num_tokens = [t for t in tokens if t.kind == TokenKind.NUMBER]
    assert [t.text for t in num_tokens] == ["1,000,000", "12,345.67"]
    assert verify_token_spans(text, tokens) is True


def test_negative_numbers() -> None:
    text = "-42 is cold, temperature is -10.5 degrees"
    tokens = tokenize(text, detailed=True)
    assert tokens[0].text == "-42"
    assert tokens[0].kind == TokenKind.NUMBER
    num_tokens = [t for t in tokens if t.kind == TokenKind.NUMBER]
    assert [t.text for t in num_tokens] == ["-42", "-10.5"]
    assert verify_token_spans(text, tokens) is True


def test_subtraction_operator_vs_negative_number() -> None:
    text = "5-2 = 3"
    assert tokenize(text) == ["5", "-", "2", "=", "3"]
