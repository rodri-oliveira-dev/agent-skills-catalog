# Testing Review

Use this reference when tests change or when production behavior changes enough that regression protection matters.

## Start from behavior

Identify the behavior introduced or modified by the pull request, then ask which failure scenarios would escape without a test.

Do not request tests merely because a line changed. Request a test when there is a concrete regression scenario worth protecting.

## High-value scenarios

Consider tests for:

- changed business rules and boundaries;
- null/empty/zero/min/max cases relevant to the contract;
- authorization and ownership rules;
- serialization or public API contract changes;
- persistence transactions/concurrency;
- retries, duplicate delivery, idempotency, and failure recovery;
- async cancellation and background-processing behavior;
- bug fixes where the original defect can be reproduced;
- compatibility behavior that existing consumers rely on.

## Assertion quality

Flag tests that:

- have no meaningful assertion;
- assert only that a mock was configured to return what it returned;
- use overly broad assertions that would pass for incorrect behavior;
- catch exceptions and then allow the test to pass without verifying the intended exception;
- test implementation details rather than the public/observable contract, creating unnecessary fragility.

Use interaction verification when the interaction itself is part of the contract, such as sending an event exactly once or never calling a dependency after validation failure.

## Determinism

Check for uncontrolled dependencies on:

- current date/time;
- random values;
- thread scheduling;
- `Thread.Sleep`;
- test execution order;
- static/global mutable state;
- local machine/environment settings;
- live network services;
- shared databases/queues/files without isolation.

Prefer injectable/control-oriented abstractions only when the nondeterminism creates an actual test problem.

## Async tests

- Await the actual operation under test.
- Avoid `async void` tests unless a test framework explicitly requires/supports the pattern.
- Avoid `.Result`/`.Wait()` in async tests.
- Ensure background work is deterministically observable before assertions.
- Use bounded timeouts for integration/eventual-consistency tests, but do not replace deterministic synchronization with arbitrary sleeps.

## Mocks

Check excessive mocking when:

- the test reproduces the implementation line by line;
- harmless internal refactors break many tests;
- important framework/database/serialization behavior is mocked away;
- the mock setup represents impossible production states and hides defects.

Do not demand real infrastructure for every unit test. Choose the lowest-cost test level that catches the risk.

## Integration tests

When the change depends on ASP.NET Core, EF Core, Dapper, serialization, database constraints, queues, caches, or HTTP semantics, consider whether a focused integration test provides materially better protection than mocks.

Review:

- isolated test data;
- cleanup;
- parallel test safety;
- realistic configuration;
- schema/migration alignment;
- authentication/authorization pipeline;
- transaction visibility;
- external dependency substitution.

## Test names and structure

Prefer consistency with nearby tests. Do not impose Given/When/Then, Arrange/Act/Assert comments, `Method_Scenario_Result`, or any specific naming pattern unless the repository already uses it.

## Coverage

Coverage percentage is a signal, not proof of test quality. Do not request arbitrary thresholds unless the repository explicitly requires them.

A small targeted regression test is often more valuable than increasing line coverage through low-value assertions.

## Severity guidance

- HIGH: a critical bug fix or sensitive authorization/data-integrity change has no practical regression protection and is easy to regress.
- MEDIUM: meaningful behavior lacks coverage, or tests are flaky/fragile enough to reduce confidence.
- LOW: small but concrete test-quality improvement.

Do not mark ordinary missing tests as BLOCKER unless repository policy or change risk genuinely justifies it.
