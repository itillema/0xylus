import re
from collections.abc import Callable

import pytest
from typer.testing import CliRunner

from zeroxylus import __version__, cli
from zeroxylus.errors import (
    ExitCode,
    InconclusiveError,
    InternalError,
    PolicyError,
    UsageError,
)

runner = CliRunner()

# ANSI control sequences (CSI). Typer styles its help output when it detects CI (GITHUB_ACTIONS)
# or FORCE_COLOR, which can split option names such as "--version" across escape codes.
_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _plain(text: str) -> str:
    return _ANSI.sub("", text)


def test_version_prints_program_name_and_version() -> None:
    result = runner.invoke(cli.app, ["--version"])

    assert result.exit_code == ExitCode.OK
    assert result.stdout == f"0xylus {__version__}\n"


def test_help_lists_the_version_option() -> None:
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == ExitCode.OK
    assert "--version" in _plain(result.stdout)


def test_no_arguments_shows_help_as_a_usage_error() -> None:
    result = runner.invoke(cli.app, [])

    assert result.exit_code == ExitCode.USAGE
    # Typer picks the stream for this help text; check what the user sees.
    assert "--version" in _plain(result.output)


def test_unknown_option_is_a_usage_error() -> None:
    result = runner.invoke(cli.app, ["--no-such-option"])

    assert result.exit_code == ExitCode.USAGE


def _app_raising(exc: Exception) -> Callable[..., None]:
    def fake_app(*args: object, **kwargs: object) -> None:
        raise exc

    return fake_app


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (PolicyError("guard blocked the fix"), ExitCode.POLICY_FAILURE),
        (UsageError("bad flag"), ExitCode.USAGE),
        (InternalError("invariant broken"), ExitCode.INTERNAL),
        (InconclusiveError("base rate not reproduced"), ExitCode.INCONCLUSIVE),
        (RuntimeError("unexpected"), ExitCode.INTERNAL),
    ],
)
def test_main_maps_errors_to_exit_codes(
    monkeypatch: pytest.MonkeyPatch, exc: Exception, expected: ExitCode
) -> None:
    monkeypatch.setattr(cli, "app", _app_raising(exc))

    with pytest.raises(SystemExit) as raised:
        cli.main()

    assert raised.value.code == expected


def test_main_reports_typed_errors_on_stderr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "app", _app_raising(PolicyError("guard blocked the fix")))

    with pytest.raises(SystemExit):
        cli.main()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "0xylus: error: guard blocked the fix\n"
