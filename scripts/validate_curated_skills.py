#!/usr/bin/env python3
"""Offline validation of curated first-party and internally adapted Agent Skills."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SHA1 = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
UPSTREAM_LICENSES = {
    "ciembor/agent-rules-books": "licenses/ciembor__agent-rules-books.LICENSE",
    "tango238/distill-ddd": "licenses/tango238__distill-ddd.LICENSE",
}


def blob_sha(data: bytes) -> str:
    """Compute the Git blob object ID (SHA-1), *not* a raw-content SHA-1."""
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def validate_curated(root: Path) -> set[str]:
    """Check curated metadata and return names included in the catalog.

    If a checkout predates the curated catalog, there is nothing to validate.
    Never interpret a missing manifest as permission to distribute extra skills.
    """
    root = root.resolve()
    manifest_file = root / "catalog.curated.json"
    if not manifest_file.is_file():
        return set()

    document = json.loads(manifest_file.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1:
        raise ValueError("Unsupported curated catalog schema")
    entries = document.get("skills")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Curated manifest must include skills")

    notices = root / "THIRD_PARTY_NOTICES.md"
    if not notices.is_file():
        raise ValueError("Missing third-party notices for curated skills")
    notice_text = notices.read_text(encoding="utf-8")
    names: set[str] = set()
    attributed: set[str] = set()

    for item in entries:
        name = item.get("id", "")
        if not NAME.fullmatch(name) or name in names:
            raise ValueError(f"Invalid or duplicated curated skill: {name}")
        names.add(name)
        if item.get("path") != f"skills/{name}":
            raise ValueError(f"Invalid curated skill path: {name}")

        owner = item.get("source_repository", "")
        if owner not in {
            "rodri-oliveira-dev/poc-arquitetura",
            "rodri-oliveira-dev/dotnet-copilot-code-review-skills",
            "rodri-oliveira-dev/dotnet-library-template",
        }:
            raise ValueError(f"Unreviewed curated source repository: {owner}")
        for key in ("source_commit", "source_skill_blob_sha"):
            if not SHA1.fullmatch(item.get(key, "")):
                raise ValueError(f"Missing immutable origin {key}: {name}")

        origin_path = item.get("source_skill_path", "")
        if not origin_path.endswith("/SKILL.md") or ".." in Path(origin_path).parts:
            raise ValueError(f"Invalid origin skill path: {name}")
        if item.get("catalog_license") != "MIT":
            raise ValueError(f"Curated skill requires catalog MIT license review: {name}")

        is_pending = item.get("license_review") == "pending-maintainer-confirmation"
        is_approved = item.get("license_review") == "approved"
        if not (is_pending or is_approved):
            raise ValueError(f"Missing explicit license review status: {name}")
        original_license = item.get("source_license")
        license_evidence = item.get("source_license_file")
        if original_license == "MIT":
            if is_pending or not license_evidence:
                raise ValueError(f"Unexpected source MIT licensing state: {name}")
            license_text = (root / license_evidence).read_text(encoding="utf-8")
            if "MIT License" not in license_text or "Permission is hereby granted" not in license_text:
                raise ValueError(f"Source license text invalid: {name}")
        elif original_license == "not-published-in-source-repository":
            if not is_pending or license_evidence is not None:
                raise ValueError(f"Unlicensed upstream must be marked for maintainer confirmation: {name}")
        else:
            raise ValueError(f"Unreviewed original license: {name}")

        folder = root / item["path"]
        skill = folder / "SKILL.md"
        if not skill.is_file() or skill.is_symlink():
            raise ValueError(f"Missing curated SKILL.md: {name}")
        content = skill.read_text(encoding="utf-8")
        header = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
        if not header:
            raise ValueError(f"Missing curated frontmatter: {name}")
        if not re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", header.group(1)):
            raise ValueError(f"Curated skill frontmatter name mismatch: {name}")
        if not re.search(r"(?m)^license:\s*MIT\s*$", header.group(1)):
            raise ValueError(f"Curated skill lacks its MIT declaration: {name}")

        inventory = item.get("files_git_blob_sha1")
        if not isinstance(inventory, dict) or "SKILL.md" not in inventory:
            raise ValueError(f"Missing curated file inventory: {name}")
        actual: dict[str, str] = {}
        for path in folder.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Unreviewed symlink in curated skill: {path}")
            if path.is_file():
                actual[path.relative_to(folder).as_posix()] = blob_sha(path.read_bytes())
        if actual != inventory:
            raise ValueError(f"Curated skill file hashes differ from catalog: {name}")

        for source in item.get("upstream_attributions", []):
            if source not in UPSTREAM_LICENSES:
                raise ValueError(f"Unknown derivative upstream: {source}")
            attributed.add(source)
            license_file = root / UPSTREAM_LICENSES[source]
            if not license_file.is_file():
                raise ValueError(f"Missing derivative source license: {source}")
            license_text = license_file.read_text(encoding="utf-8")
            if "MIT License" not in license_text or "Permission is hereby granted" not in license_text:
                raise ValueError(f"Invalid derivative MIT license text: {source}")

        if owner not in notice_text:
            raise ValueError(f"Missing attribution for internal source: {owner}")

    for source in attributed:
        if source not in notice_text:
            raise ValueError(f"Missing derivative-source attribution: {source}")
    return names


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    names = validate_curated(root)
    print(f"Validated {len(names)} curated skills.")


if __name__ == "__main__":
    main()
