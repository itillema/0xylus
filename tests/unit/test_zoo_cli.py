from pathlib import Path

import pytest

from benchmarks.zoo.__main__ import apply_override, main
from benchmarks.zoo.configs import DEFAULT_CONFIGS


def _config(configs: tuple[object, ...], key: str) -> object:
    return next(config for config in configs if getattr(config, "key", None) == key)


def test_overrides_change_one_field_of_one_configuration() -> None:
    configs = apply_override(DEFAULT_CONFIGS, "z3.rate=0.5")
    configs = apply_override(configs, "Z3.size=4")
    configs = apply_override(configs, "Z5.shared_fault=false")

    by_key = {config.key: config for config in configs}
    assert (by_key["Z3"].rate, by_key["Z3"].size) == (0.5, 4)
    assert by_key["Z5"].shared_fault is False
    unchanged = [config for config in configs if config.key not in {"Z3", "Z5"}]
    assert unchanged == [config for config in DEFAULT_CONFIGS if config.key not in {"Z3", "Z5"}]


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("Z3", "expected KEY.FIELD=VALUE"),
        ("Z3.rate", "expected KEY.FIELD=VALUE"),
        ("Z9.rate=0.1", "unknown configuration"),
        ("Z3.colour=red", "unknown field"),
        ("Z3.rate=lots", "could not convert"),
        ("Z3.rate=2", "rate must be between 0 and 1"),
        ("Z3.shared_fault=maybe", "expected true or false"),
    ],
)
def test_bad_overrides_are_refused(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        apply_override(DEFAULT_CONFIGS, text)


def test_no_run_writes_the_suite_without_running_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["--seed", "2", "--runs", "3", "--out", str(tmp_path), "--no-run"])

    assert exit_code == 0
    assert (tmp_path / "suite" / "manifest.json").is_file()
    assert not (tmp_path / "junit").exists()
    assert "3 runs planned" in capsys.readouterr().out


def test_invalid_arguments_exit_with_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--set", "Z9.rate=0.1", "--no-run"])

    assert raised.value.code == 2
    assert "unknown configuration" in capsys.readouterr().err
