#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the tests
pytest -v

# Generate coverage report if coverage is installed
if command -v pytest-cov &> /dev/null; then
    pytest --cov=backend --cov-report=term --cov-report=html
fi
