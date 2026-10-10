"""0xylus: find flaky tests in CI history and check whether a fix worked."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("zeroxylus")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0+unknown"

__all__ = ["__version__"]
