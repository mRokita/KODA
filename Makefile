.PHONY: format
format:
	poetry run isort playlists_api/ tests/
	poetry run black .

.PHONY: install
install:
	poetry install

.PHONY: lint
lint:
	-poetry run mypy --config-file pyproject.toml ${PWD}/koda
	-poetry run flake8 ${PWD}/koda

.PHONY: test
test:
	poetry run pytest --cov=./koda -vvv

.PHONY: docs_pdf
docs_pdf:
	 pandoc documentation.md -o documentation.pdf --template template.tex