"""Deterministic flaky tests for pytest-rerunfailures: reruns happen in the same process."""

import pytest

_attempts = {}


def _attempt(name):
    _attempts[name] = _attempts.get(name, 0) + 1
    return _attempts[name]


def test_passes():
    assert True


def test_fails_once_then_passes():
    assert _attempt("once") > 1, "the first attempt fails"


def test_fails_twice_then_passes():
    assert _attempt("twice") > 2, "fails until the third attempt"


def test_always_fails():
    raise AssertionError("fails on every attempt")


@pytest.fixture
def setup_fails_once():
    if _attempt("setup") == 1:
        raise RuntimeError("setup fails on the first attempt")


def test_setup_error_once(setup_fails_once):
    pass
