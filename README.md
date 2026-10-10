# Agent Skills Catalog

A curated and reproducible collection of official-source **Agent Skills** for coding agents, starting with .NET, Angular, Docker, Google Cloud (BigQuery) and Terraform.

This is an **independent community catalog**, not an official Microsoft, Google, Docker or HashiCorp distribution.

## Licensing and third-party content

**The root [MIT license](LICENSE) applies to this catalog's original code,
documentation and tooling. It does not relicense vendored Agent Skills.**
Each copied skill retains its upstream license and copyright obligations:

- **MIT** (.NET and Angular): preserve the applicable copyright and permission notices. Angular's selected skills declare MIT individually in their frontmatter.
- **Apache-2.0** (Docker and Google Cloud): retain the Apache license, relevant attribution/NOTICE files where supplied, and identify modifications when made.
- **MPL-2.0** (HashiCorp Terraform): keep the MPL on covered upstream files and modifications to those files; independently authored catalog files can remain MIT.

The source repository, upstream commit and original skill path are pinned in
[`catalog.sources.json`](catalog.sources.json). License copies and publisher
attribution are recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
The importer preserves upstream skill files unchanged; this catalog does not
claim ownership or official endorsement of third-party content.

Run `python3 scripts/validate_licenses.py` locally to verify license evidence,
source attribution and integrity hashes. Changes to publishers or license types
require an explicit policy review; the CI will reject unreviewed licenses.

## Initial selection

| Area | Skills |
| --- | --- |
| .NET / C# / EF Core | `csharp-refactoring`, `optimizing-ef-core-queries` |
| .NET testing | `run-tests`, `scaffold-dotnet-test-project`, `platform-detection`, `filter-syntax`, `test-anti-patterns`, `test-analysis-extensions` |
| Angular | `angular-developer`, `angular-new-app` |
| Docker | `docker-project-foundations`, `docker-build-strategies`, `docker-compose-patterns`, `docker-destructive-guardrails` |
| Google Cloud | `bigquery-basics` |
| Terraform | `terraform-style-guide` |

The complete folder for each skill lives at `skills/<name>/`, including any `references/`, `scripts/`, `assets/`, `checks/`, or other upstream files. A skill's presence here does not mean it is installed automatically in every consumer repository.

## Install in Codex

Using the [Skills CLI](https://github.com/vercel-labs/skills), list what this repository publishes:

```sh
npx skills add rodri-oliveira-dev/agent-skills-catalog --list
```

Install only the skill you need (example):

```sh
npx skills add rodri-oliveira-dev/agent-skills-catalog --skill docker-compose-patterns --agent codex --copy --yes
```

## Source of truth and provenance

- [`catalog.sources.json`](catalog.sources.json) is an explicit allowlist of **official upstream folders**, with a pinned source commit, category and license.
- [`scripts/sync_official_skills.py`](scripts/sync_official_skills.py) fetches those exact commits and copies complete skill directories without executing vendor scripts.
- [`sources.lock.json`](sources.lock.json) is generated after import with SHA-256 checksums for every mirrored file.
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) attributes each publisher and its license.

### Updating official skills

For now, upgrades require reviewing and changing the pinned commit in `catalog.sources.json`, running the importer, reviewing the diff, and opening a PR. **There is no scheduled update or automatic merge in this first phase.** The bootstrap workflow imports the first snapshot into the feature branch for review.

### Not in scope yet

- Mirroring personal/community skills from other repositories.
- Automatic skill recommendation by repository dependencies, architectural patterns or testing tools.
- An automatic upstream-update scheduling or alerting system.

These will be separate, reviewable improvements. Treat all imported scripts and Agent Skill instructions as untrusted until reviewed.
