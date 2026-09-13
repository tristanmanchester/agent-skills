# Portability and adaptation

Use the host's available tools without assuming a particular model, IDE, shell,
or scheduler. Resolve bundled scripts from the installed skill directory. The
core decision method does not depend on Python; the optional strict arithmetic
helpers need Python 3.10+ and accept only --input, returning JSON on stdout.

Without executable helpers, use an available calculator or work through a small
model explicitly. Apply the same fixed-anchor and scenario checks rather than
silently reverting to option-dependent min-max scaling. Do not invent missing
scores, probabilities, or a base rate to make the arithmetic possible.

Fresh sources are necessary for claims that could have changed. When retrieval
is unavailable, use the provided evidence and state the remaining limitation;
do not imply an outside view was established. Facts, assumptions, and judgement
remain distinct regardless of tool access.

Adapt the final response to the requested depth and format. Give the decision,
decisive evidence, main risk, and update condition without forcing every long
reference's heading or model count. A written update trigger is not an active
monitor or reminder. No external action follows from a recommendation without
the user's authorisation.
