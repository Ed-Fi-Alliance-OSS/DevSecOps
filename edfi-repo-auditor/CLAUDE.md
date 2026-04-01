# CLAUDE.md

## Project Overview

`edfi-repo-auditor` is a Python CLI tool that audits GitHub repositories for compliance with Ed-Fi organization governance standards. It evaluates repositories across GitHub Actions setup, security configurations, branch protection, repository settings, and pull request metrics, outputting results as CSV and/or GitHub Actions job summaries.

## Commands

```bash
# Install dependencies
poetry install

# Run the auditor
poetry run python edfi_repo_auditor -o <org> -p <token> [-r repo1 repo2]

# Tests, formatting, linting, type-checking
poetry run pytest
poetry run pytest tests/auditor/          # single module
poetry run pytest tests/test_foo.py::describe_bar  # single describe block
poetry run black .
poetry run flake8
poetry run mypy .
```

## Architecture

Data flows: `config.py` → `github_client.py` → `auditor.py` → CSV / GitHub Actions summary

- **`config.py`**: Parses CLI args and environment variables (all prefixed `AUDIT_`). Single source of configuration validation.
- **`github_client.py`**: REST and GraphQL wrapper for GitHub API. Branch protection rules use GraphQL rulesets (not the legacy REST branch protection API).
- **`auditor.py`**: Orchestrates all audit functions — `audit_actions()`, `audit_alerts()`, `get_repo_information()`, `review_files()`, `get_pr_metrics()` — then writes output.
- **`checklist.py`**: Named tuples defining each compliance rule with its description and failure message.
- **`pr_metrics.py`**: Computes PR duration, lead time, review cycles, and reviewer balance. Currently informational only (no pass/fail thresholds).
- **`ossf_score.py`**: Fetches OpenSSF Scorecard value from a shields.io SVG badge.
- **`scoring.json`**: Defines point values per checklist item and a passing threshold (15 pts). Not yet wired into runtime output.

## Test Conventions

Tests use `pytest-describe` (BDD-style `describe_`/`it_` blocks) and `pytest-mock`. GitHub API responses are mocked with `requests-mock`. See `tests/github_client/` for examples of REST mocking and `tests/auditor/` for orchestration-level tests.

## Key Constraints

- **GraphQL pagination**: Repository and alert queries are limited to 100 results — cursor-based pagination is not yet implemented.
- **API rate limits**: No built-in handling; the tool assumes a token with sufficient quota.
- **Required token scopes**: `repo` (read repos) and `read:org` (read org metadata).
- **Line length**: 110 characters (`.flake8`).

## Adding a New Audit Check

1. Add a named tuple entry to `CHECKLIST` in `checklist.py` with description and failure message.
2. Implement the logic in `auditor.py` (or a new module imported there).
3. Add tests in `tests/auditor/`.
4. Update `scoring.json` with point value if applicable.
