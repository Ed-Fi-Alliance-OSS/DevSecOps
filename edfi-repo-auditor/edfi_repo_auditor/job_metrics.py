# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
Job Failure Rate metrics module.

Computes the percentage of GitHub Actions workflow runs that concluded as a
failure over the last 30 days, both overall and broken out per workflow.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

from edfi_repo_auditor.github_client import GitHubClient

logger: logging.Logger = logging.getLogger(__name__)

LAST_N_DAYS = 30

# Conclusions that count as a failed run.
FAILURE_CONCLUSIONS = {"failure", "timed_out", "action_required", "startup_failure"}

# Conclusions that count as a successful run.
SUCCESS_CONCLUSIONS = {"success"}

JOB_FAILURE_RATE_KEY = "Job Failure Rate (%)"
TOTAL_WORKFLOW_RUNS_KEY = "Total Workflow Runs (last 30 days)"


def _job_failure_rate_key(workflow_name: str) -> str:
    return f"Job Failure Rate - {workflow_name} (%)"


def audit_job_failure_rate(runs: List[Dict]) -> Dict[str, object]:
    """
    Compute the Job Failure Rate, overall and per workflow.

    Only runs with conclusion in FAILURE_CONCLUSIONS or SUCCESS_CONCLUSIONS
    are counted; runs with conclusion "cancelled", "skipped", "neutral", or
    no conclusion (still in progress) are excluded from both the numerator
    and the denominator.

    Args:
        runs: List of workflow run dicts, each with "name" and "conclusion"

    Returns:
        Dictionary with:
        - Job Failure Rate (%): overall failure rate (float or None if no
          countable runs)
        - Job Failure Rate - <workflow name> (%): failure rate per workflow
        - Total Workflow Runs (last 30 days): count of countable runs
    """
    counted_runs = [
        run
        for run in runs
        if run.get("conclusion") in FAILURE_CONCLUSIONS
        or run.get("conclusion") in SUCCESS_CONCLUSIONS
    ]

    result: Dict[str, object] = {
        TOTAL_WORKFLOW_RUNS_KEY: len(counted_runs),
    }

    if not counted_runs:
        result[JOB_FAILURE_RATE_KEY] = None
        return result

    total_failures = sum(
        1 for run in counted_runs if run["conclusion"] in FAILURE_CONCLUSIONS
    )
    result[JOB_FAILURE_RATE_KEY] = round((total_failures / len(counted_runs)) * 100, 2)

    runs_by_workflow: Dict[str, List[Dict]] = {}
    for run in counted_runs:
        workflow_name = run.get("name") or "Unknown"
        runs_by_workflow.setdefault(workflow_name, []).append(run)

    for workflow_name, workflow_runs in runs_by_workflow.items():
        failures = sum(
            1 for run in workflow_runs if run["conclusion"] in FAILURE_CONCLUSIONS
        )
        result[_job_failure_rate_key(workflow_name)] = round(
            (failures / len(workflow_runs)) * 100, 2
        )

    return result


def get_job_failure_metrics(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Get Job Failure Rate metrics for a repository.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with Job Failure Rate metrics; see audit_job_failure_rate.
    """
    logger.info(f"Computing job failure rate metrics for {owner}/{repository}")

    now_utc = datetime.now(timezone.utc)
    runs = client.get_workflow_runs(owner, repository, since_days=LAST_N_DAYS)

    recent_runs: List[Dict] = []
    for run in runs:
        created_at_str = run.get("created_at")
        if created_at_str is None:
            continue
        try:
            created_at = datetime.fromisoformat(
                str(created_at_str).replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            continue
        if (now_utc - created_at).days > LAST_N_DAYS:
            continue
        recent_runs.append(run)

    return audit_job_failure_rate(recent_runs)
