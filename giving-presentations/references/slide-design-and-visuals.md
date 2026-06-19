# Slide Design and Visuals

Use this reference when the user is creating, critiquing, or improving slides, charts, visuals, demos, handouts, or async decks.

## Slide design principles

### 1. The title is the message

Every slide needs a title that says the point. Generic labels force the audience to do interpretive work.

Weak:

- “Market”
- “Experiment 2”
- “Customer Feedback”
- “Results”

Strong:

- “The market is consolidating around compliance-first vendors.”
- “Experiment 2 rules out transport limitation as the main mechanism.”
- “Customers describe the same workaround in five separate interviews.”
- “Throughput doubled, but only after segmentation.”

### 2. One slide, one job

A slide can do one of these jobs well:

- Orient: where are we in the story?
- Claim: what should the audience believe?
- Prove: what evidence supports the claim?
- Explain: how does the mechanism work?
- Compare: what changed or differs?
- Decide: what choice is in front of us?
- Transition: why are we moving to the next section?

If a slide tries to do four jobs, split it.

### 3. Design for a three-second read

Within three seconds, the audience should know:

1. The slide’s claim.
2. Where to look first.
3. What comparison or pattern matters.
4. Why the slide exists in the story.

Use hierarchy: size, position, whitespace, emphasis, grouping, and labels.

### 4. Reduce cognitive load

Prefer:

- Fewer words.
- Clear labels near the relevant visual element.
- Progressive disclosure for complex diagrams.
- Speaker narration instead of duplicating paragraphs on screen.
- Simple charts with the conclusion in the title.
- Backup slides for detail that may be useful but is not central.

Avoid:

- Reading dense text verbatim.
- Decorative visuals that do not support meaning.
- Dense tables in live talks.
- Multiple unrelated charts on one slide.
- Tiny labels, footnotes, and legends the room cannot read.

## Slide title rewrite patterns

| Generic label | Takeaway title |
|---|---|
| Problem | Manual triage is consuming the time we need for prevention |
| Solution | A shared intake model cuts review time without lowering quality |
| Market size | The reachable market is smaller than the category, but large enough for a venture-scale wedge |
| Roadmap | The first two releases reduce onboarding friction before expanding scope |
| Method | The control experiment isolates imaging artifacts from true microstructural change |
| Risks | The largest risk is adoption, not technical feasibility |
| Next steps | Approval today lets us start the pilot before the July freeze |

## Data slides

### The data-slide formula

1. **Claim title:** Say the conclusion.
2. **Chart:** Show only what is needed to support the claim.
3. **Highlight:** Direct attention to the relevant pattern.
4. **Plain-language interpretation:** Explain what the pattern means.
5. **Implication:** Connect it to the decision or story.

### Chart choices

| Need | Good chart | Avoid |
|---|---|---|
| Compare categories | Bar chart | Pie with many slices |
| Show trend over time | Line chart | Table of monthly values |
| Show distribution | Histogram, box plot, violin | Only mean values |
| Show part-to-whole | Stacked bar, simple pie for few categories | 3D pie |
| Show relationship | Scatter plot | Dual-axis chart unless necessary |
| Show process | Flow diagram | Paragraph of process text |
| Show uncertainty | Error bars, intervals, shaded bands | Point estimate alone |

### Make numbers meaningful

Translate important numbers into context. Instead of “70% abandonment,” use a relatable analogy or scenario that helps the audience feel the magnitude. For technical audiences, combine intuition with the exact number.

Prompts:

- “Compared with what?”
- “How big is that in human terms?”
- “What would this look like over a week, quarter, or full fleet?”
- “What decision changes because of this number?”

### Data-story sequence

For complex data:

1. Tell them what they are looking at.
2. Explain the axes and reference point.
3. Reveal the pattern.
4. Highlight the key comparison.
5. Interpret cautiously.
6. State the implication.
7. Mention limitations or uncertainty if decision-relevant.

## Technical and scientific visuals

Technical slides often fail because they try to show the full analysis all at once. Sequence the visual explanation.

Use this order:

1. Cartoon or schematic of the system.
2. The measurement or model in plain language.
3. Representative example.
4. Aggregate result.
5. Uncertainty/limitations.
6. Mechanistic interpretation.
7. Implication for the field, project, or decision.

For microscopy, tomography, spectroscopy, models, or mechanisms:

- Label the physically meaningful features, not every visible feature.
- Include scale bars and units.
- Avoid rainbow colormaps unless the mapping is justified and accessible.
- Use consistent color/shape encodings across slides.
- Show controls or baselines before asking the audience to trust a difference.
- Pair “what you see” with “what it means.”

## Async decks and leave-behinds

A live deck supports a speaker. An async deck must speak for itself.

For async decks:

- Add short body text under the takeaway title.
- Put definitions and assumptions on the slide where they are needed.
- Use a summary slide up front.
- Make navigation obvious.
- Include source notes and caveats.
- Use more explicit annotations on charts.
- Include a final recommendation and next steps.

Do not use a sparse keynote deck as an async leave-behind without adding context.

## Visual rhythm and state changes

Avoid visual monotony. Every 3–5 slides or minutes, change the state of the audience or the rhythm of the deck.

Options:

- Ask the audience to predict a number before revealing it.
- Move from abstract to concrete with an example.
- Use a customer quote or short story.
- Show a before/after comparison.
- Pause for reflection.
- Use a demo or prop.
- Insert a “decision checkpoint.”
- Switch from data to implication.

## Accessibility defaults

Design for the person farthest from the screen, on the worst connection, or using assistive technology.

Minimum checklist:

- Every slide has a unique title.
- Text is large enough to read, preferably 18 pt or larger for body text.
- Use sans serif fonts and generous spacing.
- Maintain strong text/background contrast.
- Do not use color alone to encode meaning; add labels, icons, line styles, or direct annotations.
- Add alt text for meaningful images, charts, and diagrams when producing files.
- Use built-in layouts or logical ordering so screen readers follow the intended reading order.
- Avoid dense tables; if a table is necessary, keep it simple with headers.
- Add captions/subtitles for video or audio.
- Avoid excessive motion, flashing, or distracting transitions.
- Use meaningful link text instead of raw URLs when slides will be shared.

## Slide cleanup checklist

For each slide, ask:

- What is the one point?
- Does the title say it?
- Can I cut 30–50% of the text?
- What should the audience look at first?
- Is the visual proving the title?
- Is anything decorative but not meaningful?
- Does the slide need to be live, backup, or async-only?
- Would it be readable from the back of the room or on a laptop screen?
- Does it still work in grayscale?

## Common fixes

### Text-heavy slide

- Convert paragraphs into a claim title plus 3 evidence bullets.
- Split one slide into a sequence.
- Move detail to speaker notes or backup.
- Use a diagram, process, or comparison table if it genuinely improves clarity.

### Busy chart

- Remove nonessential gridlines, legends, labels, and categories.
- Direct-label lines/bars instead of relying on a legend.
- Highlight the main series and mute context series.
- Add the conclusion in the title.
- Split into small multiples if comparing many groups.

### Weak executive slide

- Put the recommendation in the title.
- Show the decision needed.
- List options and tradeoffs.
- Move detail into backup.
- Add one sentence on risk and mitigation.

### Weak scientific slide

- Add the research question or claim as title.
- Orient the audience before showing raw data.
- Make units, scale bars, and controls visible.
- Explain what the visual feature means physically.
- Include uncertainty and limitations only where they affect interpretation.
