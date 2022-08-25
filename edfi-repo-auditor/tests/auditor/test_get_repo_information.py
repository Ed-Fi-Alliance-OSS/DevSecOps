# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch, MagicMock
from edfi_repo_auditor.auditor import get_repo_information
from edfi_repo_auditor.checklist import CHECKLIST
from edfi_repo_auditor.github_client import GitHubClient

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
CLIENT = GitHubClient(ACCESS_TOKEN)


def describe_when_getting_repo_info() -> None:
    def describe_branch_protection() -> None:
        def describe_given_there_are_no_protection_rules() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {
                    "nodes": []
                },
                "branchProtectionRules": {
                    "nodes": []
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {
                    "totalCount": 0
                },
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": {}
            }

            @pytest.fixture
            @patch('edfi_repo_auditor.auditor.audit_alerts')
            def results(mock_audit_alerts) -> dict:
                CLIENT.get_repository_information = MagicMock(return_value=RESPONSE)
                mock_audit_alerts.return_value = {}
                return get_repo_information(CLIENT, OWNER, REPO)

            def it_returns_no_rules(results: dict) -> None:
                assert results[CHECKLIST.SIGNED_COMMITS] is False
                assert results[CHECKLIST.CODE_REVIEW] is False
                assert results[CHECKLIST.REQUIRES_PR] is False
                assert results[CHECKLIST.ADMIN_PR] is False

        def describe_given_there_are_protection_rules() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {
                    "nodes": []
                },
                "branchProtectionRules": {
                    "nodes": [{
                        "pattern": "main",
                        "requiresCommitSignatures": True,
                        "isAdminEnforced": True,
                        "requiresApprovingReviews": True
                    }]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {
                    "totalCount": 0
                },
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": {}
            }

            @pytest.fixture
            @patch('edfi_repo_auditor.auditor.audit_alerts')
            def results(mock_audit_alerts) -> dict:
                CLIENT.get_repository_information = MagicMock(return_value=RESPONSE)
                mock_audit_alerts.return_value = {}
                return get_repo_information(CLIENT, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert results[CHECKLIST.SIGNED_COMMITS] is True
                assert results[CHECKLIST.CODE_REVIEW] is True
                assert results[CHECKLIST.REQUIRES_PR] is True
                assert results[CHECKLIST.ADMIN_PR] is False

        def describe_given_there_are_protection_rules_for_other_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {
                    "nodes": []
                },
                "branchProtectionRules": {
                    "nodes": [{
                        "pattern": "feature",
                        "requiresCommitSignatures": True,
                        "isAdminEnforced": True,
                        "requiresApprovingReviews": True
                    }]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {
                    "totalCount": 0
                },
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": {}
            }

            @pytest.fixture
            @patch('edfi_repo_auditor.auditor.audit_alerts')
            def results(mock_audit_alerts) -> dict:
                CLIENT.get_repository_information = MagicMock(return_value=RESPONSE)
                mock_audit_alerts.return_value = {}
                return get_repo_information(CLIENT, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert results[CHECKLIST.SIGNED_COMMITS] is False
                assert results[CHECKLIST.CODE_REVIEW] is False
                assert results[CHECKLIST.REQUIRES_PR] is False
                assert results[CHECKLIST.ADMIN_PR] is False
