# Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
make setup
```

On the first run, enter a project name and description, or press Enter to use
the repository folder name and `Add your description here`. Names must start
and end with a letter or digit and contain only letters, digits, `.`, `_`, or
`-`. Ctrl-C or end-of-input cancels without writing project configuration.

Setup creates `.venv` with Python 3.12 (uv may download Python), generates
`pyproject.toml`, and synchronizes runtime and development dependencies.
Subsequent runs preserve `pyproject.toml` and sync without prompting.
The initial runtime dependencies are defined in `scripts/setup.py`; the
development dependency group includes `pytest>=9.1.1`. After initialization, edit
`pyproject.toml` to change either list and rerun `make setup`.
An internet connection may be required to download Python and packages.
If dependency resolution fails, the requested constraints remain unchanged;
resolve the reported issue and rerun `make setup`.

Keep `pyproject.toml` and `uv.lock` in version control. Run Python commands
through `.venv/bin/python`.

To run the setup behavior checks after setup:

```sh
.venv/bin/python -m unittest discover -s tests
```
