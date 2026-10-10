"""Regression tests for third-party license/provenance enforcement."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_licenses import validate


SOURCES = (
    ("dotnet/skills", "MIT", "repository"),
    ("angular/skills", "MIT", "per-skill"),
    ("docker/skills", "Apache-2.0", "repository"),
    ("google/skills", "Apache-2.0", "repository"),
    ("hashicorp/agent-skills", "MPL-2.0", "repository"),
)
LICENSE_TEXT = {
    "MIT": "MIT License\nPermission is hereby granted\n",
    "Apache-2.0": "Apache License\nVersion 2.0, January 2004\n",
    "MPL-2.0": "Mozilla Public License Version 2.0\n",
}


class LicenseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "LICENSE").write_text(LICENSE_TEXT["MIT"], encoding="utf-8")
        (self.root / "skills").mkdir()
        (self.root / "licenses").mkdir()
        self.manifest = {"schema_version": 1, "sources": []}
        self.lock = {"schema_version": 1, "sources": [], "skills": []}
        rows = []
        for index, (repo, spdx, evidence) in enumerate(SOURCES):
            sha = f"{index + 1:040x}"
            license_decl = spdx if evidence == "repository" else f"{spdx} (per-skill frontmatter)"
            name = f"test-skill-{index}"
            relative = f"plugins/test/skills/{name}"
            self.manifest["sources"].append({
                "repository": repo, "commit": sha, "license": license_decl,
                "skills": [{"name": name, "path": relative, "category": "test"}],
            })
            self.lock["sources"].append({
                "repository": repo, "commit": sha, "license": license_decl,
            })
            folder = self.root / "skills" / name
            folder.mkdir()
            meta = f"---\nname: {name}\nlicense: {spdx}\n---\n\n# Test fixture\n"
            (folder / "SKILL.md").write_text(meta, encoding="utf-8")
            digest = hashlib.sha256(meta.encode("utf-8")).hexdigest()
            self.lock["skills"].append({
                "name": name, "source_repository": repo,
                "source_commit": sha, "source_path": relative,
                "category": "test", "files_sha256": {"SKILL.md": digest},
            })
            link = f"[{repo}](https://github.com/{repo})"
            if evidence == "repository":
                license_path = f"licenses/{repo.replace('/', '__')}.LICENSE"
                (self.root / license_path).write_text(LICENSE_TEXT[spdx], encoding="utf-8")
                rows.append(f"| {link} | {spdx} | {license_path} |")
            else:
                rows.append(f"| {link} | {spdx} (per-skill frontmatter) | Copyright |")
        (self.root / "THIRD_PARTY_NOTICES.md").write_text("\n".join(rows), encoding="utf-8")
        self.save()

    def save(self) -> None:
        (self.root / "catalog.sources.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )
        (self.root / "sources.lock.json").write_text(
            json.dumps(self.lock), encoding="utf-8"
        )

    def test_valid_catalog(self) -> None:
        self.assertEqual(validate(self.root), 5)

    def test_missing_root_mit_license(self) -> None:
        (self.root / "LICENSE").unlink()
        with self.assertRaisesRegex(ValueError, "Missing MIT license"):
            validate(self.root)

    def test_unknown_upstream_is_rejected(self) -> None:
        self.manifest["sources"][0]["repository"] = "unknown/skills"
        self.save()
        with self.assertRaisesRegex(ValueError, "Unreviewed publisher"):
            validate(self.root)

    def test_missing_vendor_license_is_rejected(self) -> None:
        (self.root / "licenses/docker__skills.LICENSE").unlink()
        with self.assertRaisesRegex(ValueError, "Missing copied upstream license"):
            validate(self.root)

    def test_vendor_license_mismatch_is_rejected(self) -> None:
        (self.root / "licenses/hashicorp__agent-skills.LICENSE").write_text(
            "MIT License", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate(self.root)

    def test_angular_requires_per_skill_mit_declaration(self) -> None:
        path = self.root / "skills/test-skill-1/SKILL.md"
        path.write_text(path.read_text().replace("license: MIT\n", ""), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must declare MIT"):
            validate(self.root)

    def test_skill_relicensing_is_rejected(self) -> None:
        path = self.root / "skills/test-skill-2/SKILL.md"
        path.write_text(path.read_text().replace("license: Apache-2.0", "license: MIT"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from publisher"):
            validate(self.root)

    def test_changed_skill_without_lock_update_is_rejected(self) -> None:
        path = self.root / "skills/test-skill-0/SKILL.md"
        path.write_text(path.read_text() + "\nChanged\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed without updating the lock"):
            validate(self.root)

    def test_missing_third_party_notice_is_rejected(self) -> None:
        (self.root / "THIRD_PARTY_NOTICES.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing THIRD_PARTY"):
            validate(self.root)

    def test_source_license_policy_drift_is_rejected(self) -> None:
        self.manifest["sources"][2]["license"] = "MIT"
        self.lock["sources"][2]["license"] = "MIT"
        self.save()
        with self.assertRaisesRegex(ValueError, "license declaration differs"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
