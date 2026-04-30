# Optimisation decisioning for agents

This skill helps agents operate ads, but an agent should not make reckless optimisation decisions. Use this guide to turn CLI data into sensible recommendations.

## Separate evidence from action

Always separate:

- observed data;
- interpretation;
- recommendation;
- actual mutation.

A report can say “pause candidate”. It should not pause unless the user approves.

## Minimum evidence checks

Before recommending pause/scale, check:

- spend volume relative to target CPA/ROAS;
- conversion count and statistical noise;
- date range and attribution window;
- whether tracking is healthy;
- creative age and learning/launch phase;
- campaign objective and optimisation event;
- budget constraints and delivery status.

## Common patterns

### Low CTR, acceptable conversion rate

Likely creative/hook/audience relevance issue. Suggest creative tests before budget changes.

### Strong CTR, poor conversion rate

Likely landing page, offer, audience intent, tracking, or product fit issue. Do not only change ads.

### High CPA with low spend

Mark as inconclusive unless spend is at least meaningful relative to target CPA. Suggest more data or a small test rather than immediate pause.

### High spend, no conversions

Check tracking first. If tracking is healthy and spend is meaningfully above target CPA, propose pause or budget reduction.

### Good ROAS but low volume

Suggest cautious scaling, not abrupt budget jumps. Large sudden budget changes can destabilise delivery.

## Recommended output language

Use:

```text
Candidate action: pause ad 123
Evidence: spent €80 over 7 days, 0 purchases, CTR 0.4%, tracking shows purchases on other ads.
Confidence: medium
Risk: may cut a learning-phase ad if attribution is delayed.
Next step: ask for approval to pause or wait 48h for more data.
```

Avoid:

```text
This ad is bad. I paused it.
```

## Scaling caution

When scaling budgets:

- show current and proposed budget;
- avoid very large jumps unless user explicitly asks;
- consider campaign/ad set learning and delivery constraints;
- verify the account currency and budget units;
- monitor after change.

## Creative testing

Good agent-generated test plans vary one or two dimensions at a time:

- angle: benefit, proof, urgency, objection handling;
- format: 1:1, 4:5, 9:16, video/static;
- audience/ad set when the user wants audience tests;
- landing page or offer only when the user asks for broader funnel testing.

Keep naming explicit so later reports can attribute performance to the test variable.
