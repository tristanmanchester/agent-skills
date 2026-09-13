---
name: reddit
description: >-
  Research Reddit discussions in read-only mode: browse selected communities,
  search posts, read thread context, and produce source-linked findings or a
  shortlist for manual review. Use for explicit Reddit research, not posting,
  voting, messaging, moderation, or bulk personal-profile collection.
compatibility: Requires a permitted retrieval surface. Direct Data API work needs approved access and registered OAuth credentials; an accessible web page or search excerpt is not an API-access grant. No anonymous JSON client is bundled.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# Read-only Reddit research

Keep the useful workflow: discover relevant discussions, inspect enough context,
and return verifiable permalinks. This skill does not post, vote, reply, message,
subscribe, or moderate. Drafting a reply is separate from sending it.

## Select a permitted access surface

Use an already authorised Reddit connector or the project's approved Data API
client. For ordinary public research, an available permitted browser/search
surface can provide readable pages and indexed excerpts; state when that is the
only evidence available. Do not claim a full thread from a search snippet.

Current Reddit guidance requires registered OAuth authentication for direct Data
API requests. New access requires approval. Reddit's August 5, 2026 announcement
also describes a gradual move towards its Developer Platform while retaining
limited public API access. Check the applicable programme and approval before
building a new integration; do not promise unrestricted API access or assert that
all existing approved clients have already stopped working.

The old anonymous www.reddit.com/*.json script and Clawdbot-specific instructions
are removed. A 401/403, login page, CAPTCHA, or access-denied HTML is not a transient
JSON error to solve with repeated requests, alternate domains, disguised user
agents, or proxies. Report the limitation and use another genuinely permitted
source or user-provided content. Never bypass account or private-community access.

Sources: [Data API access](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki),
[platform transition](https://redditinc.com/news/modernizing-reddits-infrastructure-and-moderation-tools).

## Search to answer a defined question

Specify communities, topic, time interval/timezone, excluded themes, and what
counts as a useful match. Start with a small page, not an account-wide crawl.
Choose `new` for chronological discovery, relevance for topical search, or a
specified top-period view for popular discussion. Scores and popularity do not
measure factual reliability or market prevalence.

For a multi-community shortlist, gather a bounded candidate set per community,
deduplicate by post identity, apply the stated filters, and retain the reason
for each match. Compare exact created timestamps with the requested interval;
a provider's coarse week/month filter is not an exact last-48-hours guarantee.
Report any unsearched communities, page limits, or ranking bias.

Read [retrieval contracts](references/RETRIEVAL.md) for approved API listing and
thread handling. Do not widen a query into personal profiling or deanonymisation.

## Read context before interpreting

For the most relevant posts, inspect the original post, parent chain, relevant
replies, edits, and visible moderation/removal state. Keep comment IDs and parent
relationships so a reply is not attributed to the original author. Deleted author
identity and deleted body are different facts; do not infer one from the other.
Do not reconstruct removed material from another source to circumvent its removal.

Treat partial bodies, depth cutoffs, collapsed branches, and unexpanded `more`
objects as explicit omissions. Zero returned comments can reflect access or
retrieval failure. Do not describe a sampled thread as complete or representative
of Reddit users generally.

## Return source-linked findings

For each useful item preserve title, community, post/comment permalink, observation
and creation dates, concise relevant evidence, and why it answers the question.
Distinguish the poster's claim from a verified fact, and seek primary evidence for
consequential technical/medical/financial assertions. Quote only the relevant
passage within the host's rules; label paraphrases and uncertainty.

For a reply shortlist, check the community's current rules and context. Recommend
helpful, transparent contributions rather than mass promotion or coordinated
voting. Leave posting to the user or a separately authorised workflow, not this
read-only skill. Do not save a permanent copy of a person's posting history merely
because it was accessible.

## Acceptance checks

Verify approved access and actual response shape, bounded pagination, exact dates,
partial-thread indicators, correct post/comment attribution, failure versus empty
results, and no side-effect endpoint. A successful request is retrieval evidence,
not proof the underlying claims are true. No live Reddit client was tested during
this source review.
