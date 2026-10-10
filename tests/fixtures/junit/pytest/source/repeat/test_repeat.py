"""Targets for pytest-repeat's --count, with and without parametrization."""

import pytest


def test_repeated():
    assert True


@pytest.mark.parametrize("n", [1, 2])
def test_repeated_with_params(n):
    assert n
