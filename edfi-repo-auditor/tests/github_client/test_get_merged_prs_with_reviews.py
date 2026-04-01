# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
import pytest
import requests_mock as requests_mock_module

from edfi_repo_auditor.github_client import GitHubClient, GRAPHQL_ENDPOINT

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def _graphql_response(nodes, has_next_page=False, end_cursor=None):
    return {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": nodes,
                    "pageInfo": {
                        "hasNextPage": has_next_page,
                        "endCursor": end_cursor,
                    },
                }
            }
        }
    }


def _make_node(
    number,
    created_at="2026-03-20T10:00:00Z",
    merged_at="2026-03-21T10:00:00Z",
    closed_at="2026-03-21T10:00:00Z",
    author_login="alice",
    reviews=None,
):
    return {
        "number": number,
        "createdAt": created_at,
        "mergedAt": merged_at,
        "closedAt": closed_at,
        "author": {"login": author_login} if author_login is not None else None,
        "additions": 10,
        "deletions": 5,
        "changedFiles": 2,
        "reviews": {
            "pageInfo": {"hasNextPage": False},
            "nodes": reviews or [],
        },
    }


def describe_get_merged_prs_with_reviews() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews("", REPO)

    def describe_given_blank_repository() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(OWNER, "")

    def describe_given_no_prs() -> None:
        @pytest.fixture
        def results() -> list:
            with requests_mock_module.Mocker() as m:
                m.post(GRAPHQL_ENDPOINT, json=_graphql_response([]))
                return GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(
                    OWNER, REPO
                )

        def it_returns_empty_list(results: list) -> None:
            assert results == []

    def describe_given_single_page_of_prs() -> None:
        REVIEW_NODE = {
            "author": {"login": "bob"},
            "state": "APPROVED",
            "submittedAt": "2026-03-21T09:00:00Z",
        }

        @pytest.fixture
        def results() -> list:
            with requests_mock_module.Mocker() as m:
                m.post(
                    GRAPHQL_ENDPOINT,
                    json=_graphql_response([_make_node(42, reviews=[REVIEW_NODE])]),
                )
                return GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(
                    OWNER, REPO
                )

        def it_returns_one_pr(results: list) -> None:
            assert len(results) == 1

        def it_maps_pr_number(results: list) -> None:
            assert results[0]["number"] == 42

        def it_maps_created_at(results: list) -> None:
            assert results[0]["created_at"] == "2026-03-20T10:00:00Z"

        def it_maps_merged_at(results: list) -> None:
            assert results[0]["merged_at"] == "2026-03-21T10:00:00Z"

        def it_maps_pr_user(results: list) -> None:
            assert results[0]["user"] == "alice"

        def it_returns_one_review(results: list) -> None:
            assert len(results[0]["reviews"]) == 1

        def it_maps_review_user(results: list) -> None:
            assert results[0]["reviews"][0]["user"] == "bob"

        def it_maps_review_state(results: list) -> None:
            assert results[0]["reviews"][0]["state"] == "APPROVED"

        def it_maps_review_submitted_at(results: list) -> None:
            assert results[0]["reviews"][0]["submitted_at"] == "2026-03-21T09:00:00Z"

    def describe_given_multiple_pages() -> None:
        PAGE1 = _graphql_response(
            [_make_node(2, created_at="2026-03-25T10:00:00Z")],
            has_next_page=True,
            end_cursor="cursor_abc",
        )
        PAGE2 = _graphql_response(
            [_make_node(1, created_at="2026-03-20T10:00:00Z")],
            has_next_page=False,
        )

        @pytest.fixture
        def results() -> list:
            with requests_mock_module.Mocker() as m:
                m.register_uri(
                    "POST",
                    GRAPHQL_ENDPOINT,
                    [
                        {"json": PAGE1, "status_code": HTTPStatus.OK},
                        {"json": PAGE2, "status_code": HTTPStatus.OK},
                    ],
                )
                return GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(
                    OWNER, REPO
                )

        def it_returns_prs_from_both_pages(results: list) -> None:
            assert len(results) == 2

        def it_includes_first_page_pr(results: list) -> None:
            assert results[0]["number"] == 2

        def it_includes_second_page_pr(results: list) -> None:
            assert results[1]["number"] == 1

    def describe_given_pr_with_null_author() -> None:
        @pytest.fixture
        def results() -> list:
            with requests_mock_module.Mocker() as m:
                m.post(
                    GRAPHQL_ENDPOINT,
                    json=_graphql_response([_make_node(5, author_login=None)]),
                )
                return GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(
                    OWNER, REPO
                )

        def it_returns_none_for_user(results: list) -> None:
            assert results[0]["user"] is None

    def describe_given_internal_server_error() -> None:
        def it_raises_a_RuntimeError() -> None:
            with requests_mock_module.Mocker() as m:
                m.post(
                    GRAPHQL_ENDPOINT,
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    json={},
                )
                with pytest.raises(RuntimeError):
                    GitHubClient(ACCESS_TOKEN).get_merged_prs_with_reviews(OWNER, REPO)
