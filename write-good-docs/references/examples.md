# Evidence-preserving editing examples

Every product, system, command, and measurement below is a fictional teaching fixture. Each example states the evidence available for the change. These are not runnable instructions or reusable product facts. Different faithful wording is welcome.

## 1. Improve expression without adding facts

**Mode:** prose-only edit. **Evidence:** the original sentence only.

Original:

> This document provides an overview of how you can configure request retries in the client.

Revision:

> You can configure request retries in the client.

The revision does not add setting names, failure categories, or defaults. It remains limited because its source is limited.

## 2. Add useful detail only when supplied

**Mode:** evidence-enriched rewrite. **Verified facts:** `maxAttempts` includes the initial request; its default is `4`. `backoff` controls the delay between attempts. The default policy retries transient failures only.

Original:

> There are several settings that can be used to customize retry behavior.

Revision:

> Use `maxAttempts` to set the total number of attempts, including the initial request, and `backoff` to control the delay between attempts. By default, the client makes up to four attempts for transient failures.

Without those facts, do not supply the parameter names or default. The distinction between attempts and retries must survive the rewrite.

## 3. Put a condition before an instruction

**Mode:** prose-only edit. **Evidence:** the original sentence only.

Original:

> Create a private endpoint before continuing if your deployment doesn't have public network access.

Revision:

> If your deployment doesn't have public network access, create a private endpoint before you continue.

No product behavior or prerequisite was added.

## 4. Keep an appropriate passive construction

**Mode:** prose-only edit. **Context:** the paragraph is about token lifecycle; the actor is unspecified and unimportant to the reader.

Original and revision:

> The token is refreshed after it expires.

Leave it alone. If a separate source identifies the client and responsibility matters, "The client refreshes the token after it expires" is an evidence-enriched alternative, not a stylistic guess.

## 5. Turn a vague prerequisite into an observable one

**Mode:** evidence-enriched rewrite. **Verified facts:** the database must be ready before deployment; `dbctl ready` checks readiness; output `ready=true` is the required condition.

Original:

> The database should be healthy before deployment.

Revision:

> Before deployment, run `dbctl ready`. Continue only when the command returns `ready=true`.

Without those facts, the command and output are unknown, and the meaning of "should" needs clarification. Do not invent a health check.

## 6. Make reference behavior explicit

**Mode:** evidence-enriched rewrite. **Verified facts:** `listJobs` returns jobs visible to the caller, newest first. It accepts `pageToken` to retrieve additional pages.

Original:

> `listJobs` lists jobs.

Revision:

> `listJobs` returns jobs visible to the caller, newest first. Use `pageToken` to retrieve additional pages.

**Without the verified facts:** retain the limited description and, when needed, flag visibility, ordering, and pagination as facts to verify. Do not fabricate an informative reference entry.

## 7. Keep an observation narrower than the system

**Mode:** evidence-enriched rewrite. **Evidence:** `worker.ts` calls `retry()` without an explicit limit; the retry implementation and effective queue configuration have not been supplied. An unapproved proposal suggests a dead-letter queue after five failed attempts.

Original:

> The worker probably retries indefinitely, so we should add a dead-letter queue.

Revision:

> No attempt limit is specified at this call site in `worker.ts`. Check the retry implementation and queue configuration to establish the effective limit. The proposal would move messages to a dead-letter queue after five failed attempts.

The call site does not establish unlimited retries, and the proposal remains a proposal.

## 8. Preserve a requirement–implementation conflict

**Mode:** evidence-enriched rewrite. **Evidence:** the applicable specification requires 30-day retention. The supplied deployment configuration sets retention to 7 days. No deployed runtime observation is supplied.

Revision:

> The specification requires 30-day retention; the supplied deployment configuration sets 7 days.

Do not report either value alone as the verified retention of all deployments.

## 9. State uncertainty directly

**Mode:** prose-only edit. **Evidence:** the draft fully states the observation and limitation.

Original:

> I would not claim that these peaks uniquely identify phase A. The observed peaks are consistent with either phase A or phase B, and this measurement cannot distinguish them.

Revision:

> The observed peaks are consistent with either phase A or phase B; this measurement does not distinguish them.

The author-centered caution disappears; the material uncertainty and negative finding remain.

## 10. Remove an unsupported consequence

**Mode:** evidence-checked edit. **Verified fact:** the server stores encrypted objects. No security assessment or reliability evidence is supplied.

Original:

> The server stores encrypted objects, ensuring a secure and reliable experience.

Revision:

> The server stores encrypted objects.

