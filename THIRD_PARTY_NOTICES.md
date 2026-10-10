# Third-party notices

**Scope of the MIT license:** the root `LICENSE` governs original catalog
source code, tooling and documentation. It does **not** relicense vendored
third-party skills. Their original copyright and license obligations remain in
effect for each upstream file, including any later modifications.

This catalog redistributes copies of selected upstream skill folders with
their references, assets and scripts. The pinned sources and original paths
are listed in [`catalog.sources.json`](catalog.sources.json); file checksums
are in [`sources.lock.json`](sources.lock.json).

| Source | License | Copyright / attribution |
| --- | --- | --- |
| [dotnet/skills](https://github.com/dotnet/skills) | MIT | .NET Foundation and Contributors; see `licenses/dotnet__skills.LICENSE` |
| [angular/skills](https://github.com/angular/skills) | MIT (per-skill frontmatter) | Angular Team / Google LLC. Both selected `SKILL.md` files declare MIT; the upstream skills repository did not publish a root `LICENSE` at the pinned revision. Preserve the original file-level attribution. |
| [docker/skills](https://github.com/docker/skills) | Apache-2.0 | Docker and contributors; see `licenses/docker__skills.LICENSE` |
| [google/skills](https://github.com/google/skills) | Apache-2.0 | Google and contributors; see `licenses/google__skills.LICENSE` |
| [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) | MPL-2.0 | HashiCorp and contributors; see `licenses/hashicorp__agent-skills.LICENSE` |

For MIT content, retain its permission and copyright notices. For Apache-2.0
content, retain its license and any applicable upstream NOTICE file and mark
modified files. For MPL-2.0 content, retain the MPL on covered files and
modifications; respect its source-availability requirements when distributing
modified covered files. These requirements are separate from the catalog's MIT
license. The importer's copies are intended to be unmodified.

The offline validator (`scripts/validate_licenses.py`) checks the approved
publishers, declared license types, copied license texts (or Angular's per-skill
declaration), attribution rows and file-hash inventory. New license types or
unknown publishers cannot pass without deliberate policy changes.

This is an independent community catalog, **not** an official redistribution
or endorsement by Microsoft, Google, Docker or HashiCorp. Some skills require
tools or components not provided here.

## Curated internal skills — P0

Unlike the verbatim official-source `skills`, the entries below are **reviewed adaptations**
of skills authored or maintained in this GitHub account. They are tracked separately in
[`catalog.curated.json`](catalog.curated.json) with immutable source commit, original
path, original skill blob SHA, license review status and hashes of catalog files.
Modifications to adapted content are intentional and can be inspected against the pinned source.

| Curated skill | Source | Legal status |
| --- | --- | --- |
| `ddd-domain-modeling` | [rodri-oliveira-dev/poc-arquitetura](https://github.com/rodri-oliveira-dev/poc-arquitetura) | Local MIT adaptation; third-party origins acknowledged below |
| `ddd-dotnet-implementation` | [rodri-oliveira-dev/poc-arquitetura](https://github.com/rodri-oliveira-dev/poc-arquitetura) | Local MIT adaptation; third-party origins acknowledged below |
| `integration-tests-dotnet` | [rodri-oliveira-dev/poc-arquitetura](https://github.com/rodri-oliveira-dev/poc-arquitetura) | MIT: `licenses/rodri-oliveira-dev__poc-arquitetura.LICENSE` |
| `repository-governance-sdd` | [rodri-oliveira-dev/poc-arquitetura](https://github.com/rodri-oliveira-dev/poc-arquitetura) | MIT: `licenses/rodri-oliveira-dev__poc-arquitetura.LICENSE` |
| `dotnet-code-review` | [rodri-oliveira-dev/dotnet-copilot-code-review-skills](https://github.com/rodri-oliveira-dev/dotnet-copilot-code-review-skills) | **Pending original owner/contributor confirmation**: the source repository has no published root license at the pinned revision. The adapted copy declares MIT in this catalog; review redistribution rights before merging. |

### DDD derivative attribution

The two curated DDD skills were adapted earlier from open-source material and are
**not official skills created by Vaughn Vernon**:

- [ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books) — based on
  `implementing-domain-driven-design/implementing-domain-driven-design.mini.md`
  and `domain-driven-design-distilled/domain-driven-design-distilled.mini.md`.
  **MIT, copyright (c) 2026 Maciej Ciemborowicz**.
  Full license: `licenses/ciembor__agent-rules-books.LICENSE`.
- [tango238/distill-ddd](https://github.com/tango238/distill-ddd) — source workflow
  `SKILL.md` and `README.md`, inspiring domain discovery and modeling.
  **MIT, copyright (c) 2026 Go Tanaka**.
  Full license: `licenses/tango238__distill-ddd.LICENSE`.

Books by Vaughn Vernon and Scott Wlaschin are cited as conceptual references,
not reproduced as licensed skill files. No upstream publisher endorses this catalog.

**License rule:** the MIT license at the catalog root covers newly authored catalog
components and appropriately licensed local adaptations; official mirrors always
retain their respective upstream licenses. Confirm unresolved ownership before
distributing a curated adaptation.
