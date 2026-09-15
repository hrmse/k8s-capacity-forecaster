from capacity_forecaster.evaluator import Observation, evaluate


def observation(**overrides: object) -> Observation:
    values: dict[str, object] = {
        "namespace": "platform",
        "workload": "api",
        "container": "service",
        "request_millicores": 200,
        "limit_millicores": 400,
        "peak_millicores": 250,
        "p95_millicores": 230,
        "request_mebibytes": 256,
        "limit_mebibytes": 512,
        "peak_mebibytes": 200,
        "p95_mebibytes": 180,
    }
    values.update(overrides)
    return Observation(**values)  # type: ignore[arg-type]


def test_recommends_increase_from_observed_peak() -> None:
    result = evaluate(observation())

    assert result.state == "increase_review"
    assert result.cpu_request_millicores == 300
    assert result.memory_request_mebibytes == 240


def test_recommends_decrease_only_for_large_gap() -> None:
    result = evaluate(observation(request_millicores=1000, request_mebibytes=1024, peak_millicores=400))

    assert result.state == "decrease_review"
    assert result.cpu_request_millicores == 480


def test_missing_observations_never_recommend_resize() -> None:
    result = evaluate(observation(peak_mebibytes=None))

    assert result.state == "insufficient_data"
    assert result.cpu_request_millicores is None


def test_no_change_band_preserves_request() -> None:
    result = evaluate(observation(peak_millicores=150, p95_millicores=140, peak_mebibytes=180))

    assert result.state == "hold"
    assert result.cpu_request_millicores == 200
