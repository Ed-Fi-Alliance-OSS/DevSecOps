# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import MagicMock
from edfi_repo_auditor.auditor import audit_actions
from edfi_repo_auditor.github_client import GitHubClient

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
CLIENT = GitHubClient(ACCESS_TOKEN)


def describe_when_auditing_actions() -> None:
    def it_returns_true_when_has_unit_tests() -> None:
        ACTIONS = {
            "total_count": 1,
            "workflows": [{
                "path": "test-action.yml"
            }]
        }

        ACTION_CONTENT = """
            - name: Unit Tests with coverage
        """

        CLIENT.get_actions = MagicMock(return_value=ACTIONS)
        CLIENT.get_file_content = MagicMock(return_value=ACTION_CONTENT)
        results = audit_actions(CLIENT, OWNER, REPO)
        assert results["Has Unit Tests"] is True

    def it_returns_false_when_no_unit_tests() -> None:
        ACTIONS = {
            "total_count": 1,
            "workflows": [{
                "path": "test-action.yml"
            }]
        }

        ACTION_CONTENT = """
            - name: Integration Tests
        """

        CLIENT.get_actions = MagicMock(return_value=ACTIONS)
        CLIENT.get_file_content = MagicMock(return_value=ACTION_CONTENT)
        results = audit_actions(CLIENT, OWNER, REPO)
        assert results["Has Unit Tests"] is False
