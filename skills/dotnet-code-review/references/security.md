# Security Review

Use this reference when the changed code handles authentication, authorization, credentials, untrusted input, file/URL/path handling, cryptography, serialization, sensitive data, or external process/network access.

## Authentication and authorization

- Verify sensitive operations are protected by the intended authentication scheme and authorization policy.
- Check object/resource ownership when users can supply identifiers for records they do not necessarily own.
- Check tenant isolation and claims/identity sources for user-controlled overrides.
- Do not rely on UI hiding, route naming, or client-side checks as authorization.
- Check alternate paths that reach the same operation, including background jobs and internal endpoints.

## Injection

Review untrusted values entering:

- SQL or database commands;
- shell/process arguments;
- templates;
- LDAP or other query languages;
- log message templates when structure can be manipulated;
- headers or downstream protocols.

Prefer parameterization/structured APIs. For dynamic identifiers or syntax that cannot be parameterized, require strict allow-listing.

## Secrets and sensitive data

- Flag committed passwords, API keys, access tokens, certificates/private keys, connection credentials, or other secrets.
- Check logs and exceptions for tokens, credentials, authorization headers, personal data, payment data, or sensitive domain values.
- Avoid returning internal exception details or stack traces to untrusted clients.
- Check telemetry dimensions for accidental high-cardinality or sensitive values when relevant.

## URL and network access

For user-controlled or externally supplied URLs:

- consider SSRF against loopback, link-local, cloud metadata, internal networks, or restricted services;
- validate allowed schemes/hosts/ports when the feature is intended to reach only known destinations;
- consider redirects and DNS resolution behavior when allow-listing is security-sensitive.

Do not report SSRF merely because `HttpClient` exists; there must be an attacker-influenced destination or equivalent trust boundary.

## Files and paths

- Check path traversal when untrusted input influences filesystem paths.
- Normalize/resolve paths and verify the final path stays within the intended root when that is the security boundary.
- Check uploaded file size/type/name handling and storage outside executable/static roots when applicable.
- Never trust the client-provided filename as a safe storage path.

## Deserialization and parsing

- Treat input payloads as untrusted.
- Flag unsafe polymorphic/type-name deserialization that can instantiate attacker-selected types.
- Check decompression/archive processing for path traversal and unbounded expansion when applicable.
- Check parsers for unbounded payload size or recursion on attacker-controlled input in exposed paths.

## Cryptography

- Do not invent custom cryptographic algorithms or protocols.
- Check obsolete hashes/ciphers when used for security rather than non-security checksums.
- Passwords should use a purpose-built password hashing/KDF implementation, not a fast general-purpose hash.
- Random security tokens/nonces must use a cryptographically secure RNG.
- Check key/nonce/IV reuse and storage only when the changed code actually implements those responsibilities.

## ASP.NET Core specifics

- Check authentication/authorization middleware and endpoint metadata together.
- Verify CORS changes do not confuse cross-origin browser policy with API authentication.
- Review forwarded headers/proxy trust when client IP, scheme, or host affects security decisions.
- Check cookie security properties when authentication/session cookies are modified.
- Review antiforgery for browser cookie-authenticated state-changing flows where it is applicable; do not demand it for bearer-token APIs without a browser credential context.

## Validation versus authorization

Input validation answers "is this value structurally valid?" Authorization answers "may this caller perform this action?" One does not replace the other.

## Severity guidance

- BLOCKER: clear exploitable auth bypass, injection, committed production secret, arbitrary file/process execution, or direct sensitive data exposure.
- HIGH: plausible privilege escalation, tenant escape, SSRF to protected resources, or serious sensitive logging.
- MEDIUM: defense gaps whose exploitability depends on deployment/context.

Avoid speculative security comments without an attacker-controlled input, trust boundary, and plausible impact.
