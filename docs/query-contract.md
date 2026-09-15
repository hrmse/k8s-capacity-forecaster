# Prometheus query contract

The collector feeding this tool should query a representative time window and
normalize each container into the schema in `examples/workload-snapshot.json`.
Recommended source signals:

| Field | Typical source | Notes |
| --- | --- | --- |
| `request_millicores` | kube-state-metrics `kube_pod_container_resource_requests` | Sum/aggregate after mapping pods to the workload. |
| `peak_millicores` | `max_over_time(rate(container_cpu_usage_seconds_total[5m])[14d:5m])` | Choose a window matching service seasonality. |
| `p95_millicores` | `quantile_over_time(0.95, rate(container_cpu_usage_seconds_total[5m])[14d:5m])` | Review query cardinality and aggregation. |
| memory equivalents | `container_memory_working_set_bytes` plus request/limit metrics | Working set is generally safer than cache-heavy usage. |

The tool intentionally does not hard-code PromQL because workload ownership,
recording rules and label conventions vary. Persist the exact query and time
window beside every review report.
