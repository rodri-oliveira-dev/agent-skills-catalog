---
name: dotnet-code-review
license: MIT
description: >-
  Reviews .NET and C# pull request changes for correctness, security, async and
  concurrency issues, persistence defects, performance regressions, API
  contracts, testing gaps, architecture risks, and MSBuild/NuGet configuration.
  Use for pull request and code review tasks in modern .NET repositories.
---

# .NET Code Review

Perform a diff-first, high-confidence review of .NET pull request changes.

The objective is not to maximize comment count. The objective is to find issues a strong senior/staff .NET reviewer would consider actionable before merge.

## Inputs to inspect

Use the information available in this order:

1. Pull request description and stated intent.
2. Changed files and diff.
3. Surrounding implementation needed to understand the changed behavior.
4. Existing tests and nearby conventions.
5. Project files, target framework, language version, analyzers, `.editorconfig`, and dependency versions when relevant.

Do not infer architecture, runtime version, database behavior, or repository conventions when they can be determined from the repository.

## Review workflow

### 1. Understand the change

Identify:

- what behavior is being added, removed, or changed;
- public or internal contracts affected;
- trust boundaries and external inputs;
- persistence or state transitions;
- asynchronous/background behavior;
- operationally important paths;
- tests intended to protect the change;
- build, packaging, or target-framework changes.

If the implementation appears to contradict the pull request intent, treat that as a correctness concern rather than a style concern.

### 2. Review the diff for core risks

Always consider:

- correctness and edge cases;
- security and authorization;
- data integrity;
- breaking changes;
- resource lifetime;
- async/cancellation/concurrency correctness;
- error behavior;
- regression coverage;
- build and package compatibility when project configuration changes.

### 3. Load specialist references only when relevant

Read the reference files below when the changed code contains matching signals.

| Signal | Reference |
| --- | --- |
| `async`, `await`, `Task`, background services, channels, locks, shared state | `references/async-concurrency.md` |
| hot paths, allocations, LINQ-heavy loops, strings, regex, serialization, I/O | `references/dotnet-performance.md` |
| `DbContext`, EF Core LINQ, `Include`, tracking, migrations | `references/ef-core.md` |
| `Dapper`, `Query*`, `Execute*`, `CommandDefinition`, raw SQL | `references/dapper.md` |
| controllers, Minimal APIs, middleware, HTTP clients, endpoint DTOs | `references/webapi.md` |
| authentication, authorization, secrets, untrusted input, cryptography | `references/security.md` |
| tests or meaningful behavior changes | `references/testing.md` |
| boundaries, dependency direction, public abstractions, cross-module changes | `references/architecture.md` |
| `.csproj`, `.props`, `.targets`, `Directory.Build.*`, `Directory.Packages.props`, `global.json`, NuGet/package/publish changes | `references/msbuild.md` |

Do not load every reference simply because it exists. Keep the review focused on the changed surface.

### 4. Validate every candidate finding

Before reporting a finding, answer all of these:

1. Is the issue introduced, exposed, or materially worsened by this pull request?
2. Is there a plausible failure mode or engineering cost?
3. Is the claim supported by the diff, surrounding code, project configuration, or established .NET behavior?
4. Is the suggested fix compatible with the repository's target framework and conventions?
5. Would an experienced reviewer reasonably ask for this change now?

If any answer is no or uncertain, do not report the finding as a defect. Reduce severity or omit it.

## Severity model

### BLOCKER

Use only for changes that make merging unsafe, such as:

- exploitable authentication/authorization or injection vulnerability;
- likely data corruption or irreversible data loss;
- deterministic deadlock or severe concurrency correctness issue;
- severe logic defect on a critical path;
- incompatible public contract change with immediate consumer impact.

### HIGH

Use for likely production defects such as:

- incorrect business behavior or missing critical edge handling;
- authorization bypass on a sensitive operation;
- resource exhaustion or serious connection/thread-pool risk;
- transaction or persistence consistency defects;
- major performance regression on a known high-volume path;
- missing regression protection for a high-risk fix when failure is otherwise likely;
- build/package configuration that breaks supported consumers or deployment targets.

### MEDIUM

Use for concrete but non-blocking issues such as:

- maintainability that materially raises future defect risk;
- avoidable repeated database/network work;
- fragile tests;
- architectural coupling that violates an established boundary;
- performance issues whose impact depends on scale or hot-path status;
- project-system configuration likely to drift or behave differently across targets/environments.

### LOW

Use sparingly for small, clearly beneficial, evidence-backed improvements.

Never use LOW for personal preference, formatting, optional syntax modernization, or speculative abstraction.

## Finding format

Keep each comment concise and actionable:

```markdown
**[SEVERITY] Category: short title**

Problem and concrete impact.

**Evidence:** explain what in the changed code causes the issue.

**Recommended fix:** smallest practical correction.
```

Include the changed file/line through the review system rather than repeating a large code excerpt.

Use a code suggestion only when it materially clarifies the fix. Do not rewrite whole methods to fix a one-line issue.

## Noise controls

Do not report:

- unchanged legacy issues unrelated to the pull request;
- formatting already covered by tooling;
- generic "follow SOLID/Clean Code" comments;
- demands for Repository, Unit of Work, CQRS, MediatR, DDD, Clean Architecture, factories, interfaces, or wrappers without a demonstrated need;
- "add caching" without evidence of repeated expensive work and a valid invalidation model;
- "use Span/ValueTask/ArrayPool" without hot-path evidence;
- "replace LINQ with loops" outside a demonstrated performance-sensitive path;
- blanket `ConfigureAwait(false)` recommendations in application code;
- demands to adopt newer project-system features solely because they are newer;
- comments that only praise code without helping merge quality;
- duplicate comments caused by the same root issue.

## Cross-file review

A pull request can be incorrect even when each file looks locally valid. Trace changed behavior across files when necessary, especially for:

- endpoint -> service -> persistence flows;
- transaction boundaries;
- DTO/domain mapping;
- background enqueue/dequeue paths;
- authentication/authorization checks;
- configuration registration and DI lifetime changes;
- public API implementation plus tests;
- producer/consumer schema changes;
- project file -> shared props/targets -> CI/publish behavior.

## Test review

When production behavior changes, determine whether existing tests actually cover the changed contract. Do not demand tests mechanically; identify the regression scenario that is currently unprotected.

## Performance review

Correctness comes before micro-optimization. Performance comments should describe scale, frequency, allocation/round-trip behavior, or hot-path context. If impact depends on workload and no workload context exists, say so or omit the finding.

## Architecture review

Treat the repository's existing architecture as context, not universal truth. Flag architectural issues when the change violates an established dependency/boundary rule or creates a concrete coupling, deployment, testing, ownership, or change-amplification problem.

## Project-system review

Treat MSBuild evaluation as repository-wide context. When project files change, inspect central props/targets, target frameworks, package management, and publish configuration before claiming the local XML is wrong.

## Completion

A successful review may contain zero findings.

Do not invent suggestions to make the review appear comprehensive. High precision is more valuable than high comment volume.


## Proveniência desta adaptação

Adaptada de `rodri-oliveira-dev/dotnet-copilot-code-review-skills/.github/skills/code-review/` para uso por agentes compatíveis com Agent Skills, inclusive Codex. As regras de revisão são complementares aos analisadores e controles determinísticos de cada repositório. Consulte o manifesto `catalog.curated.json` e os avisos de terceiros na raiz do catálogo. O repositório original não publicava uma licença explícita no commit de origem; a licença MIT desta adaptação precisa ser confirmada pelo mantenedor antes do merge.
