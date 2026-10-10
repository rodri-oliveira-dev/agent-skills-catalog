#!/usr/bin/env python3
"""Import complete official Agent Skill directories from pinned Git commits.

The allowlist lives in catalog.sources.json. This script copies vendor content
without executing it, and creates a reproducible file-hash lock file.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog.sources.json"
SKILLS = ROOT / "skills"
LICENSES = ROOT / "licenses"
LOCK = ROOT / "sources.lock.json"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, timeout=240)


def reject_unsafe_tree(root: Path) -> None:
    for entry in root.rglob("*"):
        if entry.is_symlink():
            raise ValueError(f"Unexpected symlink in upstream skill: {entry}")
        if entry.is_file() and entry.stat().st_size > 8_000_000:
            raise ValueError(f"Unexpected large upstream skill file: {entry}")


def fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported catalog manifest schema version")

    SKILLS.mkdir(exist_ok=True)
    LICENSES.mkdir(exist_ok=True)
    all_names: set[str] = set()
    locked = {"schema_version": 1, "sources": [], "skills": []}

    with tempfile.TemporaryDirectory(prefix="skill-import-") as tmp:
        for source in manifest["sources"]:
            repo, sha = source["repository"], source["commit"]
            if not REPO_PATTERN.fullmatch(repo) or not SHA_PATTERN.fullmatch(sha):
                raise ValueError(f"Invalid pinned source: {repo}@{sha}")

            # Treat upstream content as untrusted: no script execution or hooks.
            checkout = Path(tmp) / repo.replace("/", "__")
            git("clone", "--quiet", "--no-checkout", "--depth=1",
                "--filter=blob:none", "--sparse",
                f"https://github.com/{repo}.git", str(checkout))
            git("-C", str(checkout), "sparse-checkout", "set",
                "--", *(skill["path"] for skill in source["skills"]))
            # Fetch the exact reviewed SHA, not a moving main ref.
            git("-C", str(checkout), "fetch", "--quiet", "--depth=1", "origin", sha)
            git("-C", str(checkout), "checkout", "--quiet", "--detach", sha)

            for skill in source["skills"]:
                name = skill["name"]
                if not NAME_PATTERN.fullmatch(name) or name in all_names:
                    raise ValueError(f"Duplicate or invalid skill name: {name}")
                all_names.add(name)
                upstream = checkout / skill["path"]
                if not upstream.is_dir() or not (upstream / "SKILL.md").is_file():
                    raise FileNotFoundError(f"Missing upstream SKILL.md: {repo}/{skill['path']}")
                reject_unsafe_tree(upstream)
                meta = (upstream / "SKILL.md").read_text(encoding="utf-8")
                if not meta.startswith("---\n") or not re.search(
                    rf"(?m)^name:\s*['\"]?{re.escape(name)}['\"]?\s*$", meta
                ):
                    raise ValueError(f"Invalid skill frontmatter: {repo}/{skill['path']}")
                target = SKILLS / name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(upstream, target)
                locked["skills"].append({
                    "name": name, "category": skill["category"],
                    "source_repository": repo, "source_path": skill["path"],
                    "source_commit": sha, "files_sha256": fingerprint(target),
                })
                print(f"Imported {name}: {len(locked['skills'][-1]['files_sha256'])} files")

            # Preserve license and any publisher-supplied NOTICE without running
            # upstream scripts. A missing root LICENSE is permitted only for
            # Angular, whose selected SKILL.md files declare MIT individually.
            for legal_name in ("LICENSE", "NOTICE"):
                original = checkout / legal_name
                destination = LICENSES / (repo.replace("/", "__") + f".{legal_name}")
                if original.is_file():
                    shutil.copyfile(original, destination)
                elif legal_name == "LICENSE" and repo != "angular/skills":
                    raise FileNotFoundError(f"Missing upstream root license: {repo}/{legal_name}")
                elif destination.exists():
                    destination.unlink()

            locked["sources"].append({
                "repository": repo, "commit": sha, "license": source["license"]
            })

    LOCK.write_text(json.dumps(locked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Imported {len(locked['skills'])} curated skills from {len(locked['sources'])} pinned sources.")


if __name__ == "__main__":
    main()
