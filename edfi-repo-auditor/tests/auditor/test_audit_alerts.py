# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import datetime as real_datetime, timedelta, timezone
from typing import List
import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import ALERTS_WEEKS_SINCE_CREATED, audit_alerts
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_auditing_alerts() -> None:
    def describe_dependabot_alerts() -> None:
        def describe_given_is_not_enabled() -> None:
            ALERTS: List[dict] = []

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.has_dependabot_enabled.return_value = False
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_dependabot_enabled(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ENABLED["description"]]
                    == CHECKLIST.DEPENDABOT_ENABLED["fail"]
                )

            def it_returns_no_alerts(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_is_enabled() -> None:
            ALERTS: List[dict] = []

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.has_dependabot_enabled.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_dependabot_enabled(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ENABLED["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_there_are_no_alerts() -> None:
            ALERTS: List[dict] = []

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.has_dependabot_enabled.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_no_alerts(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ENABLED["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_there_are_alerts_not_old() -> None:
            ALERTS = [
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED - 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "CRITICAL"},
                    },
                }
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.get_repository_information.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_no_alerts(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_there_are_old_alerts_not_severe() -> None:
            ALERTS = [
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED + 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "WARNING"},
                    },
                },
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED - 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "HIGH"},
                    },
                },
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.get_repository_information.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_no_alerts(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_there_are_critical_risk_alerts_not_old() -> None:
            ALERTS = [
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED - 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "CRITICAL"},
                    },
                }
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.has_dependabot_enabled.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_no_alerts(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )

        def describe_given_there_are_old_critical_risk_alerts() -> None:
            ALERTS = [
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED + 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "CRITICAL"},
                    },
                }
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.get_repository_information.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_warning(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST.DEPENDABOT_ALERTS["fail"]
                )

        def describe_given_there_are_old_high_risk_alerts() -> None:
            ALERTS = [
                {
                    "createdAt": (
                        real_datetime.now(timezone.utc)
                        - timedelta((ALERTS_WEEKS_SINCE_CREATED + 1) * 7)
                    ).isoformat(),
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "HIGH"},
                    },
                }
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.get_repository_information.return_value = True
                return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_warning(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST.DEPENDABOT_ALERTS["fail"]
                )

        # GitHub returns Z-suffix timestamps without microseconds, e.g. "2026-04-01T12:00:00Z".
        # datetime.now(timezone.utc).isoformat() produces "+00:00" with microseconds, e.g.
        # "2026-04-01T12:00:00.500000+00:00". Lexicographically, "Z" (ASCII 90) > "." (ASCII 46),
        # so string comparison treats a Z-format timestamp at the cutoff second as newer than the
        # cutoff, silently dropping alerts that should be flagged.
        def describe_given_old_critical_alert_with_Z_format_at_cutoff_second_boundary() -> (
            None
        ):
            FIXED_NOW = real_datetime(
                2026, 4, 22, 12, 0, 0, 500000, tzinfo=timezone.utc
            )
            CUTOFF = FIXED_NOW - timedelta(ALERTS_WEEKS_SINCE_CREATED * 7)
            # Alert created at the cutoff second without microseconds and with Z suffix —
            # 0.5 s before the actual cutoff, so it should be flagged.
            ALERT_TIME = CUTOFF.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

            ALERTS = [
                {
                    "createdAt": ALERT_TIME,
                    "securityVulnerability": {
                        "package": {"name": "minimist"},
                        "advisory": {"severity": "CRITICAL"},
                    },
                }
            ]

            @pytest.fixture
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_client) -> dict:
                mock_client.has_dependabot_enabled.return_value = True
                with patch("edfi_repo_auditor.auditor.datetime") as mock_dt:
                    mock_dt.now.return_value = FIXED_NOW
                    mock_dt.fromisoformat.side_effect = real_datetime.fromisoformat
                    return audit_alerts(mock_client, OWNER, REPO, ALERTS)

            def it_returns_warning(results: dict) -> None:
                assert (
                    results[CHECKLIST.DEPENDABOT_ALERTS["description"]]
                    == CHECKLIST.DEPENDABOT_ALERTS["fail"]
                )
