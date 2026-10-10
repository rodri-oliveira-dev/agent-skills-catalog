"""Regression coverage for official skill/license allowlist removals."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.sync_official_skills import reconcile_removed


class OfficialSyncReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        self.licenses = self.root / "licenses"
        self.skills.mkdir()
        self.licenses.mkdir()

    def reconcile(
        self,
        previous_lock: dict,
        desired: set[str],
        repositories: set[str],
        curated: set[str] | None = None,
        protected: set[str] | None = None,
    ) -> tuple[list[str], list[str]]:
        return reconcile_removed(
            previous_lock,
            desired,
            repositories,
            curated or set(),
            protected or set(),
            skills_dir=self.skills,
            licenses_dir=self.licenses,
        )

    def test_removed_or_renamed_skill_is_deleted(self) -> None:
        for name in ("old-skill", "kept-skill"):
            d = self.skills / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
        previous = {"skills": [{"name": "old-skill"}, {"name": "kept-skill"}]}
        removed, licenses = self.reconcile(previous, {"kept-skill"}, {"dotnet/skills"})
        self.assertEqual(removed, ["old-skill"])
        self.assertEqual(licenses, [])
        self.assertFalse((self.skills / "old-skill").exists())
        self.assertTrue((self.skills / "kept-skill/SKILL.md").is_file())

    def test_remove_retired_source_license_and_notice(self) -> None:
        for name in ("dotnet__skills.LICENSE", "dotnet__skills.NOTICE", "google__skills.LICENSE"):
            (self.licenses / name).write_text("license", encoding="utf-8")
        previous = {"sources": [
            {"repository": "dotnet/skills"}, {"repository": "google/skills"},
        ]}
        removed_skills, removed_licenses = self.reconcile(
            previous, set(), {"google/skills"}
        )
        self.assertEqual(removed_skills, [])
        self.assertEqual(
            set(removed_licenses), {"dotnet__skills.LICENSE", "dotnet__skills.NOTICE"}
        )
        self.assertTrue((self.licenses / "google__skills.LICENSE").exists())

    def test_curated_skill_and_legal_file_are_preserved(self) -> None:
        (self.skills / "shared-skill").mkdir()
        (self.skills / "shared-skill/SKILL.md").write_text("curated", encoding="utf-8")
        (self.licenses / "old__skills.LICENSE").write_text("shared", encoding="utf-8")
        previous = {
            "skills": [{"name": "shared-skill"}],
            "sources": [{"repository": "old/skills"}],
        }
        removed = self.reconcile(
            previous, set(), set(), {"shared-skill"}, {"old__skills.LICENSE"}
        )
        self.assertEqual(removed, ([], []))
        self.assertTrue((self.skills / "shared-skill/SKILL.md").is_file())
        self.assertTrue((self.licenses / "old__skills.LICENSE").is_file())

    def test_untracked_directory_is_never_deleted(self) -> None:
        (self.skills / "user-added").mkdir()
        (self.skills / "user-added/SKILL.md").write_text("custom", encoding="utf-8")
        self.reconcile({"skills": []}, set(), set())
        self.assertTrue((self.skills / "user-added/SKILL.md").is_file())

    def test_reject_path_traversal_from_previous_lock(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsafe name"):
            self.reconcile({"skills": [{"name": "../outside"}]}, set(), set())
        with self.assertRaisesRegex(ValueError, "Unsafe repository"):
            self.reconcile({"sources": [{"repository": "../outside"}]}, set(), set())

    def test_reject_symlinked_legacy_skill(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("preserve", encoding="utf-8")
        (self.skills / "old-skill").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinked skill"):
            self.reconcile({"skills": [{"name": "old-skill"}]}, set(), set())
        self.assertTrue((outside / "secret.txt").exists())


if __name__ == "__main__":
    unittest.main()