Do not replace "ensuring" with "helping to provide." The wider claim would still lack support.

## 11. Connect established facts

**Mode:** prose-only edit. **Evidence:** a lease prevents other workers from claiming a job until expiry; expiry does not stop the original worker, and a second worker can then claim and execute the job.

Original:

> The lease expires. The original worker may still be running. A second worker can claim the job. Both workers can execute it.

Revision:

> When the lease expires, another worker can claim the job. If the original worker is still running, both workers can execute it.

The connective structure makes the existing relationship easier to follow without adding a new mechanism.

## 12. Use prose for a connected explanation

**Mode:** prose-only edit. **Evidence:** the three original statements.

Original:

- Workload identity authenticates the caller.
- Project roles authorize each request.
- Access tokens expire after one hour.

Revision:

> Workload identity authenticates the caller, and project roles authorize each request. Access tokens expire after one hour.

Keep the list instead when readers need to look up these attributes independently.

## 13. Put an established warning before risk

**Mode:** prose-only edit. **Evidence:** all effects are explicitly stated in the original.

Original:

> Run `clusterctl delete namespace NAME`. This permanently deletes all workloads in that namespace. Obtain the incident lead's approval first. Replace `NAME` with the affected namespace.

Revision:

> Obtain the incident lead's approval before continuing. Deleting the namespace permanently deletes all workloads in it.
>
> Run `clusterctl delete namespace NAME`. Replace `NAME` with the affected namespace.

The warning and approval move before the command. This example does not authorize executing it.

## 14. Make troubleshooting observable from evidence

**Mode:** evidence-enriched rewrite. **Verified facts:** `AUTH_SCOPE_MISSING` identifies an absent required scope; `SYNC_SCOPES` contains configured scopes; the project's required-scope list is the comparison source. Added scopes take effect after worker restart. A successful run records `status=completed`.

Original:

> If synchronization fails, check the configuration and restart the service.

Revision:

> If the log contains `AUTH_SCOPE_MISSING`, compare `SYNC_SCOPES` with the project's required-scope list. Add the missing scope, restart the worker, and confirm that the next synchronization records `status=completed`.

This applies to the stated error, not every synchronization failure. Without the verified facts, do not invent the diagnostic or remedy.

## 15. Preserve good writing and exact literals

**Mode:** local prose edit. **Context:** the wording is already clear and suitable for the audience.

Original and revision:

> Set `retry_count` to `5`, and then click **Apply Changes**.

No change is necessary. `retryCount` and **Apply** would be different literals, not improvements in style.

## 16. Remove an empty comment rather than invent a reason

**Mode:** comments-only edit. **Evidence:** the snippet only; no provider convention or rationale is supplied.

Original:

```ts
// Increment retryCount by one.
retryCount += 1;
```

Revision:

```ts
retryCount += 1;
```

Do not invent a provider-specific reason for incrementing. If a verified, non-obvious rationale matters, add it from that evidence.

## 17. Keep useful specialist language

**Mode:** prose-only edit. **Context:** a numerical-methods audience already knows what a robust estimator is.

Original and revision:

> The routine uses a robust estimator.

"Robust" names a technical category here. Leave it unless the task or evidence calls for a more precise description.

## 18. Preserve citation scope

**Mode:** evidence-checked edit. **Supplied source [1]:** a staging benchmark reports median latency of 40 ms on one named configuration; it contains no production comparison.

Original:

> Median latency was 40 ms in staging, demonstrating production readiness [1].

Revision:

> Median latency was 40 ms in the staging benchmark [1].

The citation supports the scoped measurement, not the added production-readiness judgment. Here [1] is a supplied fixture label, not an external citation.

## 19. Give a design decision its actual status

**Mode:** evidence-enriched rewrite. **Evidence:** an accepted first-release ADR chooses PostgreSQL because existing PostgreSQL operations meet the specified session durability requirements. A separate, unapproved review note suggests reconsidering Redis if measured traffic exceeds 2,000 writes per second.

Revision:

> The first release stores sessions in PostgreSQL, using existing operations that meet the session durability requirements. A proposed review trigger is measured traffic above 2,000 writes per second; that trigger has not been approved.

Do not present the proposed threshold as a measured limit or an accepted decision.

## 20. Keep summaries that serve a separate reader path

**Mode:** structural edit. **Evidence:** a long investigation report has an executive summary for decision-makers and a detailed findings section for implementers. Both state the same supported finding.

Decision:

> Keep the finding in both places. Remove duplicate explanation within either section, not the summary's ability to stand alone.

Repetition is justified by reader use, not automatically forbidden or required.
