# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from unittest.mock import patch

from edfi_repo_auditor.auditor import run_audit
from edfi_repo_auditor.config import Configuration

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
OTHER_REPO = "Ed-Fi-Admin"


def _config(repositories: list) -> Configuration:
    return Configuration(
        organization=OWNER,
        personal_access_token=ACCESS_TOKEN,
        repositories=repositories,
        log_level="INFO",
        save_results=False,
        file_name="",
    )


def describe_when_running_a_full_audit() -> None:
    def describe_given_all_audits_succeed() -> None:
        @patch("edfi_repo_auditor.auditor.output_to_github_actions")
        @patch("edfi_repo_auditor.auditor.get_ossf_score")
        @patch("edfi_repo_auditor.auditor.get_job_failure_metrics")
        @patch("edfi_repo_auditor.auditor.get_pr_metrics")
        @patch("edfi_repo_auditor.auditor.review_files")
        @patch("edfi_repo_auditor.auditor.audit_actions")
        @patch("edfi_repo_auditor.auditor.get_repo_information")
        @patch("edfi_repo_auditor.auditor.GitHubClient")
        def it_merges_job_failure_metrics_into_the_results_without_collisions(
            mock_client_class,
            mock_repo_info,
            mock_actions,
            mock_files,
            mock_pr_metrics,
            mock_job_metrics,
            mock_ossf,
            mock_output,
        ) -> None:
            mock_repo_info.return_value = {"Repo Check": "pass"}
            mock_actions.return_value = {"Actions Check": "pass"}
            mock_files.return_value = {"Files Check": "pass"}
            mock_pr_metrics.return_value = {"Avg PR Duration (days)": 1.0}
            mock_job_metrics.return_value = {
                "Job Failure Rate (%)": 25.0,
                "Total Workflow Runs (last 30 days)": 4,
            }
            mock_ossf.return_value = {"OSSF Score": 8.0}

            run_audit(_config([REPO]))

            results = mock_output.call_args[0][1]
            assert results["Job Failure Rate (%)"] == 25.0
            assert results["Total Workflow Runs (last 30 days)"] == 4
            assert results["Repo Check"] == "pass"
            assert results["Actions Check"] == "pass"
            assert results["Files Check"] == "pass"
            assert results["Avg PR Duration (days)"] == 1.0
            assert results["OSSF Score"] == 8.0

    def describe_given_job_failure_metrics_raises_a_runtime_error_for_one_repository() -> (  # noqa: E501
        None
    ):
        @patch("edfi_repo_auditor.auditor.output_to_github_actions")
        @patch("edfi_repo_auditor.auditor.get_ossf_score")
        @patch("edfi_repo_auditor.auditor.get_job_failure_metrics")
        @patch("edfi_repo_auditor.auditor.get_pr_metrics")
        @patch("edfi_repo_auditor.auditor.review_files")
        @patch("edfi_repo_auditor.auditor.audit_actions")
        @patch("edfi_repo_auditor.auditor.get_repo_information")
        @patch("edfi_repo_auditor.auditor.GitHubClient")
        def it_still_produces_results_for_the_other_repository(
            mock_client_class,
            mock_repo_info,
            mock_actions,
            mock_files,
            mock_pr_metrics,
            mock_job_metrics,
            mock_ossf,
            mock_output,
        ) -> None:
            mock_repo_info.return_value = {}
            mock_actions.return_value = {}
            mock_files.return_value = {}
            mock_pr_metrics.return_value = {}
            mock_job_metrics.side_effect = [
                RuntimeError("boom"),
                {
                    "Job Failure Rate (%)": 0.0,
                    "Total Workflow Runs (last 30 days)": 2,
                },
            ]
            mock_ossf.return_value = {}

            run_audit(_config([REPO, OTHER_REPO]))

            assert mock_output.call_count == 2

            first_results = mock_output.call_args_list[0][0][1]
            second_results = mock_output.call_args_list[1][0][1]

            assert "Job Failure Rate (%)" not in first_results
            assert second_results["Job Failure Rate (%)"] == 0.0
            assert second_results["Total Workflow Runs (last 30 days)"] == 2
