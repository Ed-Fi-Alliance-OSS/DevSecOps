# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import get_repo_information
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"

OK = CHECKLIST_DEFAULT_SUCCESS_MESSAGE


def describe_when_getting_repo_info() -> None:
    def describe_rulesets() -> None:
        def describe_given_there_are_no_rulesets() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {"nodes": []},
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {"totalCount": 0},
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": None,
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_no_rules(results: dict) -> None:
                assert results == {
                    CHECKLIST.WIKI["description"]: OK,
                    CHECKLIST.ISSUES["description"]: CHECKLIST.ISSUES["fail"],
                    CHECKLIST.PROJECTS["description"]: OK,
                    CHECKLIST.DELETES_HEAD["description"]: CHECKLIST.DELETES_HEAD[
                        "fail"
                    ],
                    CHECKLIST.USES_SQUASH["description"]: OK,
                    CHECKLIST.LICENSE_INFORMATION[
                        "description"
                    ]: CHECKLIST.LICENSE_INFORMATION["fail"],
                    CHECKLIST.REQUIRES_PULL_REQUEST[
                        "description"
                    ]: CHECKLIST.REQUIRES_PULL_REQUEST["fail"],
                    CHECKLIST.ADMIN_CANNOT_BYPASS[
                        "description"
                    ]: CHECKLIST.ADMIN_CANNOT_BYPASS["fail"],
                    CHECKLIST.RESTRICTS_CREATION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_CREATION["fail"],
                    CHECKLIST.RESTRICTS_DELETION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_DELETION["fail"],
                    CHECKLIST.REQUIRES_LINEAR_HISTORY[
                        "description"
                    ]: CHECKLIST.REQUIRES_LINEAR_HISTORY["fail"],
                }

        def describe_given_there_are_active_rulesets_for_main_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {
                    "nodes": [
                        {
                            "enforcement": "ACTIVE",
                            "conditions": {"refName": {"include": ["main"]}},
                            "rules": {"nodes": [{"type": "REQUIRED_SIGNATURES"}]},
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": True,
                "hasProjectsEnabled": False,
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": None,
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert results == {
                    CHECKLIST.WIKI["description"]: OK,
                    CHECKLIST.ISSUES["description"]: OK,
                    CHECKLIST.PROJECTS["description"]: OK,
                    CHECKLIST.DELETES_HEAD["description"]: CHECKLIST.DELETES_HEAD[
                        "fail"
                    ],
                    CHECKLIST.USES_SQUASH["description"]: OK,
                    CHECKLIST.LICENSE_INFORMATION[
                        "description"
                    ]: CHECKLIST.LICENSE_INFORMATION["fail"],
                    CHECKLIST.REQUIRES_PULL_REQUEST[
                        "description"
                    ]: CHECKLIST.REQUIRES_PULL_REQUEST["fail"],
                    CHECKLIST.ADMIN_CANNOT_BYPASS["description"]: OK,
                    CHECKLIST.RESTRICTS_CREATION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_CREATION["fail"],
                    CHECKLIST.RESTRICTS_DELETION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_DELETION["fail"],
                    CHECKLIST.REQUIRES_LINEAR_HISTORY[
                        "description"
                    ]: CHECKLIST.REQUIRES_LINEAR_HISTORY["fail"],
                }

        def describe_given_there_are_active_rulesets_for_other_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {
                    "nodes": [
                        {
                            "enforcement": "ACTIVE",
                            "conditions": {"refName": {"include": ["feature"]}},
                            "rules": {"nodes": [{"type": "REQUIRED_SIGNATURES"}]},
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": True,
                "hasProjectsEnabled": False,
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": {"key": "test-key"},
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert results == {
                    CHECKLIST.WIKI["description"]: OK,
                    CHECKLIST.ISSUES["description"]: OK,
                    CHECKLIST.PROJECTS["description"]: OK,
                    CHECKLIST.DELETES_HEAD["description"]: CHECKLIST.DELETES_HEAD[
                        "fail"
                    ],
                    CHECKLIST.USES_SQUASH["description"]: OK,
                    CHECKLIST.LICENSE_INFORMATION["description"]: OK,
                    CHECKLIST.REQUIRES_PULL_REQUEST[
                        "description"
                    ]: CHECKLIST.REQUIRES_PULL_REQUEST["fail"],
                    CHECKLIST.ADMIN_CANNOT_BYPASS[
                        "description"
                    ]: CHECKLIST.ADMIN_CANNOT_BYPASS["fail"],
                    CHECKLIST.RESTRICTS_CREATION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_CREATION["fail"],
                    CHECKLIST.RESTRICTS_DELETION[
                        "description"
                    ]: CHECKLIST.RESTRICTS_DELETION["fail"],
                    CHECKLIST.REQUIRES_LINEAR_HISTORY[
                        "description"
                    ]: CHECKLIST.REQUIRES_LINEAR_HISTORY["fail"],
                }

        def describe_given_there_are_active_rulesets_with_all_required_branch_rules() -> (
            None
        ):
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {
                    "nodes": [
                        {
                            "bypassActors": {"edges": []},
                            "conditions": {
                                "refName": {
                                    "include": ["~DEFAULT_BRANCH", "refs/heads/patch-*"]
                                }
                            },
                            "enforcement": "ACTIVE",
                            "name": "main*",
                            "rules": {
                                "nodes": [
                                    {"type": "DELETION"},
                                    {"type": "NON_FAST_FORWARD"},
                                    {"type": "CREATION"},
                                    {"type": "REQUIRED_LINEAR_HISTORY"},
                                    {"type": "PULL_REQUEST"},
                                    {"type": "REQUIRED_STATUS_CHECKS"},
                                ]
                            },
                            "target": "BRANCH",
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": True,
                "hasProjectsEnabled": False,
                "deleteBranchOnMerge": True,
                "squashMergeAllowed": True,
                "licenseInfo": {"key": "apache-2.0"},
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_passes_all_branch_rule_checks(results: dict) -> None:
                assert results == {
                    CHECKLIST.WIKI["description"]: OK,
                    CHECKLIST.ISSUES["description"]: OK,
                    CHECKLIST.PROJECTS["description"]: OK,
                    CHECKLIST.DELETES_HEAD["description"]: OK,
                    CHECKLIST.USES_SQUASH["description"]: OK,
                    CHECKLIST.LICENSE_INFORMATION["description"]: OK,
                    CHECKLIST.REQUIRES_PULL_REQUEST["description"]: OK,
                    CHECKLIST.ADMIN_CANNOT_BYPASS["description"]: OK,
                    CHECKLIST.RESTRICTS_CREATION["description"]: OK,
                    CHECKLIST.RESTRICTS_DELETION["description"]: OK,
                    CHECKLIST.REQUIRES_LINEAR_HISTORY["description"]: OK,
                }
