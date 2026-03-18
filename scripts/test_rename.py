"""Tests for the rename/rebrand script."""

import shutil
import tempfile
import unittest
from pathlib import Path

# We'll import from rename module once it exists
# For now, tests will fail (RED phase)


class TestPluralDerivation(unittest.TestCase):
    """Test singular-to-plural derivation logic."""

    def test_default_plural_adds_s(self):
        from rename import derive_plural

        self.assertEqual(derive_plural("item"), "items")

    def test_default_plural_for_project(self):
        from rename import derive_plural

        self.assertEqual(derive_plural("project"), "projects")

    def test_default_plural_for_widget(self):
        from rename import derive_plural

        self.assertEqual(derive_plural("widget"), "widgets")

    def test_custom_plural_override(self):
        """When user provides explicit plural, use it."""
        from rename import derive_plural

        self.assertEqual(derive_plural("person", override="people"), "people")

    def test_override_none_falls_back_to_default(self):
        from rename import derive_plural

        self.assertEqual(derive_plural("recipe", override=None), "recipes")


class TestCaseVariants(unittest.TestCase):
    """Test generation of all case variants for replacement."""

    def test_generates_lowercase(self):
        from rename import build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        # Should contain lowercase singular and plural
        self.assertIn(("item", "project"), replacements)
        self.assertIn(("items", "projects"), replacements)

    def test_generates_capitalized(self):
        from rename import build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        self.assertIn(("Item", "Project"), replacements)
        self.assertIn(("Items", "Projects"), replacements)

    def test_generates_uppercase(self):
        from rename import build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        self.assertIn(("ITEM", "PROJECT"), replacements)
        self.assertIn(("ITEMS", "PROJECTS"), replacements)

    def test_plural_replaced_before_singular(self):
        """Plural replacements must come first to avoid partial matches."""
        from rename import build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        plural_indices = [
            i for i, (old, _) in enumerate(replacements) if old in ("items", "Items", "ITEMS")
        ]
        singular_indices = [
            i for i, (old, _) in enumerate(replacements) if old in ("item", "Item", "ITEM")
        ]
        # All plural replacements should come before singular
        self.assertTrue(max(plural_indices) < min(singular_indices))


