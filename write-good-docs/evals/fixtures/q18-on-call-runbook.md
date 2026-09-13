## Draft

Queues are fundamental to distributed systems. QUEUE_LAG_HIGH is an alert that could happen for various reasons. Check things, then consider a restart. Do not forget to verify.

## Verified operational facts

The alert means the oldest unprocessed job is more than 600 seconds old; queued deliveries are delayed. Required access: on-call operator for project demo.
First collect `queuectl inspect --project demo`; retain its output before any mutation. The output includes `paused=true` or `paused=false`. If paused=true and the change owner approves, run `queuectl resume --project demo`. Otherwise stop and escalate to the incident lead; no other remediation is established here. Do not restart workers: doing so loses diagnostic state. Verify with `queuectl inspect --project demo`. Recovery requires `oldest_age_s` below 60 for three consecutive checks taken one minute apart. If recovery is not observed within 10 minutes after resuming, escalate to the incident lead. No destructive cleanup is authorized.
