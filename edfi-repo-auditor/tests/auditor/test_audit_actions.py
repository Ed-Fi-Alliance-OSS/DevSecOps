# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import MagicMock
from edfi_repo_auditor.auditor import audit_actions
from edfi_repo_auditor.checklist import CHECKLIST
from edfi_repo_auditor.github_client import GitHubClient

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
CLIENT = GitHubClient(ACCESS_TOKEN)


def describe_when_auditing_actions() -> None:
    def describe_given_reviewing_codeql() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {
                "total_count": 1,
                "workflows": [{
                    "path": "test-action.yml"
                }]
            }

        def it_returns_false_when_no_codeql(actions: dict) -> None:
            file_content = """
                - name: Analyze
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.CODEQL] is False

        def it_returns_true_when_has_codeql(actions: dict) -> None:
            file_content = """
                - name: Analyze
                  uses: github/codeql-action/analyze
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.CODEQL] is True

    def describe_given_reviewing_allowed_list() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {
                "total_count": 1,
                "workflows": [{
                    "path": "test-action.yml"
                }]
            }

        def it_returns_false_when_uses_any_action(actions: dict) -> None:
            file_content = """
                - name: Scan
                  uses: fake-action/allowed-list
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.APPROVED_ACTIONS] is False

        def it_returns_true_when_uses_approved_actions(actions: dict) -> None:
            file_content = """
                - name: Scan
                  uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.APPROVED_ACTIONS] is True

    def describe_given_reviewing_test_reporter() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {
                "total_count": 1,
                "workflows": [{
                    "path": "test-action.yml"
                }]
            }

        def it_returns_false_when_no_test_reporter(actions: dict) -> None:
            file_content = """
                - name: Integration Tests
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.TEST_REPORTER] is False

        def it_returns_true_when_has_test_reporter(actions: dict) -> None:
            file_content = """
                - name: Integration Tests Report
                uses: dorny/test-reporter
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.TEST_REPORTER] is True

    def describe_given_reviewing_unit_tests() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {
                "total_count": 1,
                "workflows": [{
                    "path": "test-action.yml"
                }]
            }

        def it_returns_true_when_has_unit_tests(actions: dict) -> None:
            file_content = """
                - name: Unit Tests with coverage
            """

            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.UNIT_TESTS] is True

        def it_returns_false_when_no_unit_tests(actions: dict) -> None:
            file_content = """
                - name: Integration Tests
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.UNIT_TESTS] is False

    def describe_given_reviewing_linter() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {
                "total_count": 1,
                "workflows": [{
                    "path": "test-action.yml"
                }]
            }

        def it_returns_true_when_has_linter(actions: dict) -> None:
            file_content = """
                - name: Linter
            """

            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.LINTER] is True

        def it_returns_false_when_no_linter(actions: dict) -> None:
            file_content = """
                - name: Review and correct
            """
            CLIENT.get_actions = MagicMock(return_value=actions)
            CLIENT.get_file_content = MagicMock(return_value=file_content)
            results = audit_actions(CLIENT, OWNER, REPO)
            assert results[CHECKLIST.LINTER] is False
