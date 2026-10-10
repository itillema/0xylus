"""Every outcome pytest can report, so the fixtures show how each one is written."""

import logging
import sys
import unittest

import pytest


def test_passes():
    assert 1 + 1 == 2


def test_fails_with_assertion_diff():
    assert [1, 2, 3] == [1, 2, 4]


def test_raises_unexpected_error():
    raise ValueError("unexpected value: 42")


@pytest.fixture
def broken_setup():
    raise RuntimeError("database fixture failed to start")


def test_errors_in_setup(broken_setup):
    pass


@pytest.fixture
def broken_teardown():
    yield
    raise RuntimeError("cleanup failed")


def test_errors_in_teardown(broken_teardown):
    pass


def test_fails_and_errors_in_teardown(broken_teardown):
    raise AssertionError("the call failed as well")


@pytest.mark.skip(reason="not supported on this platform")
def test_skipped_by_marker():
    pass


def test_skips_at_runtime():
    pytest.skip("service unavailable")


@pytest.mark.xfail(reason="known bug 123")
def test_expected_failure():
    raise AssertionError("still broken")


@pytest.mark.xfail(reason="was flaky, maybe fixed")
def test_unexpected_pass():
    pass


@pytest.mark.xfail(reason="must keep failing", strict=True)
def test_unexpected_pass_strict():
    pass


def test_writes_output():
    print("line written to stdout")
    print("line written to stderr", file=sys.stderr)
    logging.getLogger("sample").warning("a warning-level log record")


def test_records_property(record_property):
    record_property("ticket", "ABC-1")


class TestAccount:
    def test_balance_starts_at_zero(self):
        assert 0 == 0

    class TestOverdraft:
        def test_is_refused(self):
            assert True


class LegacyStyleTests(unittest.TestCase):
    def test_legacy_pass(self):
        self.assertTrue(True)

    def test_legacy_fail(self):
        self.assertEqual("expected", "actual")
