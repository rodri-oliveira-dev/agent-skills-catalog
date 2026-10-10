# Architecture Review

Use this reference when a pull request changes module boundaries, dependency direction, public abstractions, cross-cutting infrastructure, shared models, or code ownership between layers/components.

## Architecture is contextual

Do not impose a named architecture because it is popular.

First determine what architecture the repository already uses and which constraints are intentional. Relevant evidence includes:

- project references;
- folder/module boundaries;
- dependency injection registration;
- public interfaces/contracts;
- existing ADRs or documentation;
- nearby implementation patterns;
- deployment boundaries;
- tests that encode dependency rules.

A pattern deviation is only a finding when it creates a concrete problem or violates an established repository constraint.

## Dependency direction

Check for:

- a stable/core module gaining a dependency on an infrastructure-specific module that the repository intentionally isolates;
- circular project/module dependencies;
- domain/business logic becoming coupled to transport, persistence, framework, or deployment details where that coupling creates testing or reuse problems;
- implementation details leaking through public contracts;
- shared libraries becoming dependency magnets for unrelated concerns.

Do not demand dependency inversion when the direct dependency is simple, stable, local, and not causing a real problem.

## Boundaries and cohesion

Review whether the change:

- places behavior near the data/invariants it owns;
- duplicates the same rule across endpoints/services/workers;
- creates a shared abstraction used by only one caller with no volatility reason;
- spreads one feature change across many unrelated modules because responsibilities are poorly separated;
- introduces cross-module mutation or shared state that makes ownership unclear.

## Abstractions

Recommend a new abstraction only when at least one concrete driver exists, such as:

- multiple implementations genuinely exist or are imminent in the current scope;
- a volatile/external dependency needs isolation;
- test seams are otherwise impractical for behavior that requires isolation;
- duplicated policy needs one authoritative owner;
- public consumers need a stable contract independent of implementation.

Do not introduce interfaces simply to wrap every class.

## Patterns

Repository, Unit of Work, CQRS, MediatR, factories, decorators, strategies, domain events, outbox, sagas, DDD aggregates, Clean/Hexagonal architecture, and vertical slices are tools, not universal requirements.

A review finding should state the concrete problem first. The pattern may appear in the recommended fix only if it is an appropriate solution for the repository.

Example of a valid reason:

- "This write commits the database transaction before publishing the event; a process crash can permanently lose the event. The repository already uses an outbox for this consistency boundary, so route this publication through the existing outbox."

Invalid reason:

- "Use the Outbox Pattern because distributed systems should use outbox."

## Public contracts

For libraries/services consumed outside the changed module, review:

- source/binary compatibility when applicable;
- request/event/schema compatibility;
- nullability and optional fields;
- versioning expectations;
- semantic behavior changes;
- ownership/lifetime expectations;
- error/exception contracts.

A compile-safe refactor can still be an architectural breaking change for external consumers.

## Cross-cutting concerns

Check whether authentication, authorization, transactions, retries, caching, observability, validation, and error mapping are implemented at the appropriate boundary.

Flag duplicated cross-cutting logic when duplication creates inconsistent behavior or missed paths, not merely because centralized middleware/decorators could exist.

## Distributed systems

When a change crosses process boundaries, consider:

- at-least-once delivery and duplicates;
- idempotency;
- ordering assumptions;
- partial failure;
- timeouts/retries;
- consistency boundaries;
- schema compatibility;
- poison messages;
- observability/correlation.

Do not demand distributed-system patterns for purely in-process changes.

## Maintainability signals

A maintainability finding should describe tangible change cost, for example:

- adding one field now requires editing six manually duplicated mappings;
- the same business invariant has two inconsistent implementations;
- callers must know internal persistence details;
- one module exposes mutable state used by unrelated components;
- a change creates a cyclic dependency preventing independent evolution.

Avoid subjective claims such as "not clean" or "violates SOLID" without explaining the actual cost.

## Severity guidance

- HIGH: boundary violation creates likely correctness, security, deployment, or consistency failure.
- MEDIUM: concrete coupling/change-amplification/testability problem.
- LOW: small architectural improvement only when the value is immediate and obvious.

Architecture comments should usually not be BLOCKER unless they correspond to a concrete severe defect.
