# Trigger evaluations

Test automatic routing separately from writing quality. Show the agent the skill description, not a forced instruction to load it, except in the explicit-invocation set. Record whether it loads the skill before drafting. These are routing probes, not complete writing tasks; missing source files are not invitations to fabricate content.

## Automatic positives

1. "Clean up README.md; the setup steps are buried."
2. "Document the authentication flow from this repository's code and tests."
3. "Turn these accepted decision notes into an ADR."
4. "Shorten this incident runbook without losing safety checks."
5. "Fix ambiguous parameter descriptions in our API reference."
6. "Add contract docstrings to the public methods in client.py."
7. "Write a migration guide from schema v2 to v3."
8. "Update the CLI guide and command reference for --dry-run."
9. "Make this onboarding page clearer and less repetitive."
10. "Write an RFC for changing session storage."
11. "Organize this troubleshooting page around observable errors."
12. "Write a technical findings report from these benchmark results for the engineering team."

## Automatic negatives

1. "Explain this regular expression to me in chat."
2. "Draft an email announcing the new API."
3. "Write a LinkedIn post about documentation."
4. "Fix the retry bug; no docs changes."
5. "Summarize this README so I can decide whether to read it."
6. "Translate this setup guide into German; preserve its meaning and structure."
7. "Make a slide deck from this architecture document."
8. "Write landing-page copy for a developer platform."
9. "What does HTTP 429 mean?"
10. "Put this already approved contract text into a Word document without editing it."
11. "Proofread this two-sentence Slack message."
12. "Review this code for security vulnerabilities."

## Explicit invocation: activate compatible guidance

1. "Use write-good-docs to tighten this email into one paragraph."
2. "Apply write-good-docs to this research-results paragraph; keep uncertainty."
3. "Use write-good-docs to check this German translation against its English original."
4. "Use write-good-docs for the prose in this slide deck; do not impose documentation sections."

Activation is not permission to expand scope, perform factual enrichment, change meaning during translation, or displace a needed file-format skill. Grade those behaviors separately from whether the skill loaded.

## Context-dependent probes

1. "Explain the new caching behavior." Activate when the explanation is meant to become documentation, not just a chat answer.
2. "Add comments to this function." Activate for useful contract or rationale comments; ordinary implementation comments may be incidental to coding.
3. "Update the implementation and docs." Activate for the material documentation deliverable and compose with coding guidance.
4. "Make this report clearer." Activate for a durable technical findings report; inspect context for a different genre.

## Compare routing

Record trigger/non-trigger, expected category, and any context that legitimately resolves an ambiguous case. Repeat across target agents and model versions. Track clear-positive activation and clear-negative non-activation separately; 90% in each is an initial development target, not proof of writing quality. Track explicit-invocation misses separately. Retest revised descriptions on fresh phrasings and held-out tasks rather than optimizing only these probes.
