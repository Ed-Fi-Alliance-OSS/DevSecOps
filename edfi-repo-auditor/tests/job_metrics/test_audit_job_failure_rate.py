# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict, List

from edfi_repo_auditor.job_metrics import (
    JOB_FAILURE_RATE_KEY,
    TOTAL_WORKFLOW_RUNS_KEY,
    audit_job_failure_rate,
)


def _run(name: str, conclusion: str) -> Dict:
    return {"name": name, "conclusion": conclusion}


def describe_audit_job_failure_rate() -> None:
    def describe_given_no_runs() -> None:
        def it_returns_none_rate_and_zero_total() -> None:
            result = audit_job_failure_rate([])

            assert result[JOB_FAILURE_RATE_KEY] is None
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_only_excluded_conclusions() -> None:
        def it_returns_none_rate_and_zero_total() -> None:
            runs: List[Dict] = [
                _run("CI", "cancelled"),
                _run("CI", "skipped"),
                _run("CI", "neutral"),
            ]

            result = audit_job_failure_rate(runs)

            assert result[JOB_FAILURE_RATE_KEY] is None
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_mixed_success_and_failure_runs() -> None:
        def it_computes_overall_failure_rate() -> None:
            runs: List[Dict] = [
                _run("CI", "success"),
                _run("CI", "success"),
                _run("CI", "failure"),
                _run("CI", "success"),
            ]

            result = audit_job_failure_rate(runs)

            assert result[JOB_FAILURE_RATE_KEY] == 25.0
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 4

        def it_excludes_cancelled_skipped_and_neutral_from_denominator() -> None:
            runs: List[Dict] = [
                _run("CI", "success"),
                _run("CI", "failure"),
                _run("CI", "cancelled"),
                _run("CI", "skipped"),
                _run("CI", "neutral"),
            ]

            result = audit_job_failure_rate(runs)

            assert result[JOB_FAILURE_RATE_KEY] == 50.0
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 2

    def describe_given_timed_out_action_required_and_startup_failure() -> None:
        def it_counts_them_as_failures() -> None:
            runs: List[Dict] = [
                _run("CI", "success"),
                _run("CI", "timed_out"),
                _run("CI", "action_required"),
                _run("CI", "startup_failure"),
            ]

            result = audit_job_failure_rate(runs)

            assert result[JOB_FAILURE_RATE_KEY] == 75.0
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 4

    def describe_given_multiple_workflows() -> None:
        def it_computes_a_separate_rate_per_workflow() -> None:
            runs: List[Dict] = [
                _run("CI", "success"),
                _run("CI", "failure"),
                _run("CodeQL", "success"),
                _run("CodeQL", "success"),
            ]

            result = audit_job_failure_rate(runs)

            assert result["Job Failure Rate - CI (%)"] == 50.0
            assert result["Job Failure Rate - CodeQL (%)"] == 0.0
            assert result[JOB_FAILURE_RATE_KEY] == 25.0

    def describe_given_run_with_missing_name() -> None:
        def it_groups_under_unknown() -> None:
            runs: List[Dict] = [
                {"conclusion": "failure"},
                {"conclusion": "success"},
            ]

            result = audit_job_failure_rate(runs)

            assert result["Job Failure Rate - Unknown (%)"] == 50.0
