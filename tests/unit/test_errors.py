import pytest

from zeroxylus.errors import (
    ConfigError,
    ExitCode,
    InconclusiveError,
    InternalError,
    PolicyError,
    UsageError,
    ZeroxylusError,
)


def test_exit_codes_match_the_documented_table() -> None:
    assert {code.name: code.value for code in ExitCode} == {
        "OK": 0,
        "POLICY_FAILURE": 1,
        "USAGE": 2,
        "INTERNAL": 3,
        "INCONCLUSIVE": 4,
    }


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ZeroxylusError, ExitCode.INTERNAL),
        (UsageError, ExitCode.USAGE),
        (ConfigError, ExitCode.USAGE),
        (PolicyError, ExitCode.POLICY_FAILURE),
        (InconclusiveError, ExitCode.INCONCLUSIVE),
        (InternalError, ExitCode.INTERNAL),
    ],
)
def test_each_error_carries_its_exit_code(error: type[ZeroxylusError], expected: ExitCode) -> None:
    assert error.exit_code is expected
