# Async and Concurrency Review

Use this reference when the changed code contains asynchronous operations, background processing, locks, channels, caches, shared state, timers, or parallelism.

## Blocking and sync-over-async

Check for:

- `.Result`, `.Wait()`, synchronous waits, or blocking I/O inside asynchronous request/background paths;
- unnecessary `Task.Run` around naturally asynchronous I/O;
- synchronous APIs used in high-concurrency server code when an async equivalent is already part of the design.

Do not claim deadlock automatically. In ASP.NET Core, sync-over-async more commonly creates thread-pool starvation/scalability risk, although deadlocks remain possible in other synchronization contexts.

## Cancellation

- Propagate `CancellationToken` through meaningful I/O and long-running operations.
- Do not create a new token solely to silence an API contract.
- Distinguish request cancellation from application shutdown and operation-specific timeouts.
- Do not swallow `OperationCanceledException` as an ordinary failure when cancellation is expected.

## Fire-and-forget work

Flag unobserved work when:

- exceptions can disappear;
- scoped dependencies can be disposed before work completes;
- application shutdown can abandon important work;
- duplicate execution or lost work is possible;
- there is no durable queue or explicit background-worker ownership when durability is required.

## Shared state

- Check static fields, singletons, caches, dictionaries, collections, counters, and mutable options for thread safety.
- Verify compound operations are atomic when correctness depends on check-then-act behavior.
- `ConcurrentDictionary` does not automatically make multi-step workflows atomic.
- Check lock ordering and nested locks when multiple locks exist.
- Avoid holding a monitor/lock across `await`.

## Parallelism

- Check `Task.WhenAll` and parallel loops for uncontrolled fan-out against databases, HTTP services, file systems, or rate-limited dependencies.
- Verify failure behavior when one task fails and others continue.
- Ensure results and shared accumulators are safe under concurrent writes.
- Prefer bounded concurrency when input cardinality can grow without a small known limit.

## Background services

For `BackgroundService`, hosted services, timers, or consumers:

- verify shutdown cancellation;
- ensure scopes are created/disposed per unit of work when scoped dependencies are used;
- check retry loops for busy spinning and missing delay/backoff;
- check poison-message or permanently failing-item behavior;
- make sure a single unexpected exception does not silently stop critical processing unless that is intended;
- verify recurring timers cannot overlap work unexpectedly.

## `Task` and `ValueTask`

- Do not recommend `ValueTask` as a default optimization.
- A `ValueTask` should not normally be awaited multiple times or stored for arbitrary later use unless backed by a safe implementation.
- Avoid returning a hot `Task` for work that should be lazy only when the contract explicitly requires laziness.

## Async disposal

Check `await using` / `IAsyncDisposable` when resource cleanup itself is asynchronous and the changed code owns that resource.

## Severity guidance

- BLOCKER/HIGH: races causing corruption, deadlocks, lost critical work, severe unbounded fan-out, invalid resource lifetime.
- MEDIUM: missing cancellation, avoidable starvation risk, fragile concurrency, overlap risk dependent on load.
- LOW: only for small evidence-backed improvements; omit speculative concurrency commentary.
