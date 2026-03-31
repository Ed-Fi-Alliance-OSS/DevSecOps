Thanks — here’s the updated, concrete plan incorporating your preferences.

## Plan: PR Duration & Manager Metrics

Compute average PR duration for merged PRs only, with full pagination and no date filters. Extend reporting to include leadership metrics: lead time, review cycle, PR size, reviewer balance, time-to-first-response, CI health, and security posture — aligned with current client and auditor patterns.

### Steps
1. Add `get_pull_requests(owner, repo, state='closed', per_page=100)` with pagination in `edfi_repo_auditor/github_client.py` to collect `created_at`, `closed_at`, `merged_at`, `number`, `user`, `requested_reviewers`, `reviews`, `comments`, `additions`, `deletions`, `changed_files`.
2. Implement `audit_pr_duration(owner, repo, client)` in `edfi_repo_auditor/auditor.py` to compute average `(closed_at - created_at)` for PRs with `merged_at != None`; output `avg_pr_duration_days`, `merged_pr_count`.
3. Add `audit_lead_time_for_change(owner, repo, client)` in `auditor.py` to compute average `(merged_at - created_at)` for merged PRs as a proxy.
4. Add `audit_pr_review_cycle(owner, repo, client)` in `auditor.py` to compute average time from open to first approval, number of reviews per PR, approvals per PR.
5. Add `audit_pr_size_indicators(owner, repo, client)` in `auditor.py` to compute medians/averages for `additions`, `deletions`, `changed_files`; correlate size with merge duration.
6. Add `audit_reviewer_load_balance(owner, repo, client)` in `auditor.py` to aggregate reviews per reviewer and compute Gini/coefficient or top-percent share.
7. Add `audit_time_to_first_response(owner, repo, client)` in `auditor.py` to compute average latency from open to first comment or review.
8. Add `audit_ci_health_per_pr(owner, repo, client)` in `auditor.py` using existing Actions APIs to map workflows to PRs and compute pass rate, rerun count, average duration.
9. Add `audit_security_posture(owner, repo, client)` in `auditor.py` to tag PRs touching sensitive files (heuristics or CodeQL alerts) and summarize counts; reuse existing dependabot/code scanning where possible.
10. Extend aggregation in `auditor.py` to include all metrics in JSON/CSV; avoid modifying scoring in `checklist.py` unless later requested.
11. Optionally enhance `edfi_repo_auditor/html_report.py` to render an “Metrics” section showing informational values (averages, counts) per repo.

### Further Considerations
1. Data sources: Prefer REST for PRs/reviews; optionally supplement with GraphQL for richer review timing if needed.
2. Mapping CI-to-PR: Use commit SHA association or workflow run `pull_requests` context; fall back to branch name heuristics if necessary.
3. Performance: Paginate thoroughly; batch requests; consider rate-limit handling and caching patterns consistent with `github_client.py`.

## Acceptance Criteria Checklist
### Must
- **Merged-only PRs:** Average duration includes only PRs with `merged_at` set; non-merged/closed PRs are excluded.
- **No date filter:** Metric computed across all available merged PRs without time-window filters.
- **Pagination:** `get_pull_requests` paginates through all pages until exhaustion; no silent truncation.
- **Core fields collected:** Each PR record includes `number`, `created_at`, `closed_at`, `merged_at`, `user`, `additions`, `deletions`, `changed_files`.
- **Duration metric output:** JSON/CSV include `avg_pr_duration_days` and `merged_pr_count` per repository.
- **Lead time metric:** JSON/CSV include `avg_lead_time_days` computed from `created_at` to `merged_at`.
- **Tests (core):** Unit tests cover pagination, merged-only filtering, empty datasets, missing timestamps, and aggregation correctness for duration and lead time.

### Nice-to-have
- **Review cycle metrics:** JSON/CSV include `avg_time_to_first_approval`, `avg_reviews_per_pr`, `avg_approvals_per_pr`.
- **PR size indicators:** JSON/CSV include `median_additions`, `median_deletions`, `median_changed_files`, plus `avg_*` counterparts.
- **Reviewer load balance:** JSON/CSV include `top_reviewer_share_percent` (or similar) derived from review counts per reviewer.
- **Time-to-first-response:** JSON/CSV include `avg_time_to_first_response_hours` (first comment or review from someone other than author).
- **CI health per PR:** JSON/CSV include `ci_pass_rate_percent`, `avg_ci_duration_minutes`, `avg_ci_reruns_per_pr`.
- **Security posture:** JSON/CSV include `prs_flagged_security_count` and `prs_flagged_security_percent` using available signals (CodeQL/Dependabot heuristics).
- **HTML report:** Includes a “Metrics” section per repo showing the above values.
- **Tests (extended):** Unit tests validate calculations for review cycle, size indicators, reviewer balance, first response, CI health, and security posture.
