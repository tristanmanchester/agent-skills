# Reporting and decisions

Start with the business question and a complete, narrow read. Record account ID, currency/timezone, date interval, query time, level, fields, filters, attribution windows, and page completeness. Use comparable intervals and account timezone boundaries; a relative preset alone is not a reproducible report.

Useful metric groups, subject to endpoint/version support:

- Traffic: spend, impressions, reach, clicks, inline link clicks, CTR, CPC, CPM.
- Conversion: actions, action values, purchase ROAS, and cost per action type, alongside spend and the relevant IDs.
- Identity: campaign, ad-set, and ad IDs/names appropriate to the requested level.

Inspect typed entries in `actions` and `action_values`; do not sum unrelated action types or assume every purchase field measures the intended conversion. Distinguish click types and their denominators. Do not average row-level CTR/CPC/ROAS without the correct weights; recompute ratios from compatible totals. Reach is not generally additive across overlapping audiences or intervals. Zero, absent, suppressed, and failed-to-fetch metrics are different states.

## Diagnose before changing

Separate observations, hypotheses, recommendations, and executed changes. Check conversion counts, spend relative to the business's target, tracking health, attribution delay, objective, optimisation event, delivery status, campaign age, and budget constraints before proposing pause or scale.

Low CTR can suggest a creative/audience issue; high CTR with low conversion can suggest landing-page, offer, intent, or tracking problems. These are hypotheses, not causal conclusions from two ratios. Small samples and overlapping auction conditions can reverse apparent rankings. Do not invent a confidence percentage or a universal spend threshold.

ROAS measures attributed revenue relative to ad spend, not profit. Profitability needs the relevant margin, fulfilment costs, fees, refunds, and other acquisition costs. Attribution is not proof of incremental lift. Where that distinction matters, propose an experiment instead of claiming causal impact.

## Useful workflows

**Account audit:** check access and current objects, then a small Insights query. Do not create a dataset, connect a pixel, or change targeting as part of an audit.

**Budget change:** read current budget owner (campaign or ad set), units/currency, schedule, spend constraints, and delivery. Show exact before/after, get the needed authorisation, apply once, and verify. A meaningful improvement in recent metrics is not automatic permission to scale.

**Paused launch:** resolve account, page/Instagram identity, objective, audience, budget, schedule, destination, event/dataset, and creative. Create campaign/ad set/creative/ad in the order required by their dependencies, explicitly paused where applicable. Record every returned ID and verify the whole mapping before separately approved activation.

**Creative test:** define the variable, audience, outcome, and decision rule. Keep naming useful for later analysis. Do not change budget, landing page, and targeting simultaneously and then attribute the result solely to a new headline.

**Catalogue/dataset work:** treat feed changes, retailer-ID mapping, connections, and permissions as consequential writes. Check current CLI/API support and policy, especially where older catalogue features have changed. Do not infer a healthy event pipeline from one configuration flag or a non-empty Insights result.

## Deliver

Provide the period/scope, strongest supported findings with numbers, tracking/data gaps, proposed actions with rationale, and separately any authorised changes and their verification. Mark incomplete pagination or missing conversions clearly. Save large raw exports privately and return an interpretable summary rather than dumping all fields.

For live changes, any follow-up check must be actually run or explicitly scheduled by the user; do not claim unattended monitoring from a one-off skill execution.
