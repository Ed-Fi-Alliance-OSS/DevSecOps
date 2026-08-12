# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from edfi_repo_auditor.job_metrics import (
    JOB_FAILURE_RATE_KEY,
    TOTAL_WORKFLOW_RUNS_KEY,
    get_job_failure_metrics,
)

_now = datetime.now(timezone.utc)

RECENT_CREATED_AT = (_now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD_CREATED_AT = (_now - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
JUST_PAST_BOUNDARY_CREATED_AT = (_now - timedelta(days=30, hours=1)).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)


def _run(name: str, conclusion: str, created_at: str) -> dict:
    return {"name": name, "conclusion": conclusion, "created_at": created_at}


def describe_get_job_failure_metrics() -> None:
    def describe_given_no_runs() -> None:
        def it_returns_none_rate_and_zero_total() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = []

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[JOB_FAILURE_RATE_KEY] is None
            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_runs_older_than_30_days() -> None:
        def it_excludes_them_from_metrics() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = [
                _run("CI", "failure", OLD_CREATED_AT),
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_recent_runs() -> None:
        def it_includes_them_in_metrics() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = [
                _run("CI", "success", RECENT_CREATED_AT),
                _run("CI", "failure", RECENT_CREATED_AT),
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 2
            assert result[JOB_FAILURE_RATE_KEY] == 50.0
            client.get_workflow_runs.assert_called_once_with(
                "owner", "repo", since_days=30
            )

    def describe_given_run_with_missing_created_at() -> None:
        def it_excludes_it_from_metrics() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = [
                {"name": "CI", "conclusion": "failure", "created_at": None},
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_run_with_malformed_created_at() -> None:
        def it_excludes_it_from_metrics() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = [
                {"name": "CI", "conclusion": "failure", "created_at": "not-a-date"},
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0

    def describe_given_run_with_a_non_z_iso_offset() -> None:
        def it_includes_it_in_metrics() -> None:
            client = MagicMock()
            recent_with_offset = (_now - timedelta(days=5)).strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )
            client.get_workflow_runs.return_value = [
                _run("CI", "failure", recent_with_offset),
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 1

    def describe_given_a_run_just_past_the_30_day_boundary() -> None:
        def it_excludes_it_from_metrics() -> None:
            client = MagicMock()
            client.get_workflow_runs.return_value = [
                _run("CI", "failure", JUST_PAST_BOUNDARY_CREATED_AT),
            ]

            result = get_job_failure_metrics(client, "owner", "repo")

            assert result[TOTAL_WORKFLOW_RUNS_KEY] == 0
