# Ed-Fi Repository Auditor — Product Requirements Document

## Problem Statement

Ed-Fi Alliance repositories are distributed across three GitHub organizations (`Ed-Fi-Alliance-OSS`, `Ed-Fi-Closed`, and `Ed-Fi-Exchange-OSS`). Without automated tooling, verifying that each repository adheres to Ed-Fi governance standards — correct branch protection rules, required standard files, approved CI/CD pipelines, security scanning, and healthy pull-request practices — requires time-consuming manual inspection. Gaps go undetected until they become compliance or security problems.

## Solution

The `edfi-repo-auditor` is a Python CLI tool that programmatically audits one or more GitHub repositories against a defined checklist of governance rules. It fetches repository metadata, workflow files, branch-ruleset configuration, Dependabot alerts, OSSF Scorecard data, and recent pull-request history via the GitHub REST and GraphQL APIs. Results are written to a GitHub Actions job summary (markdown table) and optionally to a CSV file for trending and bulk review.

## User Stories

1. As an Ed-Fi governance engineer, I want to run an audit of a single repository from the GitHub Actions UI, so that I can quickly verify compliance without setting up a local environment.
2. As an Ed-Fi governance engineer, I want to audit all repositories in an organization in a single workflow run, so that I can produce a comprehensive compliance snapshot.
3. As an Ed-Fi governance engineer, I want audit results saved to a CSV file, so that I can track compliance trends over time.
4. As an Ed-Fi governance engineer, I want the tool to check whether a repository uses at least one GitHub Actions workflow, so that I can identify repos that have no CI/CD at all.
5. As an Ed-Fi governance engineer, I want the tool to verify that workflows reference the approved Ed-Fi repository scanner action, so that security scanning is standardized across all repos.
6. As an Ed-Fi governance engineer, I want the tool to check for CodeQL integration, so that I can ensure static analysis is running on each repo.
7. As an Ed-Fi governance engineer, I want the tool to verify that a test-reporter action (dorny/test-reporter or EnricoMi/publish-unit-test-result-action) is present, so that unit test results are surfaced in pull requests.
8. As an Ed-Fi governance engineer, I want the tool to detect the presence of a unit-test workflow by name, so that I can confirm automated testing exists.
9. As an Ed-Fi governance engineer, I want the tool to verify that the main branch requires a pull request before merging, so that direct pushes are prevented.
10. As an Ed-Fi governance engineer, I want the tool to confirm that admins cannot bypass branch-protection rules, so that governance applies equally to all contributors.
11. As an Ed-Fi governance engineer, I want the tool to check that branch creation is restricted, so that arbitrary branches cannot be created without approval.
12. As an Ed-Fi governance engineer, I want the tool to check that branch deletion is restricted, so that the main branch cannot be accidentally deleted.
13. As an Ed-Fi governance engineer, I want the tool to verify that a linear-history policy is enforced, so that merge commits are prohibited and history stays clean.
14. As an Ed-Fi governance engineer, I want the tool to check that the repository wiki is disabled, so that documentation lives in the approved locations.
15. As an Ed-Fi governance engineer, I want the tool to confirm that GitHub Issues are enabled, so that contributors have a standard way to report bugs and request features.
16. As an Ed-Fi governance engineer, I want the tool to check that GitHub Projects are disabled, so that project tracking happens in the approved tools.
17. As an Ed-Fi governance engineer, I want the tool to verify that the "delete head branch on merge" setting is enabled, so that stale branches are cleaned up automatically.
18. As an Ed-Fi governance engineer, I want the tool to verify that squash merge is the default, so that commit history stays clean.
19. As an Ed-Fi governance engineer, I want the tool to check that repository license information is configured in GitHub settings, so that the license is machine-readable.
20. As an Ed-Fi governance engineer, I want the tool to verify that Dependabot is enabled, so that dependency vulnerabilities are automatically surfaced.
21. As an Ed-Fi governance engineer, I want the tool to flag critical and high Dependabot alerts that have been open for more than three weeks, so that unresolved security issues are visible.
22. As an Ed-Fi governance engineer, I want the tool to report the OSSF Scorecard score for each repository, so that I have an independent supply-chain security signal.
23. As an Ed-Fi governance engineer, I want the tool to check for a NOTICES.md file, so that attribution obligations are documented.
24. As an Ed-Fi governance engineer, I want the tool to check for a CODE_OF_CONDUCT.md file, so that community expectations are explicit.
25. As an Ed-Fi governance engineer, I want the tool to check for a LICENSE file, so that the open-source license is present and discoverable.
26. As an Ed-Fi governance engineer, I want the tool to check for a CONTRIBUTORS.md file, so that contributor expectations are documented.
27. As an Ed-Fi governance engineer, I want the tool to check for a SECURITY.md file, so that the vulnerability disclosure process is documented.
28. As an Ed-Fi governance engineer, I want the tool to check for an AGENTS.md file, so that AI agent instructions are documented.
29. As an Ed-Fi engineering manager, I want the tool to report the number of pull requests merged in the last 30 days, so that I can gauge repository activity.
30. As an Ed-Fi engineering manager, I want the tool to report average PR duration (creation to close), so that I can monitor development velocity trends.
31. As an Ed-Fi engineering manager, I want the tool to report average lead time (creation to merge), so that I have a DORA-aligned change-delivery metric.
32. As an Ed-Fi engineering manager, I want the tool to report average time to first approval, so that I can identify review bottlenecks.
33. As an Ed-Fi engineering manager, I want the tool to report average number of reviews and approvals per PR, so that I can assess review thoroughness.
34. As an Ed-Fi engineering manager, I want the tool to report the share of reviews performed by the single most-active reviewer, so that I can detect unhealthy reviewer concentration.
35. As an Ed-Fi engineering manager, I want the tool to report total and unique reviewer counts, so that I can understand the breadth of code-review participation.
36. As a developer running the tool locally, I want to provide credentials and target configuration via environment variables, so that I do not need to repeat command-line arguments.
37. As a developer running the tool locally, I want to disable SSL certificate verification for outbound requests, so that the tool works in environments with SSL inspection proxies.
38. As a CI/CD pipeline operator, I want the audit summary written to the GitHub Actions job summary, so that results are visible directly in the workflow run UI.
39. As a CI/CD pipeline operator, I want a non-zero exit code when a fatal error occurs, so that the workflow is marked failed and does not silently swallow errors.

