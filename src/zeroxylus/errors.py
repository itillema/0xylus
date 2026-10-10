"""Typed errors and the process exit codes they map to."""

from enum import IntEnum
from typing import ClassVar


class ExitCode(IntEnum):
    """Exit codes shared by every command."""

    OK = 0
    POLICY_FAILURE = 1
    """A policy check failed, such as a validation FAIL or a guard BLOCK."""
    USAGE = 2
    """The command line or the configuration is invalid."""
    INTERNAL = 3
    """A bug: something inside the tool went wrong."""
    INCONCLUSIVE = 4
    """Validation could not decide, for example because the base rate could not be reproduced."""


class ZeroxylusError(Exception):
    """Base class for errors that end a command with a specific exit code."""

    exit_code: ClassVar[ExitCode] = ExitCode.INTERNAL


class UsageError(ZeroxylusError):
    """The command line is invalid."""

    exit_code = ExitCode.USAGE


class ConfigError(UsageError):
    """The configuration file or environment is invalid."""


class InputError(ZeroxylusError):
    """An input file is unsafe, malformed or too large to process."""

    exit_code = ExitCode.USAGE


class UnsafeXMLError(InputError):
    """An XML document uses a DTD, entity declarations or external references, which are refused."""


class MalformedInputError(InputError):
    """An input file is not well-formed, or is not the kind of document expected."""


class InputTooLargeError(InputError):
    """An input file is larger than the size limit."""


class PolicyError(ZeroxylusError):
    """A policy check failed, such as a validation FAIL or a guard BLOCK."""

    exit_code = ExitCode.POLICY_FAILURE


class InconclusiveError(ZeroxylusError):
    """Validation could not reach a verdict."""

    exit_code = ExitCode.INCONCLUSIVE


class InternalError(ZeroxylusError):
    """An internal invariant did not hold."""

    exit_code = ExitCode.INTERNAL
