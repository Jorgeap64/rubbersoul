#!/bin/bash

echo "Starting Python formatting with Black..."
uv run black .

echo "Running Ruff linting and auto-fix..."
uv run ruff check . --fix 

echo "Done! All Python files formatted and linted."
