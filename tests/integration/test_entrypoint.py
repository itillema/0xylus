import shutil
import subprocess
import sysconfig

import pytest

from zeroxylus import __version__

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("command", ["0xylus", "zeroxylus"])
def test_installed_command_prints_version(command: str) -> None:
    scripts = sysconfig.get_path("scripts")
    executable = shutil.which(command, path=scripts)
    assert executable is not None, f"{command} is not installed in {scripts}"

    result = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, check=False, timeout=60
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"0xylus {__version__}"
