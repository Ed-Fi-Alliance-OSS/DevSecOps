# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, API_URL

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
PR_NUMBER = 42
REVIEWS_URL = f"{API_URL}/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/reviews"


def describe_when_getting_pull_request_reviews() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_pull_request_reviews("", REPO, PR_NUMBER)

    def describe_given_blank_repository() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_pull_request_reviews(OWNER, "", PR_NUMBER)

    def describe_given_valid_information() -> None:
        def describe_given_single_page_of_reviews() -> None:
            REVIEWS_RESULT = """
[
    {"user": {"login": "alice"}, "state": "APPROVED", "submitted_at": "2024-01-02T10:00:00Z"},
    {"user": {"login": "bob"},   "state": "COMMENTED", "submitted_at": "2024-01-02T11:00:00Z"}
]
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{REVIEWS_URL}?per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text=REVIEWS_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_request_reviews(
                        OWNER, REPO, PR_NUMBER
                    )

            def it_returns_two_reviews(results: list) -> None:
                assert len(results) == 2

            def it_returns_user_login(results: list) -> None:
                assert results[0]["user"] == "alice"

            def it_returns_state(results: list) -> None:
                assert results[0]["state"] == "APPROVED"

            def it_returns_submitted_at(results: list) -> None:
                assert results[0]["submitted_at"] == "2024-01-02T10:00:00Z"

        def describe_given_multiple_pages_of_reviews() -> None:
            PAGE1_RESULT = """
[
    {"user": {"login": "alice"}, "state": "COMMENTED", "submitted_at": "2024-01-01T09:00:00Z"},
    {"user": {"login": "bob"},   "state": "APPROVED",  "submitted_at": "2024-01-01T10:00:00Z"}
]
""".strip()

            PAGE2_RESULT = """
[
    {"user": {"login": "carol"}, "state": "CHANGES_REQUESTED", "submitted_at": "2024-01-01T11:00:00Z"}
]
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{REVIEWS_URL}?per_page=2&page=1",
                        status_code=HTTPStatus.OK,
                        text=PAGE1_RESULT,
                    )
                    m.get(
                        f"{REVIEWS_URL}?per_page=2&page=2",
                        status_code=HTTPStatus.OK,
                        text=PAGE2_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_request_reviews(
                        OWNER, REPO, PR_NUMBER, per_page=2
                    )

            def it_returns_all_three_reviews(results: list) -> None:
                assert len(results) == 3

            def it_returns_reviews_from_first_page(results: list) -> None:
                assert results[0]["user"] == "alice"
                assert results[1]["user"] == "bob"

            def it_returns_review_from_second_page(results: list) -> None:
                assert results[2]["user"] == "carol"

        def describe_given_empty_result() -> None:
            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{REVIEWS_URL}?per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text="[]",
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_request_reviews(
                        OWNER, REPO, PR_NUMBER
                    )

            def it_returns_empty_list(results: list) -> None:
                assert results == []

        def describe_given_internal_server_error() -> None:
            def it_raises_a_RuntimeError() -> None:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{REVIEWS_URL}?per_page=100&page=1",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        text="{}",
                    )
                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_pull_request_reviews(
                            OWNER, REPO, PR_NUMBER
                        )
