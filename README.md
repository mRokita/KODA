# Development setup

[Poetry](https://python-poetry.org) is used for dependency management, see https://python-poetry.org/docs/master/#installation for installation instructions.

After installing Poetry, use `poetry install` to install project dependencies.

## Makefile tasks

- use `make format` to format code with `black` and `isort`
- use `make lint` to lint code with `mypy` and `flake8`
- use `make test` to run tests in `tests/` with `pytest`