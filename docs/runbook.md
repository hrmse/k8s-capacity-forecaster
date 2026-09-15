# Capacity review runbook

1. Generate a snapshot from reviewed Prometheus queries over a representative
   period, including seasonal/peak traffic where applicable.
2. Run the forecaster and attach both input and output to a pull request.
3. For `increase_review`, inspect throttling, OOM events, HPA behaviour and
   node headroom before changing a request.
4. For `decrease_review`, confirm no startup, batch or disaster-recovery peak
   is absent from the window; apply one change at a time.
5. Roll out via GitOps, observe error rate, latency, throttling and scheduling
   for an agreed window, then retain the evidence with the change record.

Never treat a `hold` state as proof of correctness. It only says the supplied
numbers did not cross this tool’s conservative review thresholds.