class TestContentReplacement(unittest.TestCase):
    """Test content replacement in file text."""

    def test_replaces_class_names(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = "class Item:\n    pass\n\nclass ItemResponse:\n    pass"
        result = apply_replacements(content, replacements)
        self.assertIn("class Project:", result)
        self.assertIn("class ProjectResponse:", result)
        self.assertNotIn("Item", result)

    def test_replaces_variable_names(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = "item = get_item(item_id)\nitems = list_items()"
        result = apply_replacements(content, replacements)
        self.assertIn("project = get_project(project_id)", result)
        self.assertIn("projects = list_projects()", result)

    def test_replaces_route_prefixes(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = 'prefix="/items"'
        result = apply_replacements(content, replacements)
        self.assertEqual(result, 'prefix="/projects"')

    def test_replaces_import_paths(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = "from app.items.models import Item"
        result = apply_replacements(content, replacements)
        self.assertEqual(result, "from app.projects.models import Project")

    def test_replaces_uppercase(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = 'ITEM_TABLE = "items"'
        result = apply_replacements(content, replacements)
        self.assertEqual(result, 'PROJECT_TABLE = "projects"')

    def test_no_false_positives_on_unrelated_text(self):
        from rename import apply_replacements, build_replacements

        replacements = build_replacements("item", "items", "project", "projects")
        content = "from fastapi import FastAPI"
        result = apply_replacements(content, replacements)
        self.assertEqual(result, content)


class TestDryRun(unittest.TestCase):
    """Test dry-run mode with a temporary directory."""

    def setUp(self):
        """Create a temp project structure mimicking DualStack."""
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)

        # Create directory structure
        dirs = [
            "backend/app/items",
            "backend/tests/items",
            "frontend/src/components/items",
            "frontend/src/app/(dashboard)/items",
        ]
        for d in dirs:
            (self.root / d).mkdir(parents=True, exist_ok=True)

        # Create sample files
        (self.root / "backend/app/items/models.py").write_text(
            'class Item:\n    __tablename__ = "items"\n'
        )
        (self.root / "backend/app/items/service.py").write_text(
            "def create_item(item):\n    pass\n\ndef get_items():\n    pass\n"
        )
        (self.root / "backend/app/items/routes.py").write_text(
            'from app.items.service import create_item\nprefix="/items"\n'
        )
        (self.root / "backend/app/items/__init__.py").write_text("")
        (self.root / "backend/tests/items/test_service.py").write_text(
            "def test_create_item():\n    pass\n"
        )
        (self.root / "backend/tests/items/__init__.py").write_text("")
        (self.root / "frontend/src/components/items/item-card.tsx").write_text(
            "export function ItemCard() { return <div>Item</div> }\n"
        )
        (self.root / "frontend/src/app/(dashboard)/items/page.tsx").write_text(
            "export default function ItemsPage() { return <div>Items</div> }\n"
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_dry_run_does_not_modify_files(self):
        from rename import run_rename

        original_content = (self.root / "backend/app/items/models.py").read_text()
        run_rename("item", "items", "project", "projects", dry_run=True, root=self.root)

        # File content should be unchanged
        self.assertEqual(
            (self.root / "backend/app/items/models.py").read_text(),
            original_content,
        )
        # Directory should still exist with old name
        self.assertTrue((self.root / "backend/app/items").exists())

    def test_dry_run_returns_correct_stats(self):
        from rename import run_rename

        stats = run_rename("item", "items", "project", "projects", dry_run=True, root=self.root)
        self.assertEqual(stats["dirs_renamed"], 4)
        self.assertGreater(stats["files_renamed"], 0)
        self.assertGreater(stats["files_modified"], 0)
        self.assertGreater(stats["replacements_made"], 0)

    def test_actual_rename_modifies_directories(self):
        from rename import run_rename

        run_rename("item", "items", "project", "projects", dry_run=False, root=self.root)
        # Old dirs should be gone
        self.assertFalse((self.root / "backend/app/items").exists())
        # New dirs should exist
        self.assertTrue((self.root / "backend/app/projects").exists())
        self.assertTrue((self.root / "backend/tests/projects").exists())

    def test_actual_rename_modifies_content(self):
        from rename import run_rename

        run_rename("item", "items", "project", "projects", dry_run=False, root=self.root)
        content = (self.root / "backend/app/projects/models.py").read_text()
        self.assertIn("class Project:", content)
        self.assertIn('"projects"', content)
        self.assertNotIn("Item", content)
        self.assertNotIn("items", content)

    def test_actual_rename_renames_files(self):
        from rename import run_rename

        run_rename("item", "items", "project", "projects", dry_run=False, root=self.root)
        # item-card.tsx should become project-card.tsx
        self.assertTrue(
            (self.root / "frontend/src/components/projects/project-card.tsx").exists()
        )
        self.assertFalse(
            (self.root / "frontend/src/components/projects/item-card.tsx").exists()
        )

    def test_actual_rename_returns_stats(self):
        from rename import run_rename

        stats = run_rename("item", "items", "project", "projects", dry_run=False, root=self.root)
        self.assertEqual(stats["dirs_renamed"], 4)
        self.assertGreater(stats["files_renamed"], 0)
        self.assertGreater(stats["files_modified"], 0)


class TestArgParsing(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_basic_args(self):
        from rename import parse_args

        args = parse_args(["--from", "item", "--to", "project"])
        self.assertEqual(args.from_singular, "item")
        self.assertEqual(args.to_singular, "project")
        self.assertFalse(args.dry_run)

    def test_dry_run_flag(self):
        from rename import parse_args

        args = parse_args(["--from", "item", "--to", "project", "--dry-run"])
        self.assertTrue(args.dry_run)

    def test_custom_plural_args(self):
        from rename import parse_args

        args = parse_args([
            "--from", "person", "--to", "child",
            "--from-plural", "people", "--to-plural", "children",
        ])
        self.assertEqual(args.from_plural, "people")
        self.assertEqual(args.to_plural, "children")

    def test_missing_required_args_raises(self):
        from rename import parse_args

        with self.assertRaises(SystemExit):
            parse_args(["--from", "item"])


if __name__ == "__main__":
    unittest.main()
