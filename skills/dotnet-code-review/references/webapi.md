# ASP.NET Core Web API Review

Use this reference for controllers, Minimal APIs, endpoint filters, middleware, request/response DTOs, HTTP clients, and public HTTP contracts.

## Contract correctness

Review changes to:

- routes and route constraints;
- HTTP methods;
- request binding sources;
- required/optional fields;
- JSON names and serialization behavior;
- response DTO shape;
- status codes and error bodies;
- content types;
- OpenAPI-visible contracts;
- API version behavior.

Treat accidental consumer-visible changes as compatibility risks even if the server still compiles.

## HTTP semantics

- Use methods and status codes that match actual behavior and existing API conventions.
- Distinguish `400` validation failures, `401` unauthenticated, `403` unauthorized, `404` resource hiding/not found, `409` conflicts, and `422` only according to the project's established contract.
- Check `201 Created` location/resource semantics when used.
- Avoid returning success status when an operation partially or completely failed.
- Check caching headers only when endpoint cache semantics are intentionally changed.

Do not report a status-code preference when multiple choices are valid and the repository already has a convention.

## Validation

- Validate untrusted boundary input before performing side effects when invalid values can cause incorrect behavior.
- Distinguish transport validation from domain invariants.
- Check collection/page sizes and payload sizes when unbounded client input can create resource risk.
- Do not duplicate validation across layers without a concrete reason.

## Cancellation

- Propagate the endpoint/request cancellation token into database, HTTP, file, queue, and other cancellable I/O.
- Do not treat client disconnect cancellation as an application error that should necessarily produce noisy error logs.
- Preserve operation-specific timeouts when they differ from request lifetime.

## Authentication and authorization

- Check endpoint metadata/policies and resource-level authorization together.
- Validate ownership/tenant boundaries after resource lookup when authorization depends on the resource.
- Do not accept caller identity/tenant claims from arbitrary request fields when the server already has authenticated identity context.

## Idempotency and retries

Review write endpoints for duplicate side effects when:

- clients/gateways can retry;
- a request publishes a message and writes a database;
- external payment/order/provisioning actions occur;
- the endpoint exposes an explicit idempotency key.

Do not require idempotency on every POST; require it where duplicate execution is materially harmful and retries are plausible.

## Pagination and large results

- Avoid unbounded collection responses when cardinality can grow substantially.
- Check stable ordering across pages.
- Check page size limits.
- For cursor/keyset pagination, verify cursor semantics remain stable and unique enough for the ordering.

## Error handling

- Avoid leaking exception messages, stack traces, SQL, secrets, or internal topology to clients.
- Prefer a consistent project error contract, often Problem Details in modern ASP.NET Core applications.
- Preserve correlation/trace context where existing observability relies on it.
- Avoid catch-all handlers that convert programming/system failures into misleading success or client-error responses.

## Middleware

When middleware changes, check ordering and short-circuit behavior involving:

- exception handling;
- forwarded headers;
- HTTPS/redirection;
- routing;
- CORS;
- authentication;
- authorization;
- rate limiting;
- response caching/output caching;
- endpoints/static files.

Middleware ordering is contextual. Verify against the actual pipeline before reporting a defect.

## HTTP clients

- Check per-request `HttpClient`/handler construction for socket/DNS lifetime issues when not managed intentionally.
- Check cancellation and timeout composition.
- Check non-success responses before blindly deserializing success models.
- Check retries for unsafe methods and retry storms.
- Do not retry non-idempotent operations automatically without a safe policy.

## File endpoints

For uploads/downloads:

- validate size and resource limits;
- avoid trusting client filenames as filesystem paths;
- check path traversal;
- stream large files when buffering creates a material memory risk;
- preserve correct content type/disposition and authorization.

## Common false positives

Do not require:

- controllers instead of Minimal APIs, or the reverse;
- FluentValidation instead of DataAnnotations or custom validation;
- a specific API versioning library;
- MediatR/CQRS for endpoints;
- Problem Details when the repository intentionally has another stable error contract.
