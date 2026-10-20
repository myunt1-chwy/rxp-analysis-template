import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("project_setup", Path(__file__).resolve().parents[1] / "scripts/setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="setup-test-")
        self.addCleanup(self.directory.cleanup)
        previous = Path.cwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, previous)
        self.addCleanup(patch.stopall)
        patch.object(setup.shutil, "which", return_value="uv").start()
        self.sync = patch.object(setup.subprocess, "run").start()
        patch("sys.stdout", new_callable=io.StringIO).start()
        patch("sys.stderr", new_callable=io.StringIO).start()

    def run_setup(self, answers):
        with patch("builtins.input", side_effect=answers):
            return setup.main()

    def configuration(self):
        return tomllib.loads(Path("pyproject.toml").read_text())

    def test_defaults(self):
        self.assertEqual(self.run_setup(["", ""]), 0)
        project = self.configuration()["project"]
        self.assertEqual(project["name"], Path.cwd().name)
        self.assertEqual(project["description"], "Add your description here")
        self.assertEqual(project["version"], "0.1.0")
        self.assertEqual(project["requires-python"], ">=3.12")
        self.assertEqual(project["readme"], "README.md")
        self.assertEqual(project["dependencies"], [
            "altair>=6.3.0",
            "click>=8.5.0",
            "duckdb>=1.5.5",
            "jinja2>=3.1.6",
            "pandas>=3.0.5",
            "pyarrow>=25.0.1",
            "pyyaml",
            "scipy>=1.18.1",
            "snowflake-connector-python[secure-local-storage]>=4.7.5",
            "sqlparse>=0.6.0",
            "statsmodels>=0.15.0",
        ])
        self.assertEqual(self.configuration()["dependency-groups"]["dev"], ["pytest>=9.1.1"])
        self.sync.assert_called_once_with(["uv", "sync", "--python", "3.12", "--group", "dev"], check=True)

    def test_custom_metadata_and_escaping(self):
        description = 'Quotes " and backslash \\ with café 🐾\t'
        self.assertEqual(self.run_setup(["my.project-1_x", description]), 0)
        project = self.configuration()["project"]
        self.assertEqual(project["name"], "my.project-1_x")
        self.assertEqual(project["description"], description.strip())

    def test_invalid_names_are_reprompted(self):
        self.assertEqual(self.run_setup(["bad name", "-bad", "bad/thing", "bad.", "valid", ""]), 0)
        self.assertEqual(self.configuration()["project"]["name"], "valid")

    def test_interrupted_prompts_do_not_write(self):
        for answers in ([EOFError], [KeyboardInterrupt], ["valid", EOFError], ["valid", KeyboardInterrupt]):
            with self.subTest(answers=answers):
                self.assertEqual(self.run_setup(answers), 1)
                self.assertFalse(Path("pyproject.toml").exists())
        self.sync.assert_not_called()

    def test_repeat_run_preserves_bytes_without_input(self):
        original = b'# custom metadata\n[project]\nname = "existing"\n'
        Path("pyproject.toml").write_bytes(original)
        self.assertEqual(self.run_setup([AssertionError("Must not prompt")]), 0)
        self.assertEqual(Path("pyproject.toml").read_bytes(), original)
        self.sync.assert_called_once()

    def test_sync_failure_preserves_configuration(self):
        self.run_setup(["valid", ""])
        original = Path("pyproject.toml").read_bytes()
        self.sync.side_effect = subprocess.CalledProcessError(1, "uv")
        self.assertEqual(self.run_setup([]), 1)
        self.assertEqual(Path("pyproject.toml").read_bytes(), original)

    def test_missing_uv_does_not_prompt_or_write(self):
        with patch.object(setup.shutil, "which", return_value=None):
            self.assertEqual(self.run_setup([]), 1)
        self.assertFalse(Path("pyproject.toml").exists())
        self.sync.assert_not_called()


if __name__ == "__main__":
    unittest.main()
