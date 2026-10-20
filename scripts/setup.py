"""Initialize project metadata once, then synchronize the project environment."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


RUNTIME_DEPENDENCIES = [
    "altair>=6.3.0",
    "click>=8.5.0",
    "duckdb>=1.5.5",
    "jinja2>=3.1.6",
    "pandas>=3.0.5",
    "pyarrow>=25.0.1",
    "scipy>=1.18.1",
    "snowflake-connector-python[secure-local-storage]>=4.7.5",
    "sqlparse>=0.6.0",
    "statsmodels>=0.15.0",
]
DEVELOPMENT_DEPENDENCIES = ["pytest>=9.1.1"]


def project_configuration(name: str, description: str) -> str:
    return (
        "[project]\n"
        f"name = {json.dumps(name)}\n"
        'version = "0.1.0"\n'
        f"description = {json.dumps(description, ensure_ascii=False)}\n"
        'readme = "README.md"\n'
        'requires-python = ">=3.12"\n'
        f"dependencies = {json.dumps(RUNTIME_DEPENDENCIES)}\n"
        "\n[dependency-groups]\n"
        f"dev = {json.dumps(DEVELOPMENT_DEPENDENCIES)}\n"
    )


def main() -> int:
    if shutil.which("uv") is None:
        print("Error: install uv from https://docs.astral.sh/uv/getting-started/installation/", file=sys.stderr)
        return 1

    configuration = Path("pyproject.toml")
    if not configuration.exists():
        default_name = Path.cwd().name
        try:
            while True:
                name = input(f"Project name [{default_name}]: ").strip() or default_name
                if re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?", name):
                    break
                print("Use letters, digits, dots, underscores, or hyphens; start and end with a letter or digit.")
            description = input("Description [Add your description here]: ").strip() or "Add your description here"
        except (EOFError, KeyboardInterrupt):
            print("\nSetup cancelled; no project configuration was written.", file=sys.stderr)
            return 1

        configuration.write_text(project_configuration(name, description), encoding="utf-8")

    try:
        subprocess.run(["uv", "sync", "--python", "3.12", "--group", "dev"], check=True)
    except subprocess.CalledProcessError as error:
        print("Dependency synchronization failed; version constraints were preserved. Resolve the error above and rerun make setup.", file=sys.stderr)
        return error.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
