# Dapper Review

Use this reference when changed code uses Dapper, `IDbConnection`, `DbConnection`, `CommandDefinition`, raw SQL, stored procedures, or Dapper query/execute APIs.

## SQL parameterization

- User-controlled values must be parameters, never concatenated or interpolated into executable SQL strings.
- Dynamic identifiers such as table names, column names, directions, and SQL keywords cannot be parameterized normally; require strict allow-listing when they are dynamic.
- Verify list expansion (`IN @Ids`) is intentional and bounded enough for the target database/driver.
- Check custom parameter objects and `DynamicParameters` for correct type, direction, size, precision, and value mapping when those details matter.

## Connection ownership

- Determine who owns the connection before recommending `using`/disposal.
- Dispose connections created by the changed code.
- Do not dispose a connection supplied by a caller unless the API contract transfers ownership.
- Check open connections/readers around streaming or unbuffered queries because resource lifetime extends through enumeration.

## Transactions

- Commands that must be atomic should share the intended connection and transaction.
- Verify a transaction object is passed to every participating Dapper command.
- Check commit/rollback/error behavior and ownership.
- Avoid adding explicit transactions around single statements without a real atomicity/isolation requirement.

## Query cardinality

Review whether the selected API matches expected row count:

- `QuerySingle*` expects exactly one row;
- `QuerySingleOrDefault*` expects zero or one;
- `QueryFirst*` requires at least one but permits extras;
- `QueryFirstOrDefault*` permits zero and ignores extras;
- `Query*` permits many.

Flag mismatches when extra/missing rows represent a real data or correctness defect.

## Async and cancellation

- Use async Dapper APIs in async server/background paths when database I/O should not block threads.
- Prefer `CommandDefinition` when cancellation, timeout, flags, or transaction metadata must be supplied together.
- Propagate the caller's `CancellationToken` into database work when cancellation is part of the operation contract.
- Check blocking `.Result`/`.Wait()` around Dapper async calls.

## Timeouts

- Distinguish connection timeout from command timeout.
- Do not recommend arbitrary longer timeouts as a fix for a slow query.
- Check intentionally long-running commands for an explicit policy when the default is known to be inappropriate.

## Buffering and streaming

- Buffered queries are often the safest default because rows are materialized while the connection can be released quickly.
- Unbuffered/streamed queries can reduce memory for large results but keep connection/reader resources occupied longer.
- Do not recommend streaming without considering connection-pool pressure and enumeration lifetime.

## Multi-mapping

Check:

- `splitOn` assumptions;
- duplicate parent aggregation when joining one-to-many relationships;
- missing children/null handling;
- row multiplication that creates large in-memory duplication;
- mapping order matching selected columns/types.

## Multiple result sets

For `QueryMultiple`/grid readers:

- consume result sets in the intended order;
- ensure optional/empty sets are handled correctly;
- dispose the reader/grid appropriately;
- keep connection lifetime valid until all required sets are consumed.

## Data types

Review potentially lossy or provider-sensitive mapping for:

- `decimal` precision/scale;
- `DateTime`/`DateTimeOffset` and time zones;
- GUID/UUID representation;
- enums;
- nullable database values;
- large text/binary values;
- provider-specific numeric and temporal types.

## Query performance

Prioritize database round trips and result size over local micro-optimizations.

Check for:

- queries inside loops;
- unbounded result sets;
- `SELECT *` when wide rows materially increase transfer/mapping cost;
- repeated identical queries within one operation;
- very large parameter lists;
- per-row writes that should be batched/bulked at meaningful scale.

Do not assert a missing index or bad execution plan without schema/plan evidence.

## Common false positives

Do not claim:

- every query needs a stored procedure;
- every Dapper call needs a repository wrapper;
- every connection must be manually opened before Dapper use;
- unbuffered queries are always faster;
- Dapper automatically solves SQL injection when the SQL text itself contains concatenated untrusted fragments.
