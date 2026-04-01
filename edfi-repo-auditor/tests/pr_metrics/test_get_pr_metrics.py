# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from unittest.mock import MagicMock

from edfi_repo_auditor.pr_metrics import (
    AVG_LEAD_TIME_DAYS_KEY,
    AVG_PR_DURATION_DAYS_KEY,
    AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY,
    MERGED_PRS_LAST_30_DAYS_KEY,
    get_pr_metrics,
)

# A merged_at within the last 30 days
RECENT_MERGED_AT = "2026-03-25T10:00:00Z"
CREATED_AT = "2026-03-24T10:00:00Z"
CLOSED_AT = "2026-03-25T10:00:00Z"

# A merged_at older than 30 days
OLD_MERGED_AT = "2025-01-01T10:00:00Z"


def _make_pr(
    number: int,
    merged_at: str,
    created_at: str = CREATED_AT,
    closed_at: str = CLOSED_AT,
    reviews: list = None,  # type: ignore[assignment]
) -> dict:
    return {
        "number": number,
        "created_at": created_at,
        "closed_at": closed_at,
        "merged_at": merged_at,
        "reviews": reviews if reviews is not None else [],
    }


def describe_get_pr_metrics() -> None:
    def describe_given_no_prs() -> None:
        def it_returns_zero_merged_and_none_averages() -> None:
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = []

            result = get_pr_metrics(client, "owner", "repo")

            assert result[MERGED_PRS_LAST_30_DAYS_KEY] == 0
            assert result[AVG_PR_DURATION_DAYS_KEY] is None
            assert result[AVG_LEAD_TIME_DAYS_KEY] is None

    def describe_given_prs_older_than_30_days() -> None:
        def it_excludes_them_from_metrics() -> None:
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = [
                _make_pr(1, OLD_MERGED_AT),
            ]

            result = get_pr_metrics(client, "owner", "repo")

            assert result[MERGED_PRS_LAST_30_DAYS_KEY] == 0

    def describe_given_unmerged_pr() -> None:
        def it_excludes_it_from_metrics() -> None:
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = [
                _make_pr(1, None),  # type: ignore[arg-type]
            ]

            result = get_pr_metrics(client, "owner", "repo")

            assert result[MERGED_PRS_LAST_30_DAYS_KEY] == 0

    def describe_given_recent_merged_pr() -> None:
        def it_includes_pr() -> None:
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = [
                _make_pr(42, RECENT_MERGED_AT)
            ]

            result = get_pr_metrics(client, "owner", "repo")

            assert result[MERGED_PRS_LAST_30_DAYS_KEY] == 1
            client.get_merged_prs_with_reviews.assert_called_once_with("owner", "repo")

    def describe_review_normalization() -> None:
        def it_injects_pr_created_at_into_reviews_missing_the_field() -> None:
            """
            get_pr_metrics injects pr.created_at into each review that lacks
            its own created_at. This ensures audit_pr_review_cycle can compute
            time-to-first-approval even when reviews omit the field.
            """
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = [
                _make_pr(
                    1,
                    RECENT_MERGED_AT,
                    created_at=CREATED_AT,
                    reviews=[
                        {
                            "user": "alice",
                            "state": "APPROVED",
                            "submitted_at": "2026-03-24T12:00:00Z",
                        }
                    ],
                )
            ]

            result = get_pr_metrics(client, "owner", "repo")

            # created_at injected from PR (10:00); submitted_at is 12:00 → 2 hours
            assert result[AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY] == 2.0

        def it_does_not_overwrite_created_at_already_present_on_review() -> None:
            client = MagicMock()
            client.get_merged_prs_with_reviews.return_value = [
                _make_pr(
                    1,
                    RECENT_MERGED_AT,
                    created_at=CREATED_AT,
                    reviews=[
                        {
                            "user": "bob",
                            "state": "APPROVED",
                            "submitted_at": "2026-03-24T13:00:00Z",
                            "created_at": "2026-03-24T11:00:00Z",  # 2 hours before submittal
                        }
                    ],
                )
            ]

            result = get_pr_metrics(client, "owner", "repo")

            # 13:00 - 11:00 = 2 hours (not 13:00 - 10:00 = 3 hours)
            assert result[AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY] == 2.0
