#!/usr/bin/env python3
"""Validate the curated catalog's third-party license and source metadata.

Offline and read-only: this check never fetches or executes upstream content.
It verifies legal evidence and that pinned skill snapshots match the lock file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

# Adding a publisher requires an explicit license-policy review.
SOURCE_POLICY = {
    "dotnet/skills": ("MIT", "repository"),
    "angular/skills": ("MIT", "per-skill"),
    "docker/skills": ("Apache-2.0", "repository"),
    "google/skills": ("Apache-2.0", "repository"),
    "hashicorp/agent-skills": ("MPL-2.0", "repository"),
}
LICENSE_MARKERS = {
    "MIT": ("MIT License", "Permission is hereby granted"),
    "Apache-2.0": ("Apache License", "Version 2.0"),
    "MPL-2.0": ("Mozilla Public License Version 2.0",),
}
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SKILL_NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        fail(f"Missing YAML frontmatter: {skill_md}")
    return match.group(1)


def declared_license(metadata: str) -> str | None:
    match = re.search(r"(?m)^license:\s*['\"]?([A-Za-z0-9.-]+)", metadata)
    return match.group(1) if match else None


def validate(root: Path) -> int:
    root = root.resolve()
    manifest = read_json(root / "catalog.sources.json")
    lock = read_json(root / "sources.lock.json")
    if manifest.get("schema_version") != 1 or lock.get("schema_version") != 1:
        fail("Unsupported catalog/lock schema")

    main_license = root / "LICENSE"
    if not main_license.is_file():
        fail("Missing MIT license for original catalog code")
    main_text = main_license.read_text(encoding="utf-8")
    if not all(marker in main_text for marker in LICENSE_MARKERS["MIT"]):
        fail("Root LICENSE must remain the complete MIT license")

    notice_file = root / "THIRD_PARTY_NOTICES.md"
    if not notice_file.is_file():
        fail("Missing THIRD_PARTY_NOTICES.md")
    notices = notice_file.read_text(encoding="utf-8")

    sources = manifest.get("sources", [])
    lock_sources = {s["repository"]: s for s in lock.get("sources", [])}
    lock_skills = {s["name"]: s for s in lock.get("skills", [])}
    if len(lock_sources) != len(lock.get("sources", [])):
        fail("Duplicate upstream sources in lock file")
    if len(lock_skills) != len(lock.get("skills", [])):
        fail("Duplicate skills in lock file")

    expected_names: set[str] = set()
    expected_repositories: set[str] = set()
    for source in sources:
        repo, commit = source["repository"], source["commit"]
        if repo in expected_repositories:
            fail(f"Duplicate upstream source: {repo}")
        expected_repositories.add(repo)
        if repo not in SOURCE_POLICY:
            fail(f"Unreviewed publisher/license: {repo}")
        if not SHA40.fullmatch(commit):
            fail(f"Invalid pinned commit: {repo}")
        spdx, evidence = SOURCE_POLICY[repo]
        expected_declaration = spdx if evidence == "repository" else f"{spdx} (per-skill frontmatter)"
        if source.get("license") != expected_declaration:
            fail(f"Source license declaration differs from reviewed policy: {repo}")
        locked_source = lock_sources.get(repo)
        if not locked_source or any(locked_source.get(k) != source.get(k) for k in ("commit", "license")):
            fail(f"Upstream source metadata differs from lock file: {repo}")

        row = next((line for line in notices.splitlines()
                    if line.startswith("|") and f"https://github.com/{repo}" in line), "")
        if not row or f"| {spdx}" not in row:
            fail(f"Missing upstream attribution/license in THIRD_PARTY_NOTICES.md: {repo}")

        if evidence == "repository":
            relative = f"licenses/{repo.replace('/', '__')}.LICENSE"
            legal_path = root / relative
            if not legal_path.is_file():
                fail(f"Missing copied upstream license: {relative}")
            legal_text = legal_path.read_text(encoding="utf-8")
            if not all(marker in legal_text for marker in LICENSE_MARKERS[spdx]):
                fail(f"Copied upstream license does not match expected license: {repo}")
            if relative not in row:
                fail(f"Missing upstream license file reference in notices: {repo}")
        elif "frontmatter" not in row:
            fail(f"Missing Angular per-skill license explanation in notices: {repo}")

        for skill in source.get("skills", []):
            name = skill["name"]
            if not SKILL_NAME.fullmatch(name) or name in expected_names:
                fail(f"Invalid or duplicate skill name: {name}")
            expected_names.add(name)
            folder = root / "skills" / name
            skill_md = folder / "SKILL.md"
            if not skill_md.is_file() or skill_md.is_symlink():
                fail(f"Missing/untrusted skill manifest: {skill_md}")
            meta = frontmatter(skill_md)
            declared = declared_license(meta)
            if evidence == "per-skill" and declared != spdx:
                fail(f"Skill must declare {spdx} in frontmatter: {name}")
            if declared is not None and declared != spdx:
                fail(f"Skill's declared license differs from publisher: {name}")

            locked_skill = lock_skills.get(name)
            if not locked_skill:
                fail(f"Skill missing from sources.lock.json: {name}")
            required = {
                "source_repository": repo, "source_commit": commit,
                "source_path": skill["path"], "category": skill["category"],
            }
            if any(locked_skill.get(k) != value for k, value in required.items()):
                fail(f"Skill provenance differs from lock file: {name}")
            locked_files = locked_skill.get("files_sha256")
            if not isinstance(locked_files, dict) or "SKILL.md" not in locked_files:
                fail(f"Skill lacks a complete file-hash inventory: {name}")
            actual: dict[str, str] = {}
            for file in folder.rglob("*"):
                if file.is_symlink():
                    fail(f"Symlink in copied skill: {file}")
                if file.is_file():
                    actual[file.relative_to(folder).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
            if any(not isinstance(value, str) or not SHA256.fullmatch(value)
                   for value in locked_files.values()) or actual != locked_files:
                fail(f"Skill files were added/removed/changed without updating the lock: {name}")

    if expected_repositories != set(lock_sources):
        fail("Source set differs between catalog and lock")
    if expected_names != set(lock_skills):
        fail("Skill set differs between catalog and lock")
    # Internal/curated skills are independently tracked and validated by
    # scripts/validate_curated_skills.py; they are never treated as official
    # vendor snapshots or written into sources.lock.json.
    curated_manifest = root / "catalog.curated.json"
    curated_names: set[str] = set()
    if curated_manifest.is_file():
        curated_data = read_json(curated_manifest)
        if curated_data.get("schema_version") != 1:
            fail("Unsupported curated manifest schema")
        curated_names = {entry["id"] for entry in curated_data.get("skills", [])}
        if curated_names & expected_names:
            fail("Official and curated catalogs contain duplicate skill names")
        if len(curated_names) != len(curated_data.get("skills", [])):
            fail("Duplicate names in curated catalog")
    actual_names = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    if actual_names != expected_names | curated_names:
        fail("Skill directories differ from official + curated catalog allowlists")
    return len(expected_names)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    count = validate(args.root)
    print(f"Validated provenance, license evidence and hashes for {count} skills.")


if __name__ == "__main__":
    main()
