# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_repo_auditor.pr_metrics import (
    TOP_REVIEWER_SHARE_PERCENT_KEY,
    TOTAL_REVIEWS_KEY,
    UNIQUE_REVIEWERS_KEY,
    audit_reviewer_load_balance,
)


def describe_audit_reviewer_load_balance() -> None:
    def describe_given_no_reviews() -> None:
        def it_returns_zero_counts_and_none_share() -> None:
            result = audit_reviewer_load_balance({})

            assert result[TOP_REVIEWER_SHARE_PERCENT_KEY] is None
            assert result[TOTAL_REVIEWS_KEY] == 0
            assert result[UNIQUE_REVIEWERS_KEY] == 0

    def describe_given_reviews_with_no_user_field() -> None:
        def it_returns_zero_counts_and_none_share() -> None:
            reviews = {1: [{"state": "APPROVED"}, {"state": "COMMENTED"}]}

            result = audit_reviewer_load_balance(reviews)

            assert result[TOP_REVIEWER_SHARE_PERCENT_KEY] is None
            assert result[TOTAL_REVIEWS_KEY] == 0
            assert result[UNIQUE_REVIEWERS_KEY] == 0

    def describe_given_single_reviewer() -> None:
        def it_returns_100_percent_share() -> None:
            reviews = {
                1: [{"user": "alice"}, {"user": "alice"}],
                2: [{"user": "alice"}],
            }

            result = audit_reviewer_load_balance(reviews)

            assert result[TOP_REVIEWER_SHARE_PERCENT_KEY] == 100.0
            assert result[TOTAL_REVIEWS_KEY] == 3
            assert result[UNIQUE_REVIEWERS_KEY] == 1

    def describe_given_multiple_reviewers() -> None:
        def it_computes_top_reviewer_share() -> None:
            # alice: 3 reviews, bob: 1 review → alice is 75%
            reviews = {
                1: [{"user": "alice"}, {"user": "bob"}],
                2: [{"user": "alice"}],
                3: [{"user": "alice"}],
            }

            result = audit_reviewer_load_balance(reviews)

            assert result[TOP_REVIEWER_SHARE_PERCENT_KEY] == 75.0
            assert result[TOTAL_REVIEWS_KEY] == 4
            assert result[UNIQUE_REVIEWERS_KEY] == 2

    def describe_given_reviews_with_mixed_none_users() -> None:
        def it_ignores_reviews_with_none_user() -> None:
            # None user entries must not be counted
            reviews = {
                1: [{"user": "alice"}, {"user": None}, {"user": "bob"}],
            }

            result = audit_reviewer_load_balance(reviews)

            assert result[TOTAL_REVIEWS_KEY] == 2
            assert result[UNIQUE_REVIEWERS_KEY] == 2
