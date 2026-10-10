"""Command-line entry point. Kept thin: commands delegate to library code."""

import logging
import sys
from typing import Annotated

import typer

from zeroxylus import __version__
from zeroxylus.errors import ExitCode, ZeroxylusError

PROG_NAME = "0xylus"

logger = logging.getLogger(__name__)

app = typer.Typer(
    name=PROG_NAME,
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"{PROG_NAME} {__version__}")
        raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_print_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Find flaky tests, group tests that fail together, and check whether a fix worked."""


def main() -> None:
    """Run the CLI and turn errors into the documented exit codes.

    Typer exits with 0 for --help and --version, 2 for usage errors and 130 on Ctrl-C.
    Typed errors exit with their own code; anything else is a bug and exits with 3.
    """
    try:
        app(prog_name=PROG_NAME)
    except ZeroxylusError as exc:
        typer.echo(f"{PROG_NAME}: error: {exc}", err=True)
        sys.exit(exc.exit_code)
    except Exception:
        logger.exception("%s: internal error", PROG_NAME)
        sys.exit(ExitCode.INTERNAL)