## Implementation Decisions

### Module Responsibilities

- **`config.py`** — Parses and validates CLI arguments and environment variables (all prefixed `AUDIT_`). Produces a `Configuration` dataclass consumed by the rest of the application.
- **`github_client.py`** — Thin wrapper around the GitHub REST and GraphQL APIs. Handles authentication, error translation, GraphQL variable injection, and REST pagination. Branch-protection data is read from GraphQL *rulesets* (not the deprecated REST branch-protection endpoint).
- **`auditor.py`** — Orchestration layer: calls all audit functions, merges their result dicts, invokes output helpers. Contains `audit_actions()`, `get_repo_information()`, `audit_alerts()`, `review_files()`, and `output_to_github_actions()`.
- **`pr_metrics.py`** — Standalone module that computes all PR-related metrics. Receives pre-fetched PR data and returns plain dicts. Currently all metrics are informational (no pass/fail threshold).
- **`ossf_score.py`** — Fetches the OpenSSF Scorecard score via the shields.io SVG badge endpoint, parses the score from the SVG `<title>` element using a regular expression.
- **`checklist.py`** — Single source of truth for check names and failure messages, implemented as a named-tuple of dicts.
- **`disable_tls.py`** — Context manager that monkey-patches `requests.Session` to skip TLS verification for all outbound calls within the block.
- **`__main__.py`** — Entry point: loads config, configures logging, wraps `run_audit()` in the TLS-bypass context if `--no_verify_ssl` is set.

### Key API Choices

