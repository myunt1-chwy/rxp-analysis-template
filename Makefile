.DEFAULT_GOAL := setup

.PHONY: setup init bootstrap

bootstrap:
	@command -v uv >/dev/null 2>&1 || { echo 'Error: uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/ and rerun make setup.' >&2; exit 1; }
	@test -x .venv/bin/python || uv venv --python 3.12 .venv

setup: bootstrap
	@.venv/bin/python scripts/setup.py

init: bootstrap
	@if test -f pyproject.toml; then uv sync --python 3.12 --group dev; fi
	@.venv/bin/python scripts/setup.py --init
