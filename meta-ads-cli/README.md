# meta-ads-cli

A provider-specific Agent Skill for **Meta's official `meta-ads` package**. Start with [SKILL.md](SKILL.md).

The official CLI handles routine account, campaign, ad set, ad, creative, catalogue, dataset, and Insights operations. The small `scripts/meta_graph.py` fallback retains raw Graph calls, independent batches, and image/video uploads when installed CLI help confirms a gap. It does not duplicate the full CRUD client.

Revision 3 removes the heuristic command-risk wrapper, automatic plan runner, duplicate agent prompts, and stale command/risk catalogues. They were not a reliable authorisation boundary. The direct workflow requires specific user authorisation, paused creation, exact account context, and read-after-write verification.

The fallback accepts only relative paths on `https://graph.facebook.com`, never follows redirects or paging URLs, performs no automatic retry, and reports per-item batch failure. Writes require an exact locally reviewed plan hash. Existing scripts and environment conventions from `meta-ads-control` are not compatibility interfaces.

This skill's MIT licence does not relicense Meta's proprietary CLI. Offline tests use synthetic data and mocks, not an ad account. No live CLI/API compatibility or advertising result is implied by those tests.