- Repository metadata and branch rulesets: GraphQL (single round-trip, supports pagination).
- Workflow file listing and content: REST (`/repos/{owner}/{repo}/actions/workflows` and `/repos/{owner}/{repo}/contents/{path}`).
- Dependabot alerts: GraphQL (included in the repository information query).
- Pull requests and reviews: GraphQL (`PULL_REQUESTS_WITH_REVIEWS_TEMPLATE`) — single paginated query that fetches PRs and their embedded reviews in one call.
- OSSF score: shields.io SVG badge (`img.shields.io/ossf-scorecard/github.com/{org}/{repo}`).

### Pagination Boundaries

- Repositories per organization: up to 100 (no cursor pagination yet; a warning is logged if the count exceeds 100).
- Vulnerability alerts per repository: up to 100 (same limitation).
- Pull requests with reviews: fully paginated with cursor; pagination exits early when the oldest PR on a page predates a 3× lookback window (default: 90 days back when `since_days=30`).

### Output

- **GitHub Actions job summary**: markdown table written to `$GITHUB_STEP_SUMMARY`; also logged at INFO level.
- **CSV**: written to `reports/` directory when `--save_results` is set.
- **No HTML report**: previously existed; removed in favour of the GH Actions summary.

### Scoring

- `scoring.json` defines point values per checklist item and a passing threshold (currently 15 pts). This file is present in the repository but is **not yet wired into the runtime output**.

## Testing Decisions

### Good Test Principles

- Tests exercise public interfaces and observable outputs, not internal implementation details.
- GitHub API calls are mocked at the HTTP layer using `requests-mock`; no live network calls.
- Tests are organized with `pytest-describe` BDD blocks (`describe_` / `it_` / `given_`) for readability.

### Test Coverage by Module

- **`config.py`**: covered by `tests/test_config.py` — validates all CLI flags and environment-variable equivalents.
- **`github_client.py`**: covered by `tests/github_client/` — one test file per public method, mocking HTTP responses.
- **`auditor.py`** audit functions: covered by `tests/auditor/` — one file per function (`test_audit_actions.py`, `test_audit_alerts.py`, `test_get_repo_information.py`, `test_review_files.py`).
- **`ossf_score.py`**: covered by `tests/auditor/test_ossf_score.py` — tests for valid response, missing title, HTTP 404, HTTP 500.
- **`pr_metrics.py`**: covered by `tests/pr_metrics/` — separate files for duration, review cycle, reviewer load balance, and the top-level `get_pr_metrics()` aggregator.

## Out of Scope

- **Scoring/thresholds for PR metrics**: all PR metrics are currently informational only; no pass/fail evaluation is performed.
- **Repository pagination beyond 100**: organizations with more than 100 repositories will produce an incomplete audit and a log warning.
- **Vulnerability-alert pagination beyond 100**: repositories with more than 100 open vulnerability alerts may produce incomplete results.
- **CI health per PR** (pass rate, rerun count, average duration): not implemented.
- **PR size indicators** (median additions/deletions/changed files): not implemented.
- **Time-to-first-response** (first comment or review from non-author): not implemented.
- **Security posture per PR** (PRs touching sensitive files, CodeQL-flagged PRs): not implemented.
- **HTML report**: removed in an earlier refactor; not restored.
- **Rate-limit handling**: the tool assumes the provided token has sufficient API quota.

## Further Notes

- The tool is intended to be run from GitHub Actions using the `Run Single Audit` or `Run Full Audit` workflows defined in `.github/workflows/`.
- Repository names passed via `--repositories` / `AUDIT_REPOSITORIES` are case-sensitive; incorrect casing will cause the OSSF score fetch to fail silently (shields.io returns a non-numeric badge title).
- Required GitHub token scopes: `repo` (read repositories and file contents) and `read:org` (enumerate organization repositories).
- The `scoring.json` file is a future extension point; once PR-metric thresholds are agreed upon, the scoring engine can be re-enabled to provide a single pass/fail verdict per repository.
