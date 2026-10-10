"""Parametrized tests, including ids and messages that reports must escape."""

import pytest


@pytest.mark.parametrize("value", [1, 2, 3])
def test_ids_from_values(value):
    assert value != 2


@pytest.mark.parametrize(
    "text",
    [
        "<script>alert(1)</script>",
        "pipe | in | a table",
        "@maintainer please look",
        "%0A encoded newline",
        "back`ticks`",
        "right-to-left \u202e override",
        "x" * 200,
    ],
)
def test_hostile_ids(text):
    assert text


def test_fails_with_hostile_message():
    raise AssertionError("<b>bold</b> | @here `code` %0A \u202edesrever")
