# Threat model

| Risk | Control | Boundary |
| --- | --- | --- |
| Bad/missing telemetry drives a resize | Missing signals produce `insufficient_data`; changes require review. | Query validity and Prometheus retention are external responsibilities. |
| Small variation causes churn | Targets include a buffer and decreases require a 30% gap on both dimensions. | Workload-specific behaviour still needs engineering judgement. |
| Tool directly affects workloads | The CLI has no Kubernetes credentials or mutation path. | A later GitOps change needs its own approval and policy controls. |
| Report is overwritten during collection | Output writes are atomic. | Artifact retention/access control belongs to the surrounding CI/storage system. |
