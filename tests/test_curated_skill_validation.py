"""Regression checks for catalog-curated Agent Skills."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_curated_skills import blob_sha, validate_curated


class CuratedSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.name = "test-architecture-skill"
        folder = self.root / "skills" / self.name
        folder.mkdir(parents=True)
        skill_md = "---\nname: test-architecture-skill\nlicense: MIT\n---\n# Test\n"
        (folder / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (self.root / "licenses").mkdir()
        (self.root / "licenses" / "rodri-oliveira-dev__poc-arquitetura.LICENSE").write_text(
            "MIT License\nPermission is hereby granted\n", encoding="utf-8"
        )
        (self.root / "THIRD_PARTY_NOTICES.md").write_text(
            "rodri-oliveira-dev/poc-arquitetura", encoding="utf-8"
        )
        self.data = {
            "schema_version": 1,
            "skills": [{
                "id": self.name,
                "path": f"skills/{self.name}",
                "category": "architecture",
                "classification": "internal-adapted",
                "source_repository": "rodri-oliveira-dev/poc-arquitetura",
                "source_commit": "1" * 40,
                "source_skill_path": ".agents/skills/example/SKILL.md",
                "source_skill_blob_sha": "2" * 40,
                "source_license": "MIT",
                "catalog_license": "MIT",
                "license_review": "approved",
                "source_license_file": "licenses/rodri-oliveira-dev__poc-arquitetura.LICENSE",
                "upstream_attributions": [],
                "files_git_blob_sha1": {"SKILL.md": blob_sha(skill_md.encode())}
            }]
        }
        self.persist()

    def persist(self) -> None:
        (self.root / "catalog.curated.json").write_text(json.dumps(self.data), encoding="utf-8")

    def test_valid_skill(self) -> None:
        self.assertEqual(validate_curated(self.root), {self.name})

    def test_tampered_content(self) -> None:
        path = self.root / "skills" / self.name / "SKILL.md"
        path.write_text(path.read_text() + "\nInjected\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hashes differ"):
            validate_curated(self.root)

    def test_new_file_requires_catalog_update(self) -> None:
        (self.root / "skills" / self.name / "references.md").write_text("New\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hashes differ"):
            validate_curated(self.root)

    def test_missing_origin_commit(self) -> None:
        self.data["skills"][0]["source_commit"] = "main"
        self.persist()
        with self.assertRaisesRegex(ValueError, "immutable origin"):
            validate_curated(self.root)

    def test_cannot_silently_relicense(self) -> None:
        self.data["skills"][0]["catalog_license"] = "Apache-2.0"
        self.persist()
        with self.assertRaisesRegex(ValueError, "MIT license review"):
            validate_curated(self.root)

    def test_missing_source_attribution(self) -> None:
        (self.root / "THIRD_PARTY_NOTICES.md").write_text("empty", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing attribution"):
            validate_curated(self.root)

    def test_unlicensed_original_requires_pending_confirmation(self) -> None:
        entry = self.data["skills"][0]
        entry.update({
            "source_repository": "rodri-oliveira-dev/dotnet-copilot-code-review-skills",
            "source_license": "not-published-in-source-repository",
            "source_license_file": None,
            "license_review": "approved"
        })
        self.persist()
        with self.assertRaisesRegex(ValueError, "Unlicensed upstream"):
            validate_curated(self.root)

    def test_pending_confirmation_is_distinguished(self) -> None:
        entry = self.data["skills"][0]
        entry.update({
            "source_repository": "rodri-oliveira-dev/dotnet-copilot-code-review-skills",
            "source_license": "not-published-in-source-repository",
            "source_license_file": None,
            "license_review": "pending-maintainer-confirmation"
        })
        (self.root / "THIRD_PARTY_NOTICES.md").write_text(
            "rodri-oliveira-dev/dotnet-copilot-code-review-skills", encoding="utf-8"
        )
        self.persist()
        self.assertEqual(validate_curated(self.root), {self.name})

    def test_ddd_derivative_copyright_notice_required(self) -> None:
        entry = self.data["skills"][0]
        entry["upstream_attributions"] = ["ciembor/agent-rules-books"]
        self.persist()
        with self.assertRaisesRegex(ValueError, "Missing derivative source license"):
            validate_curated(self.root)

    def test_reject_duplicate_skills(self) -> None:
        self.data["skills"].append(dict(self.data["skills"][0]))
        self.persist()
        with self.assertRaisesRegex(ValueError, "duplicated curated"):
            validate_curated(self.root)


    def test_dotnet_library_template_is_validated_as_mit_source(self) -> None:
        entry = self.data["skills"][0]
        entry.update({
            "source_repository": "rodri-oliveira-dev/dotnet-library-template",
            "source_skill_path": ".agents/skills/dotnet-security-review/SKILL.md",
            "source_license_file": "licenses/rodri-oliveira-dev__dotnet-library-template.LICENSE",
        })
        (self.root / "licenses" / "rodri-oliveira-dev__dotnet-library-template.LICENSE").write_text(
            "MIT License\nPermission is hereby granted\n",
            encoding="utf-8",
        )
        (self.root / "THIRD_PARTY_NOTICES.md").write_text(
            "rodri-oliveira-dev/dotnet-library-template", encoding="utf-8"
        )
        self.persist()
        self.assertEqual(validate_curated(self.root), {self.name})

    def test_unreviewed_curated_source_is_rejected(self) -> None:
        self.data["skills"][0]["source_repository"] = "random-publisher/skills"
        self.persist()
        with self.assertRaisesRegex(ValueError, "Unreviewed curated source"):
            validate_curated(self.root)


if __name__ == "__main__":
    unittest.main()
