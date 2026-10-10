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



def reconcile_removed(
    previous_lock: dict,
    desired_names: set[str],
    desired_repositories: set[str],
    curated_names: set[str],
    protected_license_filenames: set[str],
    *,
    skills_dir: Path,
    licenses_dir: Path,
) -> tuple[list[str], list[str]]:
    """Prune only prior *official-managed* entries no longer allowlisted.

    Never remove unknown directories or adapted/internal skills: other catalog
    categories maintain their own manifests and lifecycles. Unknown entries
    are rejected later by the validator instead of silently deleted.
    """
    removed_skills: list[str] = []
    removed_licenses: list[str] = []

    for item in previous_lock.get("skills", []):
        name = item["name"]
        if not NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Unsafe name in previous official lock: {name!r}")
        if name in desired_names or name in curated_names:
            continue
        target = skills_dir / name
        if target.is_symlink():
            raise ValueError(f"Refusing to delete symlinked skill: {target}")
        if target.is_dir():
            shutil.rmtree(target)
            removed_skills.append(name)
        elif target.exists():
            raise ValueError(f"Unexpected non-directory in official skill path: {target}")

    for item in previous_lock.get("sources", []):
        repo = item["repository"]
        if not REPO_PATTERN.fullmatch(repo) or any(part in (".", "..") for part in repo.split("/")):
            raise ValueError(f"Unsafe repository in previous official lock: {repo!r}")
        if repo in desired_repositories:
            continue
        prefix = repo.replace("/", "__")
        for legal_name in ("LICENSE", "NOTICE"):
            filename = f"{prefix}.{legal_name}"
            if filename in protected_license_filenames:
                continue
            target = licenses_dir / filename
            if target.is_symlink():
                raise ValueError(f"Refusing to delete symlinked license: {target}")
            if target.is_file():
                target.unlink()
                removed_licenses.append(filename)
            elif target.exists():
                raise ValueError(f"Unexpected non-file in license path: {target}")

    return removed_skills, removed_licenses




def adapt_unbundled_skill_links(content: str, repo: str, sha: str, name: str) -> str:
    """Replace an unavailable sibling-skill link with a pinned upstream URL.

    A source repo can contain more skills than our reviewed allowlist, and the
    Skills CLI can install an individual skill without its siblings. Keep this
    explicitly documented local fix deterministic and narrow in scope.
    """
    if (repo, name) != ("google/skills", "bigquery-basics"):
        return content
    broken_link = "](../bigquery-ai-ml)"
    if content.count(broken_link) != 1:
        raise ValueError("BigQuery upstream cross-skill link changed; manual review needed")
    fixed_link = (
        "](https://github.com/google/skills/tree/"
        f"{sha}/skills/cloud/bigquery-ai-ml)"
    )
    return content.replace(broken_link, fixed_link)



def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported catalog manifest schema version")

    SKILLS.mkdir(exist_ok=True)
    LICENSES.mkdir(exist_ok=True)
    # Keep a snapshot of the last official-managed state *before* overwriting
    # sources.lock.json, including skills that may have been removed/renamed.
    previous_lock = json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.is_file() else {}
    curated_manifest = ROOT / "catalog.curated.json"
    curated_data = json.loads(curated_manifest.read_text(encoding="utf-8")) if curated_manifest.is_file() else {}
    curated_names = {entry["id"] for entry in curated_data.get("skills", [])}
    protected_license_filenames = {
        Path(entry["source_license_file"]).name
        for entry in curated_data.get("skills", [])
        if entry.get("source_license_file")
    }
    desired_names = {skill["name"] for source in manifest["sources"] for skill in source["skills"]}
    desired_repositories = {source["repository"] for source in manifest["sources"]}
    if desired_names & curated_names:
        raise ValueError("Official skills overlap with independently curated skills")
    all_names: set[str] = set()
    locked = {"schema_version": 1, "sources": [], "skills": []}

    with tempfile.TemporaryDirectory(prefix="skill-import-") as tmp:
        for source in manifest["sources"]:
            repo, sha = source["repository"], source["commit"]
            if (not REPO_PATTERN.fullmatch(repo)
                or any(part in (".", "..") for part in repo.split("/"))
                or not SHA_PATTERN.fullmatch(sha)):
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
                if target.is_symlink():
                    raise ValueError(f"Refusing to replace symlinked skill: {target}")
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(upstream, target)
                # Only adjust the single documented BigQuery sibling link;
                # consumers can install bigquery-basics without AI/ML.
                curated_meta = adapt_unbundled_skill_links(meta, repo, sha, name)
                if curated_meta != meta:
                    (target / "SKILL.md").write_text(curated_meta, encoding="utf-8")
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

    # Only after a successful import, reconcile previously published official
    # entries against the current allowlist. Preserve independently curated
    # skills and their licenses in subsequent phases.
    removed_skills, removed_licenses = reconcile_removed(
        previous_lock,
        desired_names,
        desired_repositories,
        curated_names,
        protected_license_filenames,
        skills_dir=SKILLS,
        licenses_dir=LICENSES,
    )
    LOCK.write_text(json.dumps(locked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Imported {len(locked['skills'])} official skills from {len(locked['sources'])} pinned sources.")
    print(f"Removed obsolete official skills: {removed_skills}; licenses: {removed_licenses}")


if __name__ == "__main__":
    main()
