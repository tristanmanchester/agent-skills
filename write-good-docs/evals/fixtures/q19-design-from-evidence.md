## Existing policy

The complete policy contract for release 7.2 permits three total attempts per message, including the initial attempt. Exhausted messages enter the failure queue. Delay between attempts is 2 s.

## Experiment report E1

An isolated, supplied experiment replayed 120 recorded transient failures. The three-attempt policy recovered 90; a five-attempt variant recovered 108. No permanent failures were included. The report contains no latency, capacity, cost, or production measurements.

## Proposed change

Use five total attempts, retain the 2 s delay, and retain the failure queue after exhaustion. The proposal is unapproved. No rollout plan, rollback mechanism, owner, or success threshold has been agreed. The next decision is whether to run a broader experiment, not whether to deploy.
