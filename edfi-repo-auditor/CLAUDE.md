# CLAUDE.md

## Architecture

Data flows: `config.py` → `github_client.py` → `auditor.py` → CSV / GitHub Actions summary

- **`github_client.py`**: Branch protection rules use GraphQL *rulesets*, not the legacy REST branch-protection API.
- **`pr_metrics.py`**: All PR metrics are informational only — no pass/fail thresholds.
- **`ossf_score.py`**: Fetches the OSSF Scorecard score by parsing the score out of a shields.io SVG badge `<title>`.
- **`scoring.json`**: Defines point values per checklist item. **Not yet wired into runtime output.**

## Test Conventions

Tests use `pytest-describe` (BDD-style `describe_`/`it_` blocks) and `pytest-mock`. GitHub API responses are mocked with `requests-mock`. See `tests/github_client/` for REST mocking examples.

## Key Constraints

- **GraphQL pagination**: Repository and alert queries cap at 100 results — cursor-based pagination is not yet implemented for those queries.
- **Line length**: 110 characters (`.flake8`), overriding the common default.

## Adding a New Audit Check

1. Add a named tuple entry to `CHECKLIST` in `checklist.py` with `description` and `fail` message.
2. Implement the logic in `auditor.py` (or a new module imported there).
3. Add tests in `tests/auditor/`.
4. Update `scoring.json` with a point value if applicable.
