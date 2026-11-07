# Swift and SwiftUI

Use Swift 6 language mode with complete strict concurrency. Treat a concurrency
warning as a bug report, not noise to silence.

## Types carry the invariants

- Structs and enums by default. Use a class (usually `@Observable` and `@MainActor`) for
  identity-bearing UI models and an actor for shared mutable state.
- Enums with associated values for states:

  ```swift
  enum Upload: Sendable {
      case pending(URL)
      case sending(URL, attempt: Int)
      case done(RemoteID)
      case failed(URL, UploadError)
  }
  ```

  `switch` exhaustively, with no `default:` on your own enums, so a new case fails the build
  everywhere it isn't handled.
- `private(set)` or `private` stored properties plus a failable or throwing `init` for
  values with invariants.
- **Decoding goes through the same check.** A synthesised `Codable` on a type with
  invariants is a back door. Write `init(from decoder:)` that decodes the raw fields
  and calls the validating initialiser.
- Wrapper types for identifiers (`struct NoteID: Hashable, Codable, Sendable { let raw: UUID }`).

## Optionals and failure

- Make a property optional only when absence is a real state. A value that is "nil until
  configured" is a lifecycle; model it as one.
- `!`, `try!` and `fatalError` are for programmer errors the code has already ruled out.
  Never use them on network, disk, decoding or user input.
- Throw typed domain errors. Use typed throws (`throws(SyncError)`) when callers
  handle each case. Don't turn errors into `nil` with `try?` when the reason matters.

## Concurrency

- **Actors are reentrant.** State can change across every `await` inside an actor
  method. Re-check invariants after each suspension, or finish the state change before
  awaiting:

  ```swift
  actor TokenStore {
      private var token: Token?
      private var refreshTask: Task<Token, Error>?

      func validToken() async throws -> Token {
          if let token, !token.isExpired { return token }
          if let task = refreshTask { return try await task.value } // join, don't race
          let task = Task { try await api.refresh() }
          refreshTask = task
          defer { refreshTask = nil }
          let fresh = try await task.value
          token = fresh
          return fresh
      }
  }
  ```

- UI state and view models are `@MainActor`. Don't hop to the main actor with
  `DispatchQueue.main.async` in new code.
- Prefer structured concurrency: `async let`, `withThrowingTaskGroup`, and SwiftUI's
  `.task(id:)`, which cancels when the view disappears or the id changes. An unstructured
  `Task {}` is stored by its owner and cancelled on teardown.
- Cancellation is cooperative. Long loops call `try Task.checkCancellation()`. After an
  `await`, check that the result still applies (same id, same screen) before applying it.
- `@unchecked Sendable` and `nonisolated(unsafe)` switch off the compiler's proof. Use
  them only with a lock or queue that really protects the state, and comment what does.

## SwiftUI

- Views are a function of state. Derive values in computed properties; don't copy them
  into `@State` with `onAppear` or `onChange`.
- `@State` is for state the view owns. `@Binding` passes write access down.
  `@Environment` carries shared models. Model objects are `@Observable` classes owned by
  one parent.
- Keep side effects out of `body`. Use `.task(id:)` for loading, and button actions for
  user-caused work.
- Navigation uses value-based `NavigationStack(path:)` with `Hashable` route enums, so
  deep links and state restoration share one representation.
- Persistence (SwiftData, GRDB, files) sits behind a small store module. Views don't
  build fetch descriptors or SQL inline beyond simple `@Query` cases.

## Module boundaries

Swift packages are the enforced boundary. Split out a target when you want the compiler
to enforce a dependency direction or hide an implementation. Within it, `internal` is the
default, `package` shares across targets in the package, and `public` is the real API.
Target dependencies in `Package.swift` define the allowed graph. See
[boundaries](boundaries.md).

## Tests

- Swift Testing (`@Test`, `#expect`, `#require`, `@Test(arguments:)`) for new tests.
  `#require` stops the test on a failed precondition instead of crashing on `!`.
- Test view models and stores directly. Use an in-memory `ModelContainer` or a temp-dir
  database for persistence.
- Inject the clock (`any Clock<Duration>`) and network client at the seam. Use the real
  types for everything else.
- Verify UI flows on the simulator. A green unit test doesn't show the screen works.
