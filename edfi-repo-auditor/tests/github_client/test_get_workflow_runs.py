# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, API_URL

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
RUNS_URL = f"{API_URL}/repos/{OWNER}/{REPO}/actions/runs"


def _cutoff(since_days: int = 30) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime(
        "%Y-%m-%d"
    )


def describe_when_getting_workflow_runs() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_workflow_runs("", REPO)

    def describe_given_blank_repository() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, "")

    def describe_given_an_out_of_range_per_page() -> None:
        def it_raises_a_ValueError_when_zero() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO, per_page=0)

        def it_raises_a_ValueError_when_negative() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO, per_page=-1)

        def it_raises_a_ValueError_when_over_100() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO, per_page=101)

    def describe_given_valid_information() -> None:
        def describe_given_single_page_of_runs() -> None:
            RUNS_RESULT = """
{
    "workflow_runs": [
        {
            "name": "CI",
            "conclusion": "success",
            "created_at": "2024-01-01T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        },
        {
            "name": "CodeQL",
            "conclusion": "failure",
            "created_at": "2024-01-02T10:00:00Z",
            "path": ".github/workflows/codeql.yml"
        }
    ]
}
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text=RUNS_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO)

            def it_returns_two_runs(results: list) -> None:
                assert len(results) == 2

            def it_returns_correct_first_run_name(results: list) -> None:
                assert results[0]["name"] == "CI"

            def it_returns_correct_conclusion(results: list) -> None:
                assert results[0]["conclusion"] == "success"
                assert results[1]["conclusion"] == "failure"

        def describe_given_multiple_pages_of_runs() -> None:
            PAGE1_RESULT = """
{
    "workflow_runs": [
        {
            "name": "CI",
            "conclusion": "success",
            "created_at": "2024-01-01T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        },
        {
            "name": "CI",
            "conclusion": "failure",
            "created_at": "2024-01-02T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        }
    ]
}
""".strip()

            PAGE2_RESULT = """
{
    "workflow_runs": [
        {
            "name": "CI",
            "conclusion": "success",
            "created_at": "2024-01-03T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        }
    ]
}
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=2&page=1",
                        status_code=HTTPStatus.OK,
                        text=PAGE1_RESULT,
                    )
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=2&page=2",
                        status_code=HTTPStatus.OK,
                        text=PAGE2_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_workflow_runs(
                        OWNER, REPO, per_page=2
                    )

            def it_returns_all_three_runs(results: list) -> None:
                assert len(results) == 3

        def describe_given_a_final_page_exactly_equal_to_per_page() -> None:
            FULL_PAGE_RESULT = """
{
    "workflow_runs": [
        {
            "name": "CI",
            "conclusion": "success",
            "created_at": "2024-01-01T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        },
        {
            "name": "CI",
            "conclusion": "failure",
            "created_at": "2024-01-02T10:00:00Z",
            "path": ".github/workflows/ci.yml"
        }
    ]
}
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=2&page=1",
                        status_code=HTTPStatus.OK,
                        text=FULL_PAGE_RESULT,
                    )
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=2&page=2",
                        status_code=HTTPStatus.OK,
                        text='{"workflow_runs": []}',
                    )
                    return GitHubClient(ACCESS_TOKEN).get_workflow_runs(
                        OWNER, REPO, per_page=2
                    )

            def it_fetches_the_trailing_empty_page_and_returns_two_runs(
                results: list,
            ) -> None:
                assert len(results) == 2

        def describe_given_empty_result() -> None:
            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text='{"workflow_runs": []}',
                    )
                    return GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO)

            def it_returns_empty_list(results: list) -> None:
                assert results == []

        def describe_given_internal_server_error() -> None:
            def it_raises_a_RuntimeError() -> None:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{RUNS_URL}?created=>={_cutoff()}&per_page=100&page=1",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        text="{}",
                    )
                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_workflow_runs(OWNER, REPO)
