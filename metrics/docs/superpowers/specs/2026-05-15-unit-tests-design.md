# Unit Tests Design — edfi_tech_metrics

Date: 2026-05-15

## Problem

The `metrics/` package has no unit tests. The `tests/` directory exists but
contains only an `__init__.py`. This design adds a focused first test suite
covering pure logic and data-transformation functions that require no mocking
of external services.

## Scope

**In scope:** `settings.py`, `improvements.py`, `ossf_score.py` (with a small
refactor to enable testability).

**Out of scope:** `jira.py` (requires Jira API mock), `ticket_age.py`
(requires plotnine rendering), `backlog.py` `get_portfolio_health()` (deferred
— uses module-level globals with an existing `# TODO: refactor` comment),
`run_backlog_health_ui()` (requires ipywidgets).

## Infrastructure

- Add `pytest` to `[tool.poetry.group.dev.dependencies]` in `pyproject.toml`.
- Tests live in the existing `tests/` directory.
- Three new test files: `tests/test_settings.py`, `tests/test_improvements.py`,
  `tests/test_ossf_score.py`.

## Refactor: `ossf_score.compare_with_previous_scores`

Add a `data_dir: str = "./data/ossf-scores/"` parameter. The default
preserves existing notebook call sites. Tests pass `tmp_path` instead.
This mirrors the existing pattern in `improvements.calculate_improvements`,
which already accepts `base_dir`.

## Test Cases

### `test_settings.py`

Tests `Configuration` logging methods using pytest's `capsys` fixture to
capture stdout. `termcolor` output wraps the message but still contains the
original string, so assertions check `message in captured.out`.

| Test | Behaviour verified |
|---|---|
| `info` at INFO level | message printed |
| `info` at DEBUG level | message printed |
| `info` at ERROR level | nothing printed |
| `debug` at DEBUG level | message printed |
| `debug` at INFO level | nothing printed |
| `error` at any level | message always printed |
| `load_configuration` with valid args list | returns correct `Configuration` fields |
| `load_configuration` with missing required arg | raises `SystemExit` |

### `test_improvements.py`

Tests `calculate_improvements(base_dir, projects)` using real CSV files
written to `tmp_path`. CSV format matches `_write_stats_file` output:
columns `project, count, mean, std, min, 25%, 50%, 75%, max, date`.

Note: the `projects` parameter is unused in the function body; tests pass an
empty list.

| Test | Behaviour verified |
|---|---|
| improvement | current mean < original → positive delta |
| regression | current mean > original → negative delta |
| no change | same mean both dates → delta = 0.0 |
| multiple projects | each project gets its own delta row |
| data spread across two CSV files | files concatenated correctly before analysis |

Delta formula: `(original_mean - current_mean) / original_mean`.

### `test_ossf_score.py`

Tests `compare_with_previous_scores(current_scores, data_dir)` using real CSV
files written to `tmp_path`. Previous CSV format: columns `Repository`, `Score`.

| Test | Behaviour verified |
|---|---|
| no previous files | message printed; returned df contains only current scores; both lists empty |
| one previous file | merged df has correct columns; score differences calculated |
| improved ≥ 10% | repo in `improved_repos` |
| worsened ≤ −10% | repo in `worsened_repos` |
| change < 10% | repo in neither list |
| repo only in current | appears in merged df with NaN previous score |
