#!/bin/bash
# Test runner script wrapper for FastAPI application
cd "$(dirname "$0")"
.venv/bin/python run_tests.py "$@"