# Python

Use the project's interpreter, package manager, formatter, linter and type checker.
Good defaults for a new project that will be maintained: `uv`, Ruff for format and lint,
pyright or mypy in strict mode, pytest, and import-linter once boundaries matter.

## Parse external data into types that enforce themselves

Annotations, `TypedDict`, `cast()` and plain dataclasses check nothing at runtime:
`Interval(start="a", end="b")` constructs happily. Two separate jobs need doing. A
boundary parser turns raw input into real types, using Pydantic, the project's
schema library, or explicit conversion. The type's own constructor enforces the
invariant between fields:

```python
@dataclass(frozen=True, slots=True)
class Interval:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError(f"interval end {self.end} is not after start {self.start}")

def parse_interval(raw: Mapping[str, object]) -> Interval:
    start, end = raw.get("start"), raw.get("end")
    if not isinstance(start, str) or not isinstance(end, str):
        raise ValueError(f"interval needs ISO-8601 string start and end, got {raw!r}")
    return Interval(datetime.fromisoformat(start), datetime.fromisoformat(end))
```

`frozen=True` is shallow: a `list` field can still be mutated. Use `tuple` or
`frozenset` for collection fields of value types.

## Make illegal states unrepresentable

- `enum.StrEnum` or `Enum` for closed sets. Never compare against raw strings when an
  enum exists.
- Tagged unions with dataclasses and `match`, closed with `assert_never` so a new
  variant fails the type check everywhere it isn't handled:

  ```python
  match state:
      case Idle(): ...
      case Running(started=t): ...
      case Failed(error=e): ...
      case _: assert_never(state)
  ```

- `Literal[...]` for small fixed option sets on public functions.
- Avoid `Optional` fields whose presence depends on another field; that combination
  is a state type.

## Errors

- Real checks raise real exceptions. `assert` is removed under `python -O`; use it only
  for internal sanity checks you could delete.
- Never write `except Exception: pass`, or `except Exception: return None` far from the
  point where you can act.
- Re-raise with the cause: `raise SyncError(f"upload of {note_id} failed") from e`.
- Define a small set of domain exceptions for errors callers handle differently.

## Async

- Prefer `asyncio.TaskGroup` (3.11+): children are awaited, and one failure cancels the
  rest.
- **Keep a reference to every `create_task()` result.** The event loop holds tasks
  weakly, so an unreferenced task can be garbage-collected mid-run.
- Don't swallow `CancelledError`. Clean up in `finally`, then let it propagate.
- Never call blocking I/O or heavy CPU work in a coroutine. Use `asyncio.to_thread`
  or a process pool.

## Modules and state

- No work at import time: no connections, file reads, network calls or env-var reads
  at module level. Read configuration once at the entry point and pass it down.
- No mutable default arguments (`def f(x=[])`); use `None` and create the value inside,
  or `field(default_factory=list)`.
- Module-level globals that change at runtime are hidden links. Pass state explicitly
  or give it one owner object.
- Leading underscores and `__all__` don't stop imports. Use import-linter contracts
  where a boundary matters ([boundaries](boundaries.md)).

## Types

- Annotate every public function. Run the checker in CI; a new `# type: ignore` carries
  the error code and a reason.
- Use `Protocol` for structural typing at a real seam with two implementations. Use
  concrete classes and plain functions everywhere else.
- `dict[str, Any]` crossing a function boundary is an untyped interface. Give it a
  dataclass or `TypedDict`.

## Tests

- pytest with plain `assert`. Fixtures for setup, and `parametrize` for tables of cases.
- Hypothesis for parsers, serialisers and numerical properties.
- `tmp_path` for the filesystem. Real SQLite or a test Postgres for persistence.
- Use `freezegun` or an injected clock, never sleeps.
- `pytest.raises(SpecificError, match=...)` instead of a bare `Exception`.
