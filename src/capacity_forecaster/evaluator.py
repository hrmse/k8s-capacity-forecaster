"""Pure, deterministic capacity recommendation logic."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Observation:
    namespace: str
    workload: str
    container: str
    request_millicores: int
    limit_millicores: int | None
    peak_millicores: int | None
    p95_millicores: int | None
    request_mebibytes: int
    limit_mebibytes: int | None
    peak_mebibytes: int | None
    p95_mebibytes: int | None


@dataclass(frozen=True)
class Recommendation:
    namespace: str
    workload: str
    container: str
    state: str
    cpu_request_millicores: int | None
    memory_request_mebibytes: int | None
    rationale: str


def rounded_with_buffer(value: int, buffer: float, quantum: int) -> int:
    buffered = int(value * (1 + buffer) + 0.999999)
    return ((buffered + quantum - 1) // quantum) * quantum


def assess_dimension(request: int, peak: int | None, p95: int | None, buffer: float, quantum: int) -> int | None:
    if peak is None or p95 is None:
        return None
    # Peak captures burst risk; p95 avoids reducing a workload with sustained demand.
    target = max(peak, p95)
    return rounded_with_buffer(target, buffer, quantum)


def evaluate(observation: Observation, buffer: float = 0.20) -> Recommendation:
    if buffer < 0 or buffer > 1:
        raise ValueError("buffer must be between 0 and 1")
    cpu_target = assess_dimension(
        observation.request_millicores,
        observation.peak_millicores,
        observation.p95_millicores,
        buffer,
        10,
    )
    memory_target = assess_dimension(
        observation.request_mebibytes,
        observation.peak_mebibytes,
        observation.p95_mebibytes,
        buffer,
        16,
    )
    identity = {
        "namespace": observation.namespace,
        "workload": observation.workload,
        "container": observation.container,
    }
    if cpu_target is None or memory_target is None:
        return Recommendation(
            **identity,
            state="insufficient_data",
            cpu_request_millicores=None,
            memory_request_mebibytes=None,
            rationale="Peak and p95 observations are required for both CPU and memory.",
        )
    if cpu_target > observation.request_millicores or memory_target > observation.request_mebibytes:
        return Recommendation(
            **identity,
            state="increase_review",
            cpu_request_millicores=cpu_target,
            memory_request_mebibytes=memory_target,
            rationale="Observed demand plus safety buffer exceeds at least one declared request.",
        )
    # Reductions demand a sizeable gap so small sample variation cannot trigger churn.
    if cpu_target <= observation.request_millicores * 0.70 and memory_target <= observation.request_mebibytes * 0.70:
        return Recommendation(
            **identity,
            state="decrease_review",
            cpu_request_millicores=cpu_target,
            memory_request_mebibytes=memory_target,
            rationale="Both buffered targets are at least 30% below declared requests; review before changing.",
        )
    return Recommendation(
        **identity,
        state="hold",
        cpu_request_millicores=observation.request_millicores,
        memory_request_mebibytes=observation.request_mebibytes,
        rationale="Buffered targets are within the no-change band.",
    )


def recommendation_dict(recommendation: Recommendation) -> dict[str, object]:
    return asdict(recommendation)
