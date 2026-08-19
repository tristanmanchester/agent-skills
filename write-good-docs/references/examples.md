# Examples

Use these patterns to guide judgment. Adapt them to the project's terminology and facts; do not copy them mechanically.

## Lead with the answer

Before:

> This document provides an overview of how you can configure request retries in the client. There are several settings that can be used to customize retry behavior.

After:

> Configure request retries with `maxAttempts` and `backoff`. The default policy retries transient failures three times.

Why it is better: the reader gets the task and the controlling facts immediately. The second sentence is valid only when the defaults are verified.

## Put the condition first

Before:

> Create a private endpoint before continuing if your deployment doesn't have public network access.

After:

> If your deployment doesn't have public network access, create a private endpoint before you continue.

## Make the actor explicit

Before:

> The token is refreshed after it expires.

After, when the client acts:

> The client refreshes the token after it expires.

After, when the actor is unknown or unimportant:

> The token refreshes after it expires.

Choose the version that matches the verified behavior.

## Replace vague requirements

Before:

> The database should be healthy before deployment.

After:

> Before deployment, run `dbctl ready`. Continue only when the command returns `ready=true`.

Why it is better: the reader knows the requirement, action, and evidence.

## Remove an empty introduction

Before:

> In modern distributed systems, observability is an increasingly important topic. This section discusses the various observability features available in the service.

After:

> The service exports request latency, error rate, and queue depth as OpenTelemetry metrics.

## Prefer one useful paragraph to bullet soup

Before:

- **Authentication:** Authentication uses workload identity.
- **Authorization:** Authorization uses project roles.
- **Expiration:** Tokens expire after one hour.

After:

> Workload identity authenticates the caller, and project roles authorize each request. Access tokens expire after one hour.

Use the list only when readers need to compare or look up the three attributes independently.

## Keep warnings next to risk

Before:

> Delete the namespace with `clusterctl delete namespace NAME`.
>
> Note: This deletes all workloads in the namespace.

After:

> **Caution:** Deleting the namespace permanently deletes all workloads in it.
>
> Run:
>
> ```bash
> clusterctl delete namespace NAME
> ```

## Separate fact, inference, and proposal

Before:

> The worker probably retries indefinitely, so we should add a dead-letter queue.

After:

> The worker calls `retry()` without an attempt limit in `worker.ts`. This indicates that a permanently failing message can remain in the queue indefinitely. The proposal adds a dead-letter queue after five failed attempts.

The inference remains identifiable, and the proposal is not presented as current behavior.

## Give a design document an actual decision

Before:

> There are several possible approaches to session storage. Redis, PostgreSQL, and in-memory storage each have pros and cons.

After:

> Store sessions in PostgreSQL for the first release. It already meets the required durability and operational constraints, and the expected load does not justify a separate Redis dependency. Revisit this decision if measured session traffic exceeds 2,000 writes per second.

The threshold must come from evidence or be marked as a proposed decision criterion.

## Write reference entries by behavior

Before:

> `listJobs` lists jobs.

After:

> `listJobs` returns the jobs visible to the caller, ordered by creation time in descending order. Use `pageToken` to retrieve additional pages.

## Make troubleshooting observable

Before:

> If synchronization fails, check the configuration and restart the service.

After:

> If the log contains `AUTH_SCOPE_MISSING`, compare `SYNC_SCOPES` with the required scope list. Add the missing scope, restart the worker, and confirm that the next synchronization records `status=completed`.

## Preserve exact literals during a prose edit

Source:

> Set `retry_count` to `5` and click **Apply Changes**.

Safe edit:

> Set `retry_count` to `5`, and then click **Apply Changes**.

Unsafe edit without verification:

> Set `retryCount` to `5`, and then click **Apply**.

## Avoid a repeated conclusion

Before:

> The migration is zero-downtime because both schemas remain readable during rollout.
>
> ...
>
> ## Conclusion
>
> In conclusion, this approach enables a zero-downtime migration by keeping both schemas readable during rollout.

After:

> During rollout, readers accept both schemas. Writers switch to the new schema only after all readers are compatible.

State the mechanism once, where it belongs. Do not repeat the claim as a conclusion.

## Comment the reason, not the syntax

Before:

```ts
// Increment retryCount by one.
retryCount += 1;
```

After:

```ts
// The provider counts the initial request as attempt 1.
retryCount += 1;
```

Keep the comment only if that convention is non-obvious and consequential.
