# .NET Performance Review

Use this reference for performance-sensitive changes, hot paths, high-volume endpoints, background processing, allocation-heavy code, serialization, collections, strings, regex, or I/O.

This guidance is influenced by the MIT-licensed performance material in `dotnet/skills`, but is intentionally narrower for pull request review.

## First rule: establish relevance

Do not optimize code merely because a faster construct exists.

Before reporting a performance finding, identify at least one of:

- the code is inside a known hot path or tight loop;
- operation frequency or input size can reasonably be large;
- the change adds repeated network/database/file-system round trips;
- the change creates allocations proportional to large input;
- the change holds scarce resources longer than necessary;
- the regression is large enough to matter even at moderate volume.

If impact depends entirely on unknown workload, classify conservatively or omit the finding.

## Async and I/O

- Prefer non-blocking I/O in scalable server paths.
- Check sequential independent I/O that could safely be concurrent, but also check concurrency bounds before recommending fan-out.
- Avoid repeated open/close/reconnect cycles when the underlying abstraction is intended to pool resources.
- Check redundant serialization/deserialization or copying of large payloads.

## Database and remote calls

Network/database round trips generally matter more than small local allocations.

Check for:

- query-per-item/N+1 patterns;
- repeated calls for invariant data within the same operation;
- unbounded result sets;
- unnecessary full-object materialization when a projection would significantly reduce transferred data;
- accidental sequential remote calls in loops;
- retry multiplication that can amplify load during dependency failure.

## LINQ and collections

Do not ban LINQ.

Review LINQ when it is inside a hot loop or handles large collections. Look for:

- repeated enumeration of expensive/deferred sources;
- unnecessary `ToList`/`ToArray` materialization;
- chains creating avoidable intermediate collections;
- repeated linear lookup where a dictionary/set is justified by scale;
- sorting/grouping when only a small subset or single value is required.

Do not replace readable LINQ with loops for tiny or infrequent workloads without evidence.

## Strings

Check high-frequency string code for:

- repeated concatenation in loops;
- unnecessary casing transformations used only for comparison;
- culture-sensitive comparison when ordinal semantics are required;
- avoidable substring/copying of large inputs;
- repeated parsing/formatting of the same value.

Prefer explicit `StringComparison` when comparison semantics matter for correctness as well as performance.

## Regex

- Flag per-call regex construction on a hot path when the pattern is stable.
- Source-generated regex is useful for compile-time-known patterns on supported target frameworks, but do not require it universally.
- Dynamic patterns cannot simply be replaced by generated regex.

## Allocations and pooling

- Check large or repeated temporary allocations that are proportional to request/input volume.
- `ArrayPool<T>`, `MemoryPool<T>`, `Span<T>`, stack allocation, or custom pooling should be recommended only when the measured/obvious allocation pressure justifies added complexity.
- Do not recommend `Span<T>` across `await` boundaries where ref-struct lifetime rules make it unsuitable.

## `ValueTask`

Do not recommend `ValueTask` by default. It can help on very hot APIs that frequently complete synchronously, but it adds usage constraints and may be worse when operations usually complete asynchronously.

## Caching

Before recommending caching, require:

- a repeated expensive computation or remote read;
- a safe key;
- an invalidation/expiration model;
- acceptable staleness semantics;
- bounded memory/cardinality behavior.

Caching is not a generic fix for slow code.

## Serialization

Check for:

- unnecessary serialize-deserialize round trips;
- buffering very large payloads when streaming is appropriate;
- reflection-heavy or custom converters on high-volume paths when source generation is already feasible in the project;
- accidental inclusion of large navigation graphs or sensitive fields.

## Severity guidance

- HIGH: obvious multiplicative round trips, unbounded fan-out/resource use, severe blocking in a high-concurrency path, or a major regression on known hot code.
- MEDIUM: credible scale-dependent allocation/query cost or repeated work.
- LOW: only measurable/obvious improvements with low complexity.

Never present a micro-optimization as a merge blocker without evidence.
