
format:
    poetry run black .
    poetry run isort .
    poetry run ruff check --fix --exit-zero .

typecheck:
    poetry run pyright

check: format typecheck
