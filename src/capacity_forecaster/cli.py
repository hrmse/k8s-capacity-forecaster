"""Command-line interface for deterministic capacity report generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from capacity_forecaster.evaluator import Observation, evaluate, recommendation_dict

STATE_VALUE = {"insufficient_data": 0, "hold": 1, "increase_review": 2, "decrease_review": 3}


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def render_metrics(report: list[dict[str, object]]) -> str:
    lines = [
        "# HELP capacity_forecaster_recommendation_state Recommendation state (0 insufficient, 1 hold, 2 increase, 3 decrease).",
        "# TYPE capacity_forecaster_recommendation_state gauge",
    ]
    for item in report:
        labels = ",".join(
            f'{key}="{item[key]}"' for key in ("namespace", "workload", "container", "state")
        )
        lines.append(f"capacity_forecaster_recommendation_state{{{labels}}} {STATE_VALUE[str(item['state'])]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--buffer", default=0.20, type=float)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    report = [recommendation_dict(evaluate(Observation(**item), args.buffer)) for item in payload["observations"]]
    atomic_write(args.report, json.dumps({"recommendations": report}, indent=2, sort_keys=True) + "\n")
    atomic_write(args.metrics, render_metrics(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
