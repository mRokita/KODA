# About

This is a project for the Data Compression course at Warsaw University of Technology.

# Installation & Usage

Python >= 3.9 & pip is required

We recommend using pipx [pipx](https://pypa.github.io/pipx/) to install the program as an executable isolated inside a dedicated Python virtual environment:

```
> python3 -m pip install pipx
> python3 -m pipx ensurepath
> pipx install koda_ac
> koda --help
Usage: koda [OPTIONS] COMMAND [ARGS]...
```

Alternatively, a standard `pip install` should work:

```
> python3 -m pip install koda_ac
> python3 -m koda_ac --help
Usage: python -m koda_ac [OPTIONS] COMMAND [ARGS]...
```

# Development setup

[Poetry](https://python-poetry.org) is used for dependency management, see https://python-poetry.org/docs/master/#installation for installation instructions.

After installing Poetry, use `poetry install` to install project dependencies.

## Makefile tasks

- use `make format` to format code with `black` and `isort`
- use `make lint` to lint code with `mypy` and `flake8`
- use `make test` to run tests in `tests/` with `pytest`