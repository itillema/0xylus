"""The zoo's configurations, one planted root cause each, and where their tests live."""

from dataclasses import dataclass, replace

DEFAULT_RATE = 0.20
"""Per-run failure probability. At 30 runs it gives a 99.9% chance of at least one failure."""

CONTROL_PASSES = 10
CONTROL_FAILURES = 2
CONTROL_MODULE = "test_controls.py"


@dataclass(frozen=True)
class Layout:
    """Where one configuration's tests live in the generated suite."""

    module: str
    member_stem: str
    extras: tuple[str, ...] = ()
    """Tests in the module that aren't cluster members, such as Z1's polluter."""


LAYOUT: dict[str, Layout] = {
    "Z1": Layout("test_z1_order.py", "test_z1_victim", extras=("test_z1_polluter",)),
    "Z2": Layout("test_z2_async_timeout.py", "test_z2_wait"),
    "Z3": Layout("test_z3_resource.py", "test_z3_port"),
    "Z4": Layout("test_z4_clock.py", "test_z4_clock"),
    "Z5": Layout("test_z5_network.py", "test_z5_api"),
    "Z6": Layout("test_z6_unordered.py", "test_z6_order"),
    "Z7": Layout("test_z7_random.py", "test_z7_random"),
}


@dataclass(frozen=True)
class ZooConfig:
    """One planted root cause. Its member tests form one planted cluster.

    With `shared_fault`, one draw per run decides whether the shared resource fails, and then
    every member fails in that run. Without it, each member fails independently at `rate`, which
    makes a null control for clustering.
    """

    key: str
    cause: str
    stressor: str | None
    """The Phase 3 stressor that should reproduce this cause, if any."""
    size: int
    rate: float = DEFAULT_RATE
    shared_fault: bool = True

    def __post_init__(self) -> None:
        if self.key not in LAYOUT:
            raise ValueError(f"unknown zoo configuration {self.key!r}")
        if self.size < 1:
            raise ValueError(f"{self.key}: size must be at least 1, not {self.size}")
        if not 0.0 <= self.rate <= 1.0:
            raise ValueError(f"{self.key}: rate must be between 0 and 1, not {self.rate}")


DEFAULT_CONFIGS: tuple[ZooConfig, ...] = (
    ZooConfig("Z1", cause="test-order", stressor="order", size=3),
    ZooConfig("Z2", cause="async-timeout", stressor="cpu", size=3),
    ZooConfig("Z3", cause="resource-contention", stressor="parallel", size=2),
    ZooConfig("Z4", cause="time", stressor="time", size=2),
    ZooConfig("Z5", cause="network", stressor="network", size=4),
    ZooConfig("Z6", cause="unordered-collection", stressor="hashseed", size=2),
    ZooConfig("Z7", cause="unseeded-randomness", stressor=None, size=1),
)


def default_configs(*, rate: float = DEFAULT_RATE) -> tuple[ZooConfig, ...]:
    """Z1 to Z7 with their default sizes, all at the given failure rate."""
    return tuple(replace(config, rate=rate) for config in DEFAULT_CONFIGS)
