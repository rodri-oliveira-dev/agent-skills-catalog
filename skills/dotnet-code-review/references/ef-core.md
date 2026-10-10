# EF Core Review

Use this reference when changed code uses `DbContext`, `DbSet`, EF Core LINQ, tracking, `Include`, migrations, or EF Core transactions.

## Query shape

Check for:

- N+1 queries caused by per-row navigation access or query execution inside loops;
- unbounded materialization where data volume can grow;
- loading full entities when a small projection is all the operation needs and the reduction is meaningful;
- accidental client-side work after early materialization (`ToList`, `AsEnumerable`) that should remain server-side;
- repeated execution of the same `IQueryable` because deferred execution is misunderstood;
- non-deterministic pagination without a stable ordering.

## Tracking

- Use no-tracking queries for read-only workloads when tracking has no purpose and the result size/frequency makes it relevant.
- Do not demand `AsNoTracking` universally; tracking is required when entities are intentionally modified and saved.
- Check whether identity resolution matters when no-tracking projections contain repeated entity references.

## Related data

- Review `Include`/`ThenInclude` for large object graphs and cartesian multiplication.
- Consider split queries when multiple collection includes can cause significant row multiplication, but account for consistency and additional round trips.
- Prefer projections for read models when they materially reduce transferred data and simplify shape.
- Do not flag every `Include`; determine whether it is necessary for the requested result.

## Writes

- Check `SaveChanges` inside loops when changes could reasonably be batched.
- Check multiple `SaveChanges` calls when atomicity across them is required.
- For bulk updates/deletes on supported EF Core versions, `ExecuteUpdate`/`ExecuteDelete` may be appropriate when entity materialization is unnecessary and domain hooks are not required.
- Verify generated values, concurrency tokens, and tracked state are not assumed to be updated when bypassing normal tracked entity saves.

## Transactions and concurrency

- `SaveChanges` is transactional for its own operation, but multi-step workflows may require a larger transaction boundary.
- Check optimistic concurrency handling when concurrency tokens are used.
- Check retries and execution strategies when explicit transactions are introduced; retry behavior can change.
- Do not create a transaction solely because a single normal `SaveChanges` call exists.

## DbContext lifetime

- `DbContext` is not thread-safe. Do not share one context concurrently across tasks.
- Check singleton/background components for incorrect context lifetime.
- In background services, create/dispose scopes or use an appropriate context factory when needed.
- Avoid retaining tracked contexts/entities for long-lived application state.

## Translation and SQL semantics

- Check custom methods, unsupported expressions, date/time operations, string operations, and value conversions when query translation could differ from in-memory semantics.
- Avoid assuming a query is efficient solely from its LINQ appearance. If a claim depends on generated SQL or the execution plan, state that verification is needed.
- Parameterized values are normally handled safely by EF Core; raw SQL APIs require separate injection review.

## Raw SQL

- Distinguish interpolated APIs that parameterize values from APIs that accept raw executable SQL.
- Never pass untrusted identifiers or SQL fragments without strict allow-listing because parameterization cannot represent table/column/order keywords.

## Indexes

Do not automatically recommend an index for every filtered column. Index usefulness depends on selectivity, ordering, joins, table size, write cost, existing indexes, and the execution plan.

Report an index concern only when schema/workload evidence exists or phrase it as something to verify rather than a confirmed defect.

## Migrations

Check migrations for:

- destructive column/table changes;
- non-null additions without safe backfill/default strategy;
- long blocking operations on large tables;
- application/schema compatibility during rolling deployment;
- accidental data conversion or precision loss.

Generated migration snapshots are not normal application code; avoid style comments on them.

## Common false positives

Do not claim:

- every read query needs `AsNoTracking`;
- every `Include` is an N+1 problem;
- every LINQ query needs `CompileQuery`;
- repositories are required around `DbContext`;
- `DbContext` must be manually wrapped in Unit of Work;
- split queries are always faster;
- raw SQL is inherently better for performance.

Use repository context and workload evidence.
