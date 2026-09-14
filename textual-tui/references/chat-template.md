# Chat starter ownership and tests

The chat starter accepts one current reply at a time. Submitting again while busy
leaves the draft and the accepted request unchanged; it does not use exclusive
worker cancellation as an implicit conversation policy. The Stop action explicitly
revokes local result ownership before requesting cancellation. A new request may
then be submitted, while any late result/event from the old worker is ignored.
This does not prove an external service stopped or undo an already completed write.

The demo adapter is async and local. Replace `build_reply` deliberately, with
transport deadlines, an authorised service, safe error reporting, and a recovery
policy for unknown outcomes. Use an appropriate executor for blocking/CPU work.
The revision check belongs on the UI runtime where results are applied, not only
before starting a worker. This example is not a durable conversation store or
streaming protocol implementation.

A reply failure has a visible status without an invented assistant response or
automatic retry. Cancellation releases local controls even before the worker's
coroutine starts; it does not depend on its `finally` block running. Unmounting
invalidates the request revision. Worker events from another request cannot clear
the new request's busy state.

Messages use `Static(..., markup=False)`, not Markdown interpolation. Literal
brackets and backticks are displayed as text. Apply the target application's
policy for control characters and untrusted links before adding richer rendering.
The view follows appended content only when it was already at the bottom, and
rechecks the scroll position at refresh time. It never re-anchors all history on
every message. Test actual layout and user scroll behaviour in Textual.

## Two different test layers

`python -m unittest discover -s tests -p test_chat_template.py -v` runs the real
rendered template's methods with explicit UI/worker doubles. It checks request
ownership, drafts, failure states, cancellation, late responses, unmount, plain-text
configuration, and scroll decisions. It does not import Textual or reproduce its
worker scheduler, DOM, TCSS, terminal, or browser implementation.

The scaffolded `tests/test_<module>.py` contains three real Pilot tests for the
integrating project. They use controlled events and bounded worker completion,
not a fixed delay followed by a permissive message count. Install the project's
selected Textual/pytest/pytest-asyncio versions and run those tests in an isolated
app environment. Also check narrow-terminal layout, focus, scrolling, and repeated
stop/send interactions. Syntactic parsing is not proof those runtime tests pass.

## Sources checked September 14, 2026

- https://textual.textualize.io/guide/workers/
- https://textual.textualize.io/api/worker/
- https://textual.textualize.io/api/widget/#textual.widget.Widget.is_vertical_scroll_end
- https://textual.textualize.io/widgets/static/
- https://textual.textualize.io/guide/testing/

The supplied template, not only its prose, must retain these decisions when revised.
