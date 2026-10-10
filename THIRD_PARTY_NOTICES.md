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
