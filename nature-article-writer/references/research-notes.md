# Research notes behind v2

This file records the main evidence sources that motivated the v2 design. It is not a substitute for checking live journal pages when the target journal is known.

## Official Nature and Nature Portfolio guidance

### Nature writing guidance
Key takeaways used in this skill:
- read the current author pages and recent issues before drafting to a specific journal
- write for readers outside the immediate discipline
- prefer active voice where it clarifies agency
- unpack dense concepts and minimise jargon and acronyms
- keep the paper focused on a concise message

### Nature formatting guidance
Key takeaways used in this skill:
- main Nature Articles use a referenced summary paragraph aimed at broad readers
- titles should stay concise and accessible
- Methods, Data Availability, and Code Availability need explicit handling
- figure legends should begin with a brief title and define statistics clearly

### AI and reporting policy
Key takeaways used in this skill:
- LLMs cannot be authors
- AI-assisted copy editing is treated differently from deeper scientific use
- reporting summaries and availability statements are often required for original research

## Human-like writing research incorporated into the skill

### Comparative stylistics work
Recent comparative work on LLM and human writing reports that instruction-tuned models often overuse:
- present-participial clauses
- nominalizations
- noun-heavy informational density

The study explicitly argues these are useful revision cues rather than detector rules. This is why v2 uses them for diagnosis, not for "beating detectors".

### Biomedical abstract vocabulary analyses
Large-scale analyses of recent biomedical abstracts suggest that LLM-affected prose often shows excess style words and a recognisable shift in lexical texture. This motivated the stronger anti-hype and anti-generic-language layers.

### Reader-guidance principles
Writing guidance from the Nature / Springer ecosystem emphasises that readers take cues not only from linking words but also from where information is placed in a sentence. This motivated the sentence-craft emphasis on topic position, stress position, and old-to-new information flow.

## Why this matters for skill design

The main failure mode of many "humanizer" prompts is that they push prose toward generic warmth or casualness. That is the wrong target for scientific manuscripts.

For Nature-style papers, the relevant improvements are:
- better structural architecture
- stronger paragraph jobs
- better sentence guidance
- less adjective-led importance
- fewer generic transitions
- more explicit limitation handling
- better alignment with the user's own exemplar prose

That is why v2 adds:
- journal calibration
- exemplar anchoring
- editorial blueprint templates
- a prose fingerprinting script
- stronger preflight checks
